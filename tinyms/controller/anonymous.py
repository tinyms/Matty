__author__ = 'tinyms'

from sqlalchemy import func

from tinyms.core.annotation import route, api
from tinyms.core.web import IRequest
from tinyms.core.common import Utils
from tinyms.core.orm import SessionFactory
from tinyms.core.entity import Account, Archives, Role
from tinyms.core.setting import AppSettingHelper


@route("/login")
class Login(IRequest):
    def get(self, *args, **kwargs):
        """
        render login form
        :param args:
        :param kwargs:
        """
        allowd_register = AppSettingHelper.get("s_usr_register_open", "N")
        opt = dict()
        opt["allowd_register"] = allowd_register
        self.render("login.html", opt=opt)

    def post(self, *args, **kwargs):
        """
        do login action
        :param args:
        :param kwargs:
        """
        login_id = self.get_argument("login_id")
        login_pwd = self.get_argument("login_pwd")
        if not login_id or not login_pwd:
            self.redirect(self.get_login_url())
        cnn = SessionFactory.new()

        if Utils.is_email(Utils.trim(login_id)):
            rows = cnn.query(Account.id, Archives.name).outerjoin(Archives, Account.archives_id == Archives.id) \
                .filter(Archives.email == login_id).filter(Account.login_pwd == Utils.md5(login_pwd)) \
                .filter(Account.enabled == 1).limit(1).all()
            if len(rows) > 0:
                id_ = rows[0][0]
                name = rows[0][1]
                self.set_secure_cookie(IRequest.__key_account_id__, "%i" % id_)
                self.set_secure_cookie(IRequest.__key_account_name__, name)
                Login.update_last_login_datetime(id_)
        else:
            rows = cnn.query(Account.id, Archives.name).outerjoin(Archives, Account.archives_id == Archives.id) \
                .filter(Account.login_name == login_id).filter(Account.login_pwd == Utils.md5(login_pwd)) \
                .filter(Account.enabled == 1).limit(1).all()
            if len(rows) > 0:
                id_ = rows[0][0]
                name = rows[0][1]
                self.set_secure_cookie(IRequest.__key_account_id__, "%i" % id_)
                self.set_secure_cookie(IRequest.__key_account_name__, name)
                Login.update_last_login_datetime(id_)

        self.redirect("/workbench/dashboard")

    @staticmethod
    def update_last_login_datetime(id_):
        cnn = SessionFactory.new()
        a = cnn.query(Account).get(id_)
        a.last_logon_time = Utils.current_datetime()
        cnn.commit()


@route("/reg")
class Reg(IRequest):
    def get(self, *args, **kwargs):
        allowd_register = AppSettingHelper.get("s_usr_register_open", "N")
        opt = dict()
        opt["allowd_register"] = allowd_register
        self.render("reg.html", opt=opt)


@api("tinyms.controller.anonymous.reg")
class RegApi():
    def create(self):
        account_name = self.param("account_name")
        if not account_name:
            return "AccountNameRequired"
        email = self.param("email")
        if not email:
            return "EmailRequired"
        pwd = self.param("pwd")
        if not pwd:
            return "PwdRequired"
        agree = self.param("agree")
        print(agree)
        if not agree:
            return "AgreeRequired"
        re_pwd = self.param("re_pwd")
        if pwd != re_pwd:
            return "PwdNotSame"

        sf = SessionFactory.new()
        num = sf.query(func.count(Account.id)).filter(Account.login_name == account_name).scalar()
        if num > 0:
            return "AccountExists"
        num = sf.query(func.count(Archives.id)).filter(Archives.email == email).scalar()
        if num > 0:
            return "EmailExists"

        #create a person
        length = len(str(sf.query(func.count(Archives.id)).scalar()))
        max_length = AppSettingHelper.get("s_usr_code_fmt_length", "5")
        prefix = AppSettingHelper.get("s_usr_code_prefix", "P")
        if length > Utils.parse_int(max_length):
            max_length = "%s" % (length + 1)
        fmt = prefix + "%0" + max_length + "d"

        p = Archives()
        p.email = email
        p.name = Utils.email_account_name(email)
        p.join_date = Utils.current_datetime()
        sf.add(p)
        sf.flush()
        p.code = fmt % p.id

        u = Account()
        u.login_name = account_name
        u.login_pwd = Utils.md5(pwd)
        u.create_time = Utils.current_datetime()
        u.last_logon_time = Utils.current_datetime()
        u.enabled = 1
        u.archives_id = p.id
        sf.add(u)
        sf.flush()

        default_role_id = Utils.parse_int(AppSettingHelper.get("s_usr_register_default_role_name", 0))
        if default_role_id > 0:
            default_role = sf.query(Role).get(default_role_id)
            if default_role:
                u.roles.append(default_role)

        sf.commit()

        self.request.set_secure_cookie(IRequest.__key_account_id__, "%i" % u.id)
        self.request.set_secure_cookie(IRequest.__key_account_name__, email)
        return "Success"


@route("/logout")
class Logout(IRequest):
    def get(self, *args, **kwargs):
        self.clear_all_cookies()
        self.redirect("/login")