from os import path

from XMLAPIUtils import XMLAPIFunction

from System.Web import HttpUtility


from datetime import datetime
from time import strptime



credentialsFile = open(path.join(path.dirname(__file__), "twitter-credentials.txt"), "r")
userName = credentialsFile.readline()
password = credentialsFile.readline()
credentialsFile.close()



def ParseTwitterDate(string):
    return datetime(*strptime(string, "%a %b %d %H:%M:%S +0000 %Y")[0:6])


class TwitterUser(object):
    def __init__(self):
        self.status = None


class TwitterStatus(object):
    pass


class GetTwitterUserData(XMLAPIFunction):

    def __init__(self, screenName):
        XMLAPIFunction.__init__(self, "http://twitter.com/users/show.xml")
        self.url += "?screen_name=" + HttpUtility.UrlEncode(screenName)
        self.inUser = False
        self.currentField = None
        self.user = None
        self.inStatus = False


    def getData(self):
        return XMLAPIFunction.getData(self, userName, password)


    def start(self, tagName):
        if tagName == "user":
            self.user = TwitterUser()
        elif tagName == "status" and self.user is not None:
            self.inStatus = True
            self.user.status = TwitterStatus()
        else:
            self.currentField = tagName


    def end(self, tagName):
        if tagName == "status":
            self.inStatus = False


    def text(self, text):
        if self.currentField == "created_at":
            value = ParseTwitterDate(text)
        else:
            value = text

        if self.inStatus:
            setattr(self.user.status, self.currentField, value)
        elif self.currentField and self.user:
            setattr(self.user, self.currentField, value)



class GetTwitterListMembers(XMLAPIFunction):

    def __init__(self, listOwner, listName):
        XMLAPIFunction.__init__(self, "http://api.twitter.com/1/%s/%s/members.xml" % (listOwner, listName))
        self.inUser = False
        self.members = []
        self.currentField = None
        self.currentMember = None
        self.nextCursor = "-1"
        self.inNextCursor = False


    def getData(self):
        while self.nextCursor != "" and self.nextCursor != "0":
            XMLAPIFunction.getData(self, userName, password, {"cursor" : self.nextCursor})
        return self


    def start(self, tagName):
        if tagName == "user":
            self.currentMember = TwitterUser()
            self.members.append(self.currentMember)
        elif tagName == "next_cursor":
            self.inNextCursor = True
        else:
            self.currentField = tagName


    def end(self, tagName):
        if tagName == "user":
            self.currentMember = None
        elif tagName == "next_cursor":
            self.inNextCursor = False


    def text(self, text):
        if self.inNextCursor:
            self.nextCursor = text
        elif self.currentField and self.currentMember:
            setattr(self.currentMember, self.currentField, text)



