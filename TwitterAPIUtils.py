from os import path

from XMLAPIUtils import XMLAPIFunction


credentialsFile = open(path.join(path.dirname(__file__), "twitter-credentials.txt"), "r")
userName = credentialsFile.readline()
password = credentialsFile.readline()
credentialsFile.close()


class TwitterUser(object):
    pass


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
            XMLAPIFunction.getData(self, {"cursor" : self.nextCursor}, userName, password)
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
            self.currentCurrentMember = None
        elif tagName == "next_cursor":
            self.inNextCursor = False
        
            
    def text(self, text):
        if self.inNextCursor:
            self.nextCursor = text
        elif self.currentField and self.currentMember:
            setattr(self.currentMember, self.currentField, text)
        
                

