from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

class MainPage(webapp.RequestHandler):
	def get(self):
		self.response.headers['content-type'] = 'text/plain'
		self.response.out.write('First response from cmstats home page \n')
		self.response.out.write(self.request.query_string + "\n")
		self.response.out.write(self.request.url + "\n")
		self.response.out.write(self.request.body + "\n")

app = webapp.WSGIApplication([('/', MainPage)], debug = True)

def main():
	run_wsgi_app(app)

if __name__ == "__main__":
	main()