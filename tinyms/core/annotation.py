__author__ = 'tinyms'

from functools import wraps
from tinyms.core.entity import SecurityPoint
from tinyms.core.common import Utils


#for plugin to extends
class EmptyClass(object):
    pass


class ObjectPool():
    mode_dev = False
    server_starups = list()
    points = list()
    user_security_points = list()
    api = dict()
    ajax = dict()
    url_patterns = list()
    sidebar_menus = list()
    ui_mapping = dict()
    treeview = dict()
    autocomplete_keys = dict()
    datatable_provider = dict()
    dataview_provider = dict()
    setting = dict()


class IWebConfig():
    def server_port(self):
        return 80

    def database_driver(self):
        return None

    def debug(self):
        return False

    def settings(self, ws_setting):
        """
        Append or modify tornado setting
        :param ws_setting: dict()
        :return:
        """
        return


def server_starup():
    """
    Web服务器启动的时候.类需要实现下列方法
    def load(),无返回值，在此方法内编写自定义逻辑
    """

    def ref_pattern(cls):
        if ObjectPool.server_starups.count(cls) == 0:
            ObjectPool.server_starups.append(cls)
        return cls

    return ref_pattern


def reg_point(key, category="", group_="", description=""):
    """
    :param key: 必须唯一，如果在系统中重复将被忽略掉
    :param category:分类
    :param group_:分类下的分组
    :param description:此安全点的用途
    :return:无返回值
    """
    if not key:
        return
    for sp in ObjectPool.points:
        if sp.key_ == key:
            return
    point = SecurityPoint()
    point.key_ = key
    point.description = description
    point.group_ = group_
    point.category = category
    ObjectPool.points.append(point)


def points():
    """
    用户注册自己的安全点.类需要实现下列方法
    def reg(),无返回值，请在此方法内使用reg_point方法进行安全点注册
    """

    def ref_pattern(cls):
        if ObjectPool.user_security_points.count(cls) == 0:
            ObjectPool.user_security_points.append(cls)
        return cls

    return ref_pattern


def route(pattern):

    """
    路由设置
    :param pattern: /path/(.*) 或者 /path/abc 等等
    :return:
    """

    def ref_pattern(cls):
        ObjectPool.url_patterns.append((pattern, cls))
        return cls

    return ref_pattern


def sidebar(path, url, label="", point="", position=0, icon_class="icon-link"):
    """

    :param path: /dashboard/count etc
    :param url:
    :param label:
    :param point:
    :param position: 1-1000
    :param icon_class:
    :return:
    """

    def ref_sidebar(cls):
        if path:
            if not url:
                return cls
            label_ = "Uname"
            if not label:
                label_ = path.split("/")[-1]
            else:
                label_ = label
            ObjectPool.sidebar_menus.append((position, path, url, label_, point, icon_class ))
        return cls

    return ref_sidebar


def auth(points=set(), default_value=None):
    def handle_func(func):
        @wraps(func)
        def returned_func(*args, **kwargs):
            self_ = args[0]
            account_id = self_.request.get_current_user()
            if not account_id:
                return returned_func
            points_ = self_.request.get_current_account_points()
            diff = points & points_
            if len(diff) > 0:
                return func(*args, **kwargs)
            else:
                return default_value

        return returned_func

    return handle_func


def api(key):
    """
    api mapping.
    """

    def ref(cls):
        ObjectPool.api[key] = cls
        return cls

    return ref


def ajax(key):
    """
    ajax mapping.
    """

    def ref(cls):
        ObjectPool.ajax[key] = cls
        return cls

    return ref


def ui(name):
    """
    ui mapping. 配置UI至模版可用
    """

    def ref_pattern(cls):
        ObjectPool.ui_mapping[name] = cls
        return cls

    return ref_pattern


def autocomplete(id_):
    """
    自动完成数据源
    def data(req, search_word)
    """

    def ref_ac(cls):
        ObjectPool.autocomplete_keys[Utils.md5(id_)] = cls
        return cls

    return ref_ac

#for widgets


def datatable_provider(entity_name):
    """
    受装饰的类可以实现下面任意方法
    def total(query,req) -> return query
    def dataset(query,req) -> return query

    def before_add(entity_obj,sf,req) 保存之前作一些校验动作,返回提示信息,entity_obj已经填充了表单传过来的数据
    def after_add(entity_obj,sf,req) ->return last inserted id,entity_obj已经填充了表单传过来的数据

    def before_modify(entity_obj,sf,req) 修改之前作一些校验动作,返回提示信息
    def after_modify(entity_obj,sf,req)

    def before_delete(entity_obj,sf,req) 修改之前作一些校验动作,返回提示信息
    def after_delete(entity_obj,sf,req)
    """

    def ref_pattern(cls):
        ObjectPool.datatable_provider[entity_name] = cls
        return cls

    return ref_pattern


def dataview_provider(view_name):
    """
    def count(default_search_val,http_req) -> return int
    def list(default_search_val,start,limit, http_req) -> return [dict,dict..],
            start,limit: query.order_by(entity.id.desc()).offset(display_start).limit(display_length)
    def add(http_req) -> ->last inserted id
    def view(id,http_req) -> return dict
    def modify(id,http_req) -> return err msg
    def delete(id,http_req) -> return err msg
    """

    def ref_pattern(cls):
        ObjectPool.dataview_provider[view_name] = cls
        return cls

    return ref_pattern


def setting(id_, tpl, title, security_point, postion=0, parent_id=None):
    """
    def save(kv,http_req) -> 用户处理设置保存
    def form_submit_javascript(http_req) -> 保存设置时表单数据提交前所要做的处理
    def form_fill_javascript(http_req) -> 设置加载时，自定义数据填充
    :param id_
    :param tpl: 模版路径
    :param title: Tab 名称
    :param security_point: 安全点,决定当前用户是否有权编辑
    :param postion: 位置排序
    :param parent_id: 父ID
    :return:
    """

    def ref_setting(cls):
        obj = EmptyClass()
        obj.id = id_
        obj.tpl = tpl
        obj.title = title
        obj.point = security_point
        obj.postion = postion
        obj.parent = parent_id
        obj.cls = cls
        ObjectPool.setting[id_] = obj
        return cls

    return ref_setting