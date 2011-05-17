'''
The module to get the CM stats and put them in the datastore
'''

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import urlfetch
from google.appengine.ext import db
import datetime
import logging

url = "http://stats.cyanogenmod.com"
result = urlfetch.fetch(url)
contentbyline = result.content.split("\n")

curtime = datetime.datetime.strftime(datetime.datetime.now(), "%m%d%H%M")

class Snapshot(db.Model):
    time = db.StringProperty(required=True)
    type = db.StringProperty(required=True, choices=set(["Device", "Version", "Installs"]))
    name = db.StringProperty(required=True)
    installcount = db.IntegerProperty(required=True)

officialinstallflag = False
unofficialinstallflag = False
totalinstallflag = False
geteverything = False

if datetime.datetime.strftime(datetime.datetime.now(), "%M") == "00":
    geteverything = True
    logging.debug("Getting everything at " + curtime)
    
for line in contentbyline:
    if line.find("<td>Official Installs</td>") != -1:
        officialinstallflag = True
        continue
    elif line.find("<td>Unofficial Installs (KANGs)</td>") != -1:
        unofficialinstallflag = True
        continue
    elif line.find("<td><b>TOTAL</b></td>") != -1:
        totalinstallflag = True
        continue
    elif line.find("Installs by Version") != -1:
        devicetype = "Version"
    elif line.find("Installs by Device") != -1:
        devicetype = "Device"
    elif officialinstallflag == True:
        officialinstallflag = False
        end = line.find("/") - 1
        start = line.find(">") + 1
        if len(line[start:end]) > 3:
            officialinstalls = int(line[start:end].replace(",", ""))
        else:
            officialinstalls = int(line[start:end])
    elif unofficialinstallflag == True:
        unofficialinstallflag = False
        end = line.find("/") - 1
        start = line.find(">") + 1
        if len(line[start:end]) > 3:
            unofficialinstalls = int(line[start:end].replace(",", ""))
        else:
            unofficialinstalls = int(line[start:end])
    elif totalinstallflag == True:
        totalinstallflag = False
        end = line.find("/") - 1
        start = line.find("<b>") + 3
        if len(line[start:end]) > 3:
            totalinstalls = int(line[start:end].replace(",", ""))
        else:
            totalinstalls = int(line[start:end])
    elif line.find("<tr><td>") != -1:
        if geteverything == True:
            start = line.find("<tr><td>") + 8
            end = line.find("</td>")
            if len(line[start:end]) > 1:
                devicename = line[start:end]
            else:
                devicename = "Generic"
            start = line.find("</td><td>") + 9
            end = line.rfind("</td>")
            if len(line[start:end]) > 3:
                installs = int(line[start:end].replace(",", ""))
            else:
                installs = int(line[start:end])
            devicesnapshot = Snapshot(time=curtime, type=devicetype, name=devicename, installcount=installs)
            devicesnapshot.put()

totalinstallsnapshot = Snapshot(time=curtime, type="Installs", name="Total", installcount=totalinstalls)
officialinstallsnapshot = Snapshot(time=curtime, type="Installs", name="Official", installcount=officialinstalls)
unofficialinstallsnapshot = Snapshot(time=curtime, type="Installs", name="Unofficial", installcount=unofficialinstalls)
totalinstallsnapshot.put()
officialinstallsnapshot.put()
unofficialinstallsnapshot.put()

class GetStats(webapp.RequestHandler):
    def get(self):
        self.response.headers['content-type'] = 'text/plain'
        self.response.out.write("Snapshot at " + curtime + "\n")
        self.response.out.write("Official Installs : " + str(officialinstalls) + "\n")
        self.response.out.write("Unofficial Installs : " + str(unofficialinstalls) + "\n")
        self.response.out.write("total Installs : " + str(totalinstalls) + "\n")

app = webapp.WSGIApplication([('/get/stats', GetStats)], debug = True)

def main():
    run_wsgi_app(app)

if __name__ == "__main__":
    main()