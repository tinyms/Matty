__author__ = 'tinyms'

from sqlalchemy import func

from tinyms.core.common import Utils

from tinyms.core.web import IAuthRequest
from tinyms.core.entity import Account
from tinyms.core.orm import SessionFactory
from tinyms.core.annotation import ObjectPool, route, setting, api
from tinyms.core.setting import UserSettingHelper, AppSettingHelper


@route("/workbench/setting")
class SettingPage(IAuthRequest):
    def get(self, *args, **kwargs):
        return self.render("workbench/setting.html", items=ObjectPool.setting)


@api("tinyms.core.setting")
class SettingApi():
    def load(self):
        usr = self.request.current_user
        level_u = UserSettingHelper(usr)
        level_u_ = level_u.load()
        level_s = AppSettingHelper.load()
        level_all = dict(level_u_, **level_s)
        return level_all

    def save(self):
        kv = self.request.wrap_params_to_dict()
        level_user = dict()
        level_system = dict()
        for k in kv:
            if k.startswith("u_"):
                level_user[k] = kv[k]
            elif k.startswith("s_"):
                level_system[k] = kv[k]
        AppSettingHelper.set(level_system)
        u = UserSettingHelper("%s" % self.request.current_user)
        u.set(level_user)

        #允许用户在设置保存之后再做其它数据变更
        items = ObjectPool.setting
        for k in items.keys():
            obj = items[k].cls()
            if hasattr(obj, "save"):
                msg = obj.save(kv, self)
                if msg:
                    return msg

        AppSettingHelper.reload()
        return "success"


@setting("tinyms_core_setting_sys", "workbench/sys_setting_page.html", "基本", "tinyms.entity.setting.system")
class SystemSetting():
    def save(self, kv, http_req):
        return ""

    def form_submit_javascript(self, http_req):
        pass

    def form_fill_javascript(self, http_req):
        pass


@setting("tinyms_core_setting_user", "workbench/user_setting_page.html", "个人", "tinyms.entity.setting.user")
class SystemSetting():
    def save(self, kv, http_req):
        _usr_old_pwd = kv.get("_usr_old_pwd")
        _usr_new_pwd = kv.get("_usr_new_pwd")
        _usr_new_repwd = kv.get("_usr_new_repwd")
        if _usr_new_pwd == _usr_new_repwd:
            usr_id = http_req.current_user
            sf = SessionFactory.new()
            num = sf.query(func.count(Account.id)).filter(Account.id == usr_id) \
                .filter(Account.login_pwd == Utils.md5(_usr_old_pwd)).scalar()
            if num > 0:
                a = sf.query(Account).get(usr_id)
                a.login_pwd = Utils.md5(_usr_new_pwd)
                sf.commit()
                return ""
            else:
                return "PasswordError"
        else:
            return "PasswordNotSame"

    def form_submit_javascript(self, req):
        pass

    def form_fill_javascript(self, req):
        pass