__author__ = 'tinyms'

import json
from tornado.web import RequestHandler
from tinyms.core.common import JsonEncoder
from tinyms.core.annotation import EmptyClass, ObjectPool, route
from tinyms.core.cache import CacheManager
from tinyms.dao.account import AccountHelper


class IRequest(RequestHandler):
    __key_account_id__ = "account_id"
    __key_account_name__ = "account_name"
    __key_account_points__ = "@cache.cookie.account.securitypoints.%s"

    def __init__(self, application, request, **kwargs):
        RequestHandler.__init__(self, application, request, **kwargs)

    def auth(self, points=set()):
        """
        细微控制数据输出,不产生页面跳转相关动作
        :param points:
        :return:
        """
        diff = points & self.get_current_account_points()
        if len(diff) > 0:
            return True
        return False

    def get_template_namespace(self):
        namespace = dict(
            handler=self,
            request=self.request,
            current_user=self.current_user,
            locale=self.locale,
            _=self.locale.translate,
            static_url=self.static_url,
            xsrf_form_html=self.xsrf_form_html,
            reverse_url=self.reverse_url,
            auth=self.auth # Add to auth current user security points
        )
        namespace.update(self.ui)
        return namespace

    def get_login_url(self):
        return "/login"

    def write_error(self, status_code, **kwargs):
        if status_code == 401:
            self.render("login.html")
        elif status_code == 403:
            self.render("err.html", reason="访问禁止")
        elif status_code == 404:
            self.clear_all_cookies()
        else:
            self.render("err.html", reason="服务器内部错误")


    def get_current_user(self):
        """
        account id, int
        :return:
        """
        id = self.get_secure_cookie(IRequest.__key_account_id__)
        if id:
            return int(id)
        return None

    def get_current_account_points(self):
        """
        account security points: set('key1','key2',..)
        :return:
        """
        temp = set()
        if not self.get_current_user():
            return temp
        cache = CacheManager.get(500, 30 * 1000)
        points = cache.get(IRequest.__key_account_points__ % self.get_current_user())
        if points:
            print("Exists Cache Account Points")
            return points
        else:
            temp = temp.union(AccountHelper.points(self.get_current_user()))
            return temp

    def get_current_account_name(self):
        """
        current account name,sex,post,org etc.
        :return:
        """
        name = self.get_secure_cookie(IRequest.__key_account_name__)
        if name:
            return name
        return ""

    def wrap_entity(self, entity_object, excude_keys=["id"]):
        """
        把参数值填充到对象对应属性中，针对ORM中的Entity
        :param obj:
        :param excude_keys:
        :return:
        """
        dict_ = dict()
        args = self.request.arguments
        for key in args.keys():
            if excude_keys.count(key) != 0:
                continue
            dict_[key] = self.get_argument(key)
        entity_object.dict(dict_)
        return entity_object

    def wrap_params_to_dict(self):
        dict_ = dict()
        args = self.request.arguments
        for key in args:
            dict_[key] = self.get_argument(key)
        return dict_

    def wrap_params_to_obj(self):
        obj = EmptyClass()
        args = self.request.arguments
        for key in args:
            setattr(obj, key, self.get_argument(key))
        return obj


class IAuthRequest(IRequest):
    def __init__(self, application, request, **kwargs):
        IRequest.__init__(self, application, request, **kwargs)

    def prepare(self):
        if not self.get_current_user():
            self.redirect("/login")


@route(r"/api/(.*)/(.*)")
class ApiHandler(IRequest):
    def get(self, key, method_name):
        self.req(key, method_name)

    def post(self, key, method_name):
        self.req(key, method_name)

    def req(self, key, method_name):
        """
        Url: localhost/api/key/method
        :param key: example: com.tinyms.category.v2
        :return:

        example:
            @api("com.tinyms.category.v2")
            class ApiTest():
                def create():
                    prama1 = self.param("prama1");
                    req = self.request # IRequest

            client side:
            $.post("/api/com.tinyms.category.v2/create",params,func,"json");
        """
        self.set_header("Content-Type", "text/json;charset=utf-8")
        if not key:
            self.write("Key require.")
        else:
            cls = ObjectPool.api.get(key)
            if not cls:
                self.write("Object not found.")
            else:
                obj = cls()
                if hasattr(obj, method_name):
                    setattr(obj, "request", self)
                    setattr(obj, "__params__", self.wrap_params_to_dict())
                    setattr(obj, "param", lambda key: obj.__params__.get(key))
                    func = getattr(obj, method_name)
                    result = func()
                    self.write(json.dumps(result, cls=JsonEncoder))


@route(r"/ajax/(.*).js")
class AjaxHandler(IRequest):
    def get(self, key):
        self.set_header("Content-Type", "text/javascript;charset=utf-8")
        if not key:
            self.write("alert('Ajax key require.')")
        else:
            cls = ObjectPool.ajax.get(key)
            if not cls:
                self.write("alert('Object not found.')")
            else:
                obj = cls()
                if hasattr(obj, "__export__") and type(obj.__export__) == list:
                    return self.render("widgets/ajax.tpl",
                                       module_name=obj.__class__.__module__,
                                       class_name=obj.__class__.__qualname__,
                                       key=key,
                                       methods=obj.__export__)
                else:
                    self.write("alert('Attr `__export__` not exists or blank!');")

    def post(self, key):

        data_type = self.get_argument("__data_type__")
        if data_type == "json":
            self.set_header("Content-Type", "text/json;charset=utf-8")
        elif data_type == "script":
            self.set_header("Content-Type", "text/javascript;charset=utf-8")
        elif data_type == "html":
            self.set_header("Content-Type", "text/html;charset=utf-8")

        if not key:
            self.write("alert('Ajax key require.')")
        else:
            cls = ObjectPool.ajax.get(key)
            if not cls:
                self.write("Class not found.")
            else:
                method_name = self.get_argument("__method_name__")
                obj = cls()
                if hasattr(obj, method_name):
                    setattr(obj, "request", self)
                    setattr(obj, "__params__", self.wrap_params_to_dict())
                    setattr(obj, "param", lambda key_: obj.__params__.get(key_))
                    func = getattr(obj, method_name)
                    result = func()
                    if data_type == "json":
                        self.write(json.dumps(result, cls=JsonEncoder))
                    else:
                        self.write(result)


@route("/autocomplete/(.*)")
class AutoCompleteHandler(IRequest):
    def post(self, id_):
        cls = ObjectPool.autocomplete_keys.get(id_)
        self.set_header("Content-Type", "text/json;charset=utf-8")
        if cls:
            obj = cls()
            if hasattr(obj, "data"):
                search_word = self.get_argument("search_word")
                data = obj.data(self, search_word)
                self.write(json.dumps(data, cls=JsonEncoder))
        else:
            self.write(json.dumps(list(), cls=JsonEncoder))