__author__ = 'tinyms'

import json
from sqlalchemy import or_
from tinyms.core.common import Utils
from tinyms.core.web import IAuthRequest
from tinyms.core.annotation import route, ajax, auth, dataview_provider, datatable_provider
from tinyms.core.orm import SessionFactory
from tinyms.core.entity import SecurityPoint, Role, Account, Archives
from tinyms.dao.account import AccountHelper


@ajax("RoleSecurityPointsAssign")
class RoleSecurityPointsEdit():
    __export__ = ["list", "save"]

    @auth({"tinyms.entity.role.points.view"}, [])
    def list(self):
        role_id = self.param("id")
        if not role_id:
            return []
        cnn = SessionFactory.new()
        points = cnn.query(SecurityPoint.id).join((Role, SecurityPoint.roles)).filter(Role.id == role_id).all()
        return [p[0] for p in points]

    @auth({"tinyms.entity.role.points.update"}, ["UnAuth"])
    def save(self):
        role_id = self.param("id")
        if not role_id:
            return ["Error"]
        points = json.loads(self.param("points"))
        cnn = SessionFactory.new()
        role = cnn.query(Role).filter(Role.id == role_id).limit(1).scalar()
        if role and not role.name == "SuperAdmin":
            role.securitypoints = []
            cnn.commit()
            spoints = cnn.query(SecurityPoint).filter(SecurityPoint.id.in_(points)).all()
            for sp in spoints:
                role.securitypoints.append(sp)
            cnn.commit()
        return ["success"]

    pass


@ajax("AccountRoleEdit")
class AccountRoleEdit():
    __export__ = ["list", "save"]

    @auth({"tinyms.entity.account.role.view"}, [])
    def list(self):
        account_id = Utils.parse_int(self.param("id"))
        cnn = SessionFactory.new()
        ds = cnn.query(Role.id).join(Account, Role.accounts).filter(Account.id == account_id).all()
        roles = list()
        for row in ds:
            roles.append(row[0])
        return roles

    @auth({"tinyms.entity.account.role.edit"}, ["UnAuth"])
    def save(self):
        account_id = Utils.parse_int(self.param("id"))
        role_id = Utils.parse_int(self.param("role_id"))
        state = Utils.parse_int(self.param("state"))
        cnn = SessionFactory.new()
        account = cnn.query(Account).get(account_id)
        if account:
            role = cnn.query(Role).get(role_id)
            if role:
                if state == 0:
                    account.roles.append(role)
                else:
                    account.roles.remove(role)
                cnn.commit()
                return ["success"]
        return ["failure"]


@route("/workbench/security")
class RoleOrg(IAuthRequest):
    def get(self, *args, **kwargs):
        context = dict()
        categories = self.role_categories()
        all_ = list()
        for c in categories:
            sub = list()
            groups = self.role_groups(c)
            for g in groups:
                sub.append((g, self.points(c, g)))
            all_.append((c, sub, Utils.md5(c)))

        context["categories"] = all_
        context["roles_for_account"] = self.role_for_account()
        return self.render("workbench/role_org.html", data=context)

    #列出可用角色
    def role_for_account(self):
        cnn = SessionFactory.new()
        items = cnn.query(Role.id, Role.name).all()
        print(items)
        return items

    def role_categories(self):
        cnn = SessionFactory.new()
        items = cnn.query(SecurityPoint.category).group_by(SecurityPoint.category).all()
        categories = [(cat[0]) for cat in items]
        return categories

    def role_groups(self, c):
        cnn = SessionFactory.new()
        items = cnn.query(SecurityPoint.group_).filter(SecurityPoint.category == c). \
            group_by(SecurityPoint.group_).all()
        groups = [item[0] for item in items]
        return groups

    def points(self, c, g):
        cnn = SessionFactory.new()
        items = cnn.query(SecurityPoint).filter(SecurityPoint.category == c).filter(SecurityPoint.group_ == g).order_by(
            SecurityPoint.id.asc()).all()
        return items


@datatable_provider("tinyms.core.entity.Role")
class RoleDataProvider():
    def total(self, query, req):
        q = query.filter(Role.name != "SuperAdmin")
        return q

    def dataset(self, query, req):
        q = query.filter(Role.name != "SuperAdmin")
        return q

#账户管理数据提供
@dataview_provider("tinyms.core.view.AccountManager")
class AccountDataProvider():
    def count(self, default_search_val, http_req):
        db_cnn = SessionFactory.new()
        q = db_cnn.query(Account, Archives.name, Archives.email) \
            .outerjoin(Archives, Account.archives_id == Archives.id) \
            .filter(Account.login_name != "root")
        if default_search_val:
            q = q.filter(or_(Account.login_name.like('%' + default_search_val + '%'),
                             Archives.name.like('%' + default_search_val + '%'),
                             Archives.email.like('%' + default_search_val + '%')))
        return q.count()

    def list(self, default_search_val, start, limit, http_req):
        db_cnn = SessionFactory.new()
        q = db_cnn.query(Account, Archives.name, Archives.email) \
            .outerjoin(Archives, Account.archives_id == Archives.id) \
            .filter(Account.login_name != "root")
        if default_search_val:
            q = q.filter(or_(Account.login_name.like('%' + default_search_val + '%'),
                             Archives.name.like('%' + default_search_val + '%'),
                             Archives.email.like('%' + default_search_val + '%')))
        ds = q.order_by(Account.id.desc()).offset(start).limit(limit).all()
        items = list()
        for row in ds:
            item = dict()
            obj = row[0].dict()
            item["id"] = obj["id"]
            item["archives_id"] = obj["archives_id"]
            item["login_name"] = obj["login_name"]
            item["enabled"] = obj["enabled"]
            item["last_logon_time"] = Utils.format_datetime_short(obj["last_logon_time"])
            item["create_time"] = Utils.format_datetime_short(obj["create_time"])
            item["name"] = row[1]
            item["email"] = row[2]
            items.append(item)
        return items

    def add(self, http_req):
        login_name = http_req.get_argument("login_name")
        if not login_name:
            return "UserLoginIdNotBlank"
        password = http_req.get_argument("password")
        if not password:
            return "PasswordNotBlank"
        repassword = http_req.get_argument("repassword")
        if password != repassword:
            return "PasswordNotSame"
        bind_target_user = http_req.get_argument("archives_id")
        enabled = Utils.parse_int(http_req.get_argument("enabled"))
        account_id = AccountHelper.create(login_name, password, bind_target_user, enabled)
        return account_id

    def modify(self, id_, http_req):
        login_name = http_req.get_argument("login_name")
        if not login_name:
            return "UserLoginIdNotAllowedBlank"
        password = http_req.get_argument("password")
        print(password)
        if password:
            repassword = http_req.get_argument("repassword")
            if password != repassword:
                return "PasswordIsNotSame"
        bind_target_user = http_req.get_argument("archives_id")
        enabled = Utils.parse_int(http_req.get_argument("enabled"))
        msg = AccountHelper.update(id_, login_name, password, bind_target_user, enabled)
        if msg == "Updated":
            return ""
        return msg

    def delete(self, id_, http_req):
        msg = AccountHelper.delete(id_)
        if msg == "Success":
            return ""
        return msg