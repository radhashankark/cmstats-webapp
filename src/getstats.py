'''
The module to get the CM stats and put them in the datastore
'''

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import urlfetch
from google.appengine.ext import db
import datetime

url = "http://stats.cyanogenmod.com"
result = urlfetch.fetch(url)
contentbyline = result.content.split("\n")
wantedline = "Not Found"
for line in contentbyline:
    if str(line).contains("<td><b>TOTAL</b></td>"):
        wantedline = contentbyline.next()

class Snapshot(db.Model):
    time = db.StringProperty(required=True)
    total = db.StringProperty(required=True)
    
curtime = datetime.datetime.strftime(datetime.datetime.now(), "%m%d%H%M") 
snapshot = Snapshot(time=curtime, total="1023")
snapshot.put()

class GetStats(webapp.RequestHandler):
    def get(self):
        self.response.headers['content-type'] = 'text/plain'
        self.response.out.write("Snapshot recorded at " + curtime + "\n")
        self.response.out.write("Lines in content : " + str(len(contentbyline)) + "\n")
        self.response.out.write(wantedline)

app = webapp.WSGIApplication([('/get/stats', GetStats)], debug = True)

def main():
    run_wsgi_app(app)

if __name__ == "__main__":
    main()