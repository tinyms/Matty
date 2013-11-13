__author__ = 'tinyms'

import os
import sys
import base64
import uuid
import webbrowser

from tornado.ioloop import IOLoop
from tornado.web import Application

from tinyms.core.common import Plugin, Utils
from tinyms.core.annotation import IWebConfig, ObjectPool
from tinyms.core.orm import SessionFactory
from tinyms.core.loader import Loader

Plugin.load()

ws_settings = dict()
ws_settings["debug"] = True
ws_settings["static_path"] = os.path.join(os.getcwd(), "static")
ws_settings["template_path"] = os.path.join(os.getcwd(), "templates")
ws_settings["cookie_secret"] = "askgpoi45345j2l34j6lkjasljdfpajsfd"#(base64.b64encode(uuid.uuid4().bytes + uuid.uuid4().bytes)).decode("utf-8")

ws_settings["ui_modules"] = dict()
for key in ObjectPool.ui_mapping:
    ws_settings["ui_modules"][key] = ObjectPool.ui_mapping[key]

port = 80
web_configs = Plugin.get(IWebConfig)
if web_configs:
    for web_config in web_configs:
        if hasattr(web_config,"debug"):
            ws_settings["debug"] = web_config.debug()
        if hasattr(web_config, "server_port"):
            port = web_config.server_port()
        if hasattr(web_config, "settings"):
            web_config.settings(ws_settings)
        #Only one in application
        if hasattr(web_config, "database_driver"):
            SessionFactory.__engine__ = web_config.database_driver()
            SessionFactory.create_tables()
            Loader.init()

#compress js and css file to one
Utils.combine_text_files(os.path.join(os.getcwd(), "static/jslib/"), "tinyms.common")
for urls in ObjectPool.url_patterns:
    print("Url Mapping:",urls)
app = Application(ObjectPool.url_patterns, **ws_settings)

if __name__ == "__main__":
    server_new = True
    try:
        app.listen(port)
    except Exception as e:
        server_new = False
        print("%s" % e)
    webbrowser.open_new_tab("http://localhost:%i" % port)
    if server_new:
        try:
            IOLoop.instance().start()
        except Exception as e:
            print("%s" % e)
            sys.exit(1)