__author__ = 'tinyms'

from datetime import datetime
from sqlalchemy import func
from tinyms.core.common import Utils
from tinyms.core.orm import SessionFactory
from tinyms.core.entity import Role, Archives, Account, SecurityPoint
from tinyms.core.annotation import ObjectPool, reg_point
from tinyms.dao.category import CategoryHelper
from tinyms.core.setting import AppSettingHelper


#Web服务器加载时，初始化必要数据
class Loader():
    @staticmethod
    def init():
        AppSettingHelper.load()
        #Create Root Category
        helper = CategoryHelper("ROOT")
        if not helper.exists("ROOT"):
            helper.create("ROOT")
        role_id = Loader.create_super_role()
        if not role_id:
            return
        Loader.create_root_account(role_id)
        Loader.create_base_securitypoints()
        Loader.assign_points_to_superadmin(role_id)
        #自定义加载
        for cls in ObjectPool.server_starups:
            obj = cls()
            if hasattr(obj, "load"):
                obj.load()

    @staticmethod
    def create_root_account(role_id):
        cnn = SessionFactory.new()
        num = cnn.query(func.count(Archives.id)).scalar()
        role_ = cnn.query(Role).get(role_id)
        if num == 0:
            usr = Archives()
            usr.name = "超级管理员"
            usr.email = "admin@local.com"
            usr.code = "P00001"
            cnn.add(usr)
            cnn.commit()

            a = Account()
            a.login_name = "root"
            a.login_pwd = Utils.md5("root")
            a.create_time = datetime.now()
            a.enabled = 1
            a.archives_id = usr.id
            cnn.add(a)
            a.roles.append(role_)
            cnn.commit()

    @staticmethod
    def create_super_role():
        cnn = SessionFactory.new()
        role_ = cnn.query(Role).filter(Role.name == "SuperAdmin").limit(1).scalar()
        if role_:
            return role_.id
        role_ = Role()
        role_.name = "SuperAdmin"
        role_.description = "超级管理员"
        cnn.add(role_)
        cnn.commit()
        return role_.id

    @staticmethod
    def assign_points_to_superadmin(role_id):
        cnn = SessionFactory.new()
        role_ = cnn.query(Role).get(role_id)
        changes = list()
        for point in ObjectPool.points:
            p = cnn.query(SecurityPoint).filter(SecurityPoint.key_ == point.key_).limit(1).scalar()
            if p:
                p.category = point.category
                p.group_ = point.group_
                p.description = point.description
                changes.append(p)
            else:
                cnn.add(point)
                point.roles.append(role_)
        cnn.commit()

    @staticmethod
    def create_base_securitypoints():
        #Menu
        reg_point("tinyms.sidebar.archives.show", "菜单", "侧边栏", "人员档案")
        reg_point("tinyms.sidebar.role_org.show", "菜单", "侧边栏", "角色组织")
        reg_point("tinyms.sidebar.sys_categories.show", "菜单", "侧边栏", "系统分类")
        reg_point("tinyms.sidebar.sys_params.show", "菜单", "侧边栏", "系统参数")
        #OrgTreeView
        reg_point("tinyms.view.orgtree.list", "角色组织", "组织", "查看组织列表")
        reg_point("tinyms.view.orgtree.view", "角色组织", "组织", "查看组织明细")
        reg_point("tinyms.view.orgtree.add", "角色组织", "组织", "添加组织")
        reg_point("tinyms.view.orgtree.update", "角色组织", "组织", "修改组织")
        reg_point("tinyms.view.orgtree.delete", "角色组织", "组织", "删除组织")
        #分类管理
        reg_point("tinyms.view.termtaxonomy.list", "角色组织", "分类", "查看分类列表")
        reg_point("tinyms.view.termtaxonomy.view", "角色组织", "分类", "查看分类明细")
        reg_point("tinyms.view.termtaxonomy.add", "角色组织", "分类", "添加分类")
        reg_point("tinyms.view.termtaxonomy.update", "角色组织", "分类", "修改分类")
        reg_point("tinyms.view.termtaxonomy.delete", "角色组织", "分类", "删除分类")
        #角色管理
        reg_point("tinyms.entity.role.list", "角色组织", "角色", "查看角色列表")
        reg_point("tinyms.entity.role.view", "角色组织", "角色", "查看角色明细")
        reg_point("tinyms.entity.role.add", "角色组织", "角色", "添加角色")
        reg_point("tinyms.entity.role.update", "角色组织", "角色", "修改角色")
        reg_point("tinyms.entity.role.delete", "角色组织", "角色", "删除角色")
        reg_point("tinyms.entity.role.points.view", "角色组织", "权限", "查看角色权限点")
        reg_point("tinyms.entity.role.points.update", "角色组织", "权限", "修改角色权限")
        #账户管理
        reg_point("tinyms.entity.account.list", "角色组织", "账户", "查看账户列表")
        reg_point("tinyms.entity.account.view", "角色组织", "账户", "查看账户明细")
        reg_point("tinyms.entity.account.add", "角色组织", "账户", "添加账户")
        reg_point("tinyms.entity.account.update", "角色组织", "账户", "修改账户")
        reg_point("tinyms.entity.account.delete", "角色组织", "账户", "删除账户")
        reg_point("tinyms.entity.account.role.view", "角色组织", "账户", "查看账户角色")
        reg_point("tinyms.entity.account.role.edit", "角色组织", "账户", "为账户设置角色")
        #档案管理
        reg_point("tinyms.entity.archives.list", "档案管理", "人员", "查看人员列表")
        reg_point("tinyms.entity.archives.view", "档案管理", "人员", "查看人员明细")
        reg_point("tinyms.entity.archives.add", "档案管理", "人员", "添加人员")
        reg_point("tinyms.entity.archives.update", "档案管理", "人员", "修改人员")
        reg_point("tinyms.entity.archives.delete", "档案管理", "人员", "删除人员")
        #档案管理
        reg_point("tinyms.entity.setting.system", "系统设置", "设置", "全局设置")
        reg_point("tinyms.entity.setting.user", "系统设置", "设置", "用户自定义设置")

        for cls in ObjectPool.user_security_points:
            obj = cls()
            if hasattr(obj, "reg"):
                obj.reg()


