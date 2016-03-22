import webapp2
from admin import AdminHandler
from dashboard import DashboardHandler

app = webapp2.WSGIApplication([
    webapp2.Route('/', DashboardHandler),
    webapp2.Route('/admin', AdminHandler, name="admin"),
], debug=True)
