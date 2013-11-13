__author__ = 'tinyms'
from tinyms.core.web import IAuthRequest
from tinyms.core.annotation import route

@route("/workbench/dashboard")
class Dashboard(IAuthRequest):
    def get(self, *args, **kwargs):
        self.render("workbench/dashboard.html")
    def post(self, *args, **kwargs):
        self.render("workbench/dashboard.html")