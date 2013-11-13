__author__ = 'tinyms'

from tinyms.core.web import IRequest, route
from tinyms.core.annotation import api, ajax, auth


#@route(r"/lottery/betting")
#@sidebar("/lottery","/lottery/betting","足彩")
#@sidebar("/lottery/betting","/lottery/betting","投注")
#class UITestHandler(IRequest):
#    def get(self):
#        self.render("betting.html")

@api("test")
class ApiTest():
    @auth({'key1'})
    def list(self):
        return [2, 5, 1, 12]


@ajax("test")
class AjaxTest():
    __export__ = ["list"]

    def list(self):
        print(self.param("abc"))
        return [2, 5, 1, 12]


@route(r"/ball")
class WelcomeHandler(IRequest):
    def get(self):
        self.redirect("/static/index.html")


@route(r"/")
class WelcomeHandler(IRequest):
    def get(self):
        self.redirect("/login")