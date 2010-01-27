import clr
clr.AddReference("System.Web")

from System.IO import StreamReader
from System.Net import WebRequest, NetworkCredential
from System.Web import HttpUtility
from System.Xml import XmlNodeType, XmlTextReader


class XMLAPIFunction(object):
    def __init__(self, url):
        self.url = url

    def getData(self, userName=None, password=None, extraParams={}):
        url = self.url
        if len(extraParams.items()) > 0:
            print "Adding ", extraParams, " onto ", url
            if url.find("?") == -1:
                url += "?"
            url += "&".join(["%s=%s" % (k, HttpUtility.UrlEncode(v)) for k, v in extraParams.items()])
        print url
        request = WebRequest.Create(url)
        if userName is not None:
            request.Credentials = NetworkCredential(userName, password)
        response = request.GetResponse()
        try:
            reader = XmlTextReader(StreamReader(response.GetResponseStream()))
            while reader.Read():
                if reader.NodeType == XmlNodeType.Element:
                    self.start(reader.Name)
                elif reader.NodeType == XmlNodeType.Text:
                    self.text(reader.Value)
                elif reader.NodeType == XmlNodeType.EndElement:
                    self.end(reader.Name)
        finally:
            response.Close()

        return self
