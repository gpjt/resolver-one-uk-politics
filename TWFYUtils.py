from os import path

from XMLAPIUtils import XMLAPIFunction

from System.Web import HttpUtility



apiKeyFile = open(path.join(path.dirname(__file__), "twfy-apikey.txt"), "r")
apiKey = apiKeyFile.readline()
apiKeyFile.close()

twfyURL = "http://www.theyworkforyou.com/api/%s?key=%s&output=xml" % ("%s", apiKey)

class TWFYFunction(XMLAPIFunction):
    def __init__(self, functionName):
        XMLAPIFunction.__init__(self, twfyURL % functionName)



class GetConstituencies(TWFYFunction):

    def __init__(self):
        TWFYFunction.__init__(self, "getConstituencies")
        self.inConstituency = False
        self.constituencies = []

    def start(self, tagName):
        if tagName == "name":
            self.inConstituency = True

    def end(self, tagName):
        if tagName == "name":
            self.inConstituency = False

    def text(self, text):
        if self.inConstituency:
            self.constituencies.append(text)


class GetGeometry(TWFYFunction):

    def __init__(self, constituency):
        TWFYFunction.__init__(self, "getGeometry")
        self.constituency = constituency
        self.url += "&name=" + HttpUtility.UrlEncode(constituency)
        self.currentTag = None
        self.fields = ("centre_lat", "centre_lon", "area", "min_lat", "max_lat", "min_lon", "max_lon", "parts")

    def start(self, tagName):
        if tagName in self.fields:
            self.currentTag = tagName

    def end(self, tagName):
        self.currentTag = None

    def text(self, text):
        if self.currentTag is not None:
            setattr(self, self.currentTag, text)

    def __str__(self):
        return "Constituency %s: [%s]" % (self.constituency, [("%s=%s" % (field, getattr(self, field, None))) for field in self.fields])


class GetMP(TWFYFunction):

    def __init__(self, constituency):
        TWFYFunction.__init__(self, "getMP")
        self.constituency = constituency
        self.url += "&constituency=" + HttpUtility.UrlEncode(constituency)
        self.currentTag = None
        self.fields = (
            "member_id", "house", "first_name", "last_name", "constituency", "party",
            "person_id", "title", "lastupdate", "full_name", "image",
            "entered_house", "left_house", "entered_reason", "left_reason",
        )

    def start(self, tagName):
        if tagName in self.fields:
            self.currentTag = tagName

    def end(self, tagName):
        self.currentTag = None

    def text(self, text):
        if self.currentTag is not None:
            setattr(self, self.currentTag, text)

    def __str__(self):
        return "MP for %s: [%s]" % (self.constituency, [("%s=%s" % (field, getattr(self, field, None))) for field in self.fields])


class MP(object):
    pass


class GetMPs(TWFYFunction):

    def __init__(self):
        TWFYFunction.__init__(self, "getMPs")
        self.inMatch = False
        self.mps = []
        self.currentField = None
        self.currentMP = None

    def start(self, tagName):
        if tagName == "match":
            self.currentMP = MP()
            self.mps.append(self.currentMP)
        else:
            self.currentField = tagName

    def end(self, tagName):
        if tagName == "match":
            self.currentMP = None


    def text(self, text):
        if self.currentField and self.currentMP:
            setattr(self.currentMP, self.currentField, text)


class MemberData(object):
    pass

class GetMPsInfo(TWFYFunction):

    def __init__(self, ids):
        TWFYFunction.__init__(self, "getMPsInfo")
        self.url += "&id=" + HttpUtility.UrlEncode(",".join(str(id) for id in ids))
        self.mps = []
        self.currentField = None
        self.currentMP = None
        self.inByMemberID = False

    def start(self, tagName):
        if tagName == "match" and self.currentMP is None:
            self.currentMP = MP()
            self.mps.append(self.currentMP)
        elif tagName == "by_member_id" and self.currentMP is not None:
            self.currentMP.memberData = MemberData()
            self.inByMemberID = True
        else:
            self.currentField = tagName

    def end(self, tagName):
        if tagName == "by_member_id":
            self.inByMemberID = False
        if tagName == "match" and not self.inByMemberID:
            self.currentMP = None


    def text(self, text):
        if self.currentField:
            if self.inByMemberID:
                setattr(self.currentMP.memberData, self.currentField, text)
            elif self.currentMP:
                setattr(self.currentMP, self.currentField, text)