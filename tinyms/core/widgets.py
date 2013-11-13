__author__ = 'tinyms'

import json
from tornado.web import UIModule
from tornado.util import import_object
from sqlalchemy import func
from tinyms.core.common import Utils, JsonEncoder
from tinyms.core.annotation import ui, route, ObjectPool, EmptyClass
from tinyms.core.orm import SessionFactory
from tinyms.core.web import IRequest
from tinyms.core.entity import Term, TermTaxonomy, Role
from tinyms.dao.account import AccountHelper


class IWidget(UIModule):
    pass


@ui("Version")
class VersionModule(IWidget):
    def render(self, *args, **kwargs):
        return "&copy; ArchX 2013, v1.0b"


@ui("CurrentAccountName")
class CurrentAccountName(IWidget):
    def render(self):
        return AccountHelper.name(self.current_user)


@ui("SideBar")
class SideBar(IWidget):
    archives_show = False
    role_org_show = False
    sys_params_show = False

    def render(self):
        points = list(AccountHelper.points(self.current_user))
        if points.count("tinyms.sidebar.archives.show"):
            self.archives_show = True
        if points.count("tinyms.sidebar.role_org.show"):
            self.role_org_show = True
        if points.count("tinyms.sidebar.sys_params.show"):
            self.sys_params_show = True
        custom_menus = ObjectPool.sidebar_menus
        first_levels = list()
        for menu in custom_menus:
            if menu[1].count("/") == 1:
                first_levels.append(menu)
        html_builder = list()
        self.sort_menus(first_levels)
        for first in first_levels:
            if first[4] and points.count(first[4]) == 0:
                continue
            p = '<a href="' + first[2] + '"><i class="' + first[5] + ' icon-xlarge"></i><span>' + first[
                3] + '</span></a>'
            subs = self.children(first[1])
            if len(subs) > 0:
                html_builder.append('<li class="dropdown-submenu">')
                html_builder.append(p)
                html_builder.append('<ul class="dropdown-menu">')
                self.sort_menus(subs)
                for sub in subs:
                    if sub[4] and points.count(sub[4]) == 0:
                        continue
                    html_builder.append('<li><a href="' + sub[2] + '">' + sub[3] + '</a></li>')
                    pass
                html_builder.append('</ul>')
                html_builder.append('</li>')
            else:
                html_builder.append("<li>" + p + "</li>")
        menu_html = "".join(html_builder)
        context = dict()
        context["menu"] = menu_html
        context["archives_show"] = self.archives_show
        context["role_org_show"] = self.role_org_show
        context["sys_params_show"] = self.sys_params_show
        return self.render_string("workbench/sidebar.html", context=context)

    def children(self, path):
        subs = list()
        for menu in ObjectPool.sidebar_menus:
            if menu[1].startswith(path + "/"):
                subs.append(menu)
        return subs

    def sort_menus(self, items):
        items.sort(key=lambda x: x[0])

@ui("DataComboBox")
class DataComboBoxModule(IWidget):
    def render(self, **prop):
        self.dom_id = prop.get("id")
        self.cols = prop.get("cols")
        self.sort_sql = prop.get("sort_sql")
        self.entity_full_name = prop.get("entity")
        self.query_class = prop.get("query_class") # obj prop `data` func return [(k,v),(k,v)...]
        self.allow_blank = prop.get("allow_blank")
        html = list()
        html.append("<select id='%s' name='%s' class='form-control'>" % (self.dom_id, self.dom_id))
        if self.allow_blank:
            html.append("<option value=''> </option>")
        if not self.query_class:
            if not self.entity_full_name:
                return "<small>Require entity full name.</small>"
            if self.entity_full_name:
                cls = import_object(self.entity_full_name)
                cnn = SessionFactory.new()
                q = cnn.query(cls)
                if self.sort_sql:
                    q = q.order_by(self.sort_sql)
                items = q.all()
                all = list()
                for item in items:
                    all.append([(getattr(item, col)) for col in self.cols.split(",")])
                for opt in all:
                    html.append("<option value='%s'>%s</option>" % (opt[0], opt[1]))
        else:
            obj = import_object(self.query_class)()
            if hasattr(obj, "data"):
                items = getattr(obj, "data")()
                for item in items:
                    html.append("<option value='%s'>%s</option>" % (item[0], item[1]))
        html.append("</select>")
        return "".join(html)


@ui("RoleComboBox")
class RoleListComboBox(IWidget):
    def render(self, **prop):
        dom_id = prop.get("id")
        allow_blank = prop.get("allow_blank")
        html = list()
        html.append("<select id='%s' name='%s'>" % (dom_id, dom_id))
        if allow_blank:
            html.append("<option value=''> </option>")
        sf = SessionFactory.new()
        ds = sf.query(Role).filter(Role.name != "SuperAdmin").all()
        for row in ds:
            label = "%s(%s)" % (row.name, row.description)
            html.append("<option value='%s'>%s</option>" % (row.id, label))
        html.append("</select>")
        return "".join(html)


class DataTableBaseModule(IWidget):
    def javascript_files(self):
        items = list()
        items.append("/static/jslib/datatable/js/jquery.dataTables.1.9.4.modified.js")
        #items.append("/static/jslib/datatable/extras/tabletools/js/ZeroClipboard.js")
        #items.append("/static/jslib/datatable/extras/tabletools/js/TableTools.min.js")
        items.append("/static/jslib/tinyms.datatable.js")
        return items

    def css_files(self):
        items = list();
        #items.append("/static/jslib/datatable/css/jquery.dataTables.css")
        #items.append("/static/jslib/datatable/extras/tabletools/css/TableTools.css")
        return items

    def embedded_css(self):
        return ".datatable_col_sel{width:20px;}"


@ui("DataTable")
class DataTableModule(DataTableBaseModule):
    __entity_mapping__ = dict()
    __default_search_fields__ = dict()
    __security_points__ = dict()

    def render(self, **prop):
        self.dom_id = prop.get("id")#client dom id
        self.cols = prop.get("cols")#entity field list
        self.titles = prop.get("titles")#title list
        self.entity_full_name = prop.get("entity")#entity name
        autoform = prop.get("autoform")
        checkable = prop.get("checkable")
        toolbar_add = prop.get("toolbar_add")
        search_fields = prop.get("search_fields")#default search field name,and text type,
        search_tip = prop.get("search_tip")
        point = EmptyClass()
        point.list = prop.get("point_list")
        point.view = prop.get("point_view")
        point.add = prop.get("point_add")
        point.update = prop.get("point_update")
        point.delete = prop.get("point_delete")

        if not self.entity_full_name:
            return "Require entity full name."
        self.datatable_key = Utils.md5(self.entity_full_name)
        DataTableModule.__security_points__[self.datatable_key] = point
        if search_fields:
            DataTableModule.__default_search_fields__[self.datatable_key] = search_fields
        else:
            DataTableModule.__default_search_fields__[self.datatable_key] = []
        sub = dict()
        sub["name"] = self.entity_full_name
        sub["cols"] = self.cols
        DataTableModule.__entity_mapping__[self.datatable_key] = sub

        tag = ""
        if checkable:
            tag += "<th><input type='checkbox' style='width: 13px; height: 13px;' onclick='%s_.CheckAll(this);'/></th>" % self.dom_id
        for title in self.titles:
            tag += "<th>" + title + "</th>"
        tag += "<th>#</th>"

        opt = dict()
        opt["point"] = point
        opt["id"] = self.dom_id
        opt["autoform"] = autoform
        opt["checkable"] = checkable
        if not search_tip:
            search_tip = ""
        opt["search_tip"] = search_tip
        opt["thTags"] = tag
        opt["entity_name_md5"] = self.datatable_key
        if autoform:
            opt["cols"] = self.create_editform()
        html_col = list()

        index = 0
        for col in self.cols:
            html_col.append(
                {"mData": col, "sTitle": self.titles[index], "sClass": "datatable_column_" + col,
                 "sDefaultContent": ""})
            index += 1

        opt["col_defs"] = json.dumps(html_col)
        self.create_editform()
        return self.render_string("widgets/datatable_html.html", opt=opt)

    def create_editform(self):
        obj = import_object(self.entity_full_name)()
        metas = obj.cols_meta()
        col_defs = list()
        for meta in metas:
            if meta["name"] == "id":
                continue
            col_def = dict()
            col_def["name"] = meta["name"]
            col_def["type"] = ""
            col_def["required"] = ""
            if meta["length"] > 0:
                col_def["length"] = 'maxlength="%s"' % meta["length"]
            else:
                col_def["length"] = ''
            if not meta["nullable"]:
                col_def["required"] = "required"
            if meta["type"] == "int":
                col_def["type"] = "digits"
            elif meta["type"] == "numeric":
                col_def["type"] = "number"
            elif meta["type"] == "date":
                col_def["type"] = "date"
            col_defs.append(col_def)
        return col_defs


@route(r"/datatable/(.*)/(.*)")
class DataTableHandler(IRequest):
    def post(self, id_, act):
        point = DataTableModule.__security_points__.get(id_)
        message = dict()
        if act == "list":
            if not self.auth({point.list}):
                self.write(dict())
            else:
                self.list(id_)
        elif act == "save":
            if not self.auth({point.update}):
                message["success"] = False
                message["msg"] = "UnAuth"
                self.write(json.dumps(message))
            else:
                self.update(id_)
        elif act == "saveNext":
            if not self.auth({point.update}):
                message["success"] = False
                message["msg"] = "UnAuth"
                self.write(json.dumps(message))
            else:
                self.update(id_)
        elif act == "delete":
            if not self.auth({point.delete}):
                message["success"] = False
                message["msg"] = "UnAuth"
                self.write(json.dumps(message))
            else:
                self.delete(id_)

    def delete(self, id_):
        self.set_header("Content-Type", "text/json;charset=utf-8")
        meta = DataTableModule.__entity_mapping__.get(id_)
        if not meta:
            self.set_status(403, "Error!")
        entity = import_object(meta["name"])
        custom_filter = ObjectPool.datatable_provider.get(meta["name"])
        custom_filter_obj = None
        if custom_filter:
            custom_filter_obj = custom_filter()
        valid_msg = ""
        message = dict()
        message["flag"] = "delete"
        rec_id = self.get_argument("id")
        sf = SessionFactory.new()
        cur_row = sf.query(entity).get(rec_id)
        if hasattr(custom_filter_obj, "before_delete"):
            valid_msg = custom_filter_obj.before_delete(cur_row, sf, self)
        if not valid_msg:
            sf.delete(cur_row)
            sf.commit()
            if hasattr(custom_filter_obj, "after_delete"):
                custom_filter_obj.after_delete(cur_row, sf, self)
            message["success"] = True
            message["msg"] = "Deleted"
            self.write(json.dumps(message))
        else:
            message["success"] = False
            message["msg"] = valid_msg
            self.write(json.dumps(message))

    def update(self, id_):
        message = dict()
        self.set_header("Content-Type", "text/json;charset=utf-8")
        meta = DataTableModule.__entity_mapping__.get(id_)
        if not meta:
            self.set_status(403, "Error!")
        entity = import_object(meta["name"])
        custom_filter = ObjectPool.datatable_provider.get(meta["name"])
        custom_filter_obj = None
        if custom_filter:
            custom_filter_obj = custom_filter()
        rec_id = self.get_argument("id")
        valid_msg = ""
        if not rec_id:
            message["flag"] = "add"
            sf = SessionFactory.new()
            obj = self.wrap_entity(entity())
            if hasattr(custom_filter_obj, "before_add"):
                valid_msg = custom_filter_obj.before_add(obj, sf, self)
                #检查没有数据上的问题才执行保存动作
            if not valid_msg:
                sf.add(obj)
                sf.commit()
                if hasattr(custom_filter_obj, "after_add"):
                    custom_filter_obj.after_add(obj, sf, self)
                message["success"] = True
                message["msg"] = obj.id
                self.write(json.dumps(message))
            else:
                message["success"] = False
                message["msg"] = valid_msg
                self.write(json.dumps(message))
        else:
            message["flag"] = "update"
            sf = SessionFactory.new()
            cur_row = sf.query(entity).get(rec_id)
            self.wrap_entity(cur_row)
            if hasattr(custom_filter_obj, "before_modify"):
                valid_msg = custom_filter_obj.before_modify(cur_row, sf, self)
            if not valid_msg:
                sf.commit()
                if hasattr(custom_filter_obj, "after_modify"):
                    custom_filter_obj.after_modify(cur_row, sf, self)
                message["success"] = True
                message["msg"] = "Updated"
                self.write(json.dumps(message))
            else:
                message["success"] = False
                message["msg"] = valid_msg
                self.write(json.dumps(message))

    def list(self, id_):
        meta = DataTableModule.__entity_mapping__.get(id_)
        if not meta:
            self.set_status(403, "Error!")
        entity = import_object(meta["name"])
        self.datatable_display_cols = meta["cols"]
        self.set_header("Content-Type", "text/json;charset=utf-8")
        display_start = Utils.parse_int(self.get_argument("iDisplayStart"))
        display_length = Utils.parse_int(self.get_argument("iDisplayLength"))
        #cols_num = self.get_argument("iColumns")

        #全局搜索处理段落
        default_search_value = self.get_argument("sSearch")
        default_search_fields = DataTableModule.__default_search_fields__.get(id_)
        default_search_sqlwhere = ""
        default_search_sqlwhere_params = dict()
        if default_search_value and default_search_fields:
            temp_sql = list()
            for field_name in default_search_fields:
                temp_sql.append("%s like :%s" % (field_name, field_name))
                default_search_sqlwhere_params[field_name] = "%" + default_search_value + "%"
            default_search_sqlwhere = " OR ".join(temp_sql)

        #排序处理段落
        sort_params = self.parse_sort_params()
        order_sqlwhere = ""
        for k, v in sort_params.items():
            order_sqlwhere += "1=1 ORDER BY %s %s" % (k, v)
            break

        #DataGrid数据查询段落
        cnn = SessionFactory.new()
        #here place custom filter
        total_query = cnn.query(func.count(1)).select_from(entity)
        ds_query = cnn.query(entity)

        custom_filter = ObjectPool.datatable_provider.get(meta["name"])
        if custom_filter:
            custom_filter_obj = custom_filter()
            if hasattr(custom_filter_obj, "total"):
                total_query = custom_filter_obj.total(total_query, self)
            if hasattr(custom_filter_obj, "dataset"):
                ds_query = custom_filter_obj.dataset(ds_query, self)

        if default_search_value:
            total_query = total_query.filter(default_search_sqlwhere).params(**default_search_sqlwhere_params)
            ds_query = ds_query.filter(default_search_sqlwhere).params(**default_search_sqlwhere_params)

        if order_sqlwhere:
            ds_query = ds_query.filter(order_sqlwhere)
        total = total_query.scalar()
        ds = ds_query.offset(display_start).limit(display_length)

        results = dict()
        results["sEcho"] = self.get_argument("sEcho")
        results["iTotalRecords"] = total
        results["iTotalDisplayRecords"] = total
        results["aaData"] = [item.dict() for item in ds]
        self.write(json.dumps(results, cls=JsonEncoder))

    def parse_sort_params(self):
        params = dict()
        col_index = Utils.parse_int(self.get_argument("iSortCol_0"))
        direct = self.get_argument("sSortDir_0")
        params[self.datatable_display_cols[col_index]] = direct
        return params


@ui("DataView")
class DataViewModule(DataTableBaseModule):
    __view_mapping__ = dict()
    __security_points__ = dict()

    def render(self, **prop):
        self.dom_id = prop.get("id")#client dom id
        self.cols = prop.get("cols")#entity field list
        self.titles = prop.get("titles")#title list
        self.dataview_name = prop.get("view")#仅仅只是一个Key，不做他用,全站唯一
        checkable = prop.get("checkable")
        search_tip = prop.get("search_tip")
        select_mode = prop.get("select_mode")
        self.point = EmptyClass()
        self.point.list = prop.get("point_list")
        self.point.view = prop.get("point_view")
        self.point.add = prop.get("point_add")
        self.point.update = prop.get("point_update")
        self.point.delete = prop.get("point_delete")

        if not self.dataview_name:
            return "Require data view name."

        self.dataview_key = Utils.md5(self.dataview_name)
        DataViewModule.__view_mapping__[self.dataview_key] = self.dataview_name
        DataViewModule.__security_points__[self.dataview_key] = self.point

        tag = ""
        if checkable:
            tag += "<th><input type='checkbox' style='width: 13px; height: 13px;' onclick='%s_.CheckAll(this);'/></th>" % self.dom_id
        for title in self.titles:
            tag += "<th>" + title + "</th>"
        tag += "<th>#</th>"

        opt = dict()
        opt["cols"] = self.cols
        opt["autoform"] = prop.get("autoform")
        opt["point"] = self.point
        opt["id"] = self.dom_id
        opt["thTags"] = tag
        opt["select_mode"] = select_mode
        opt["entity_name_md5"] = self.dataview_key
        opt["checkable"] = checkable
        if not search_tip:
            search_tip = ""
        opt["search_tip"] = search_tip

        html_col = list()

        index = 0
        for col in self.cols:
            html_col.append(
                {"mData": col, "sTitle": self.titles[index], "sClass": "datatable_column_" + col,
                 "sDefaultContent": ""})
            index += 1

        opt["col_defs"] = json.dumps(html_col)
        return self.render_string("widgets/dataview_html.html", opt=opt)


@route(r"/dataview/(.*)/(.*)")
class DataViewHandler(IRequest):
    def post(self, id_, act):
        point = DataViewModule.__security_points__.get(id_)
        message = dict()
        if act == "list":
            if not self.auth({point.list}):
                self.write(dict())
            else:
                self.list(id_)
        elif act == "save":
            if not self.auth({point.update}):
                message["success"] = False
                message["msg"] = "UnAuth"
                self.write(json.dumps(message))
            else:
                self.update(id_)
        elif act == "saveNext":
            if not self.auth({point.update}):
                message["success"] = False
                message["msg"] = "UnAuth"
                self.write(json.dumps(message))
            else:
                self.update(id_)
        elif act == "delete":
            if not self.auth({point.delete}):
                message["success"] = False
                message["msg"] = "UnAuth"
                self.write(json.dumps(message))
            else:
                self.delete(id_)

    def delete(self, id):
        self.set_header("Content-Type", "text/json;charset=utf-8")
        name = DataViewModule.__view_mapping__.get(id)
        if not name:
            self.set_status(403, "Error!")
        message = dict()
        message["flag"] = "delete"
        message["success"] = False
        message["msg"] = "Miss DataProvider!"
        rec_id = self.get_argument("id")
        custom_filter = ObjectPool.dataview_provider.get(name)
        if custom_filter:
            custom_filter_obj = custom_filter()
            if hasattr(custom_filter_obj, "delete"):
                msg = custom_filter_obj.delete(rec_id, self)
                if msg:
                    message["success"] = False
                    message["msg"] = msg
                else:
                    message["success"] = True
                    message["msg"] = "Deleted"
        self.write(json.dumps(message))

    def update(self, id_):
        message = dict()
        message["success"] = False
        message["msg"] = "Miss DataProvider!"
        self.set_header("Content-Type", "text/json;charset=utf-8")
        name = DataViewModule.__view_mapping__.get(id_)
        if not name:
            self.set_status(403, "Error!")
        custom_data_provider = ObjectPool.dataview_provider.get(name)
        obj = None
        if custom_data_provider:
            obj = custom_data_provider()
        rec_id = self.get_argument("id")
        if not rec_id:
            message["flag"] = "add"
            if hasattr(obj, "add"):
                msg = obj.add(self)
                if type(msg) == int:
                    message["success"] = True
                    message["msg"] = msg
                else:
                    message["success"] = False
                    message["msg"] = msg
        else:
            message["flag"] = "update"
            if hasattr(obj, "modify"):
                msg = obj.modify(rec_id, self)
                if msg:
                    message["success"] = False
                    message["msg"] = msg
                else:
                    message["success"] = True
                    message["msg"] = "Updated"

        self.write(json.dumps(message))

    def list(self, id_):
        name = DataViewModule.__view_mapping__.get(id_)
        if not name:
            self.set_status(403, "Error!")

        self.set_header("Content-Type", "text/json;charset=utf-8")
        display_start = Utils.parse_int(self.get_argument("iDisplayStart"))
        display_length = Utils.parse_int(self.get_argument("iDisplayLength"))

        total = 0
        ds = list()

        custom_data_provider = ObjectPool.dataview_provider.get(name)
        if custom_data_provider:
            default_search_value = self.get_argument("sSearch")
            obj = custom_data_provider()
            if hasattr(obj, "count"):
                total = obj.count(default_search_value, self)
            if hasattr(obj, "list"):
                ds = obj.list(default_search_value, display_start, display_length, self)

        results = dict()
        results["sEcho"] = self.get_argument("sEcho")
        results["iTotalRecords"] = total
        results["iTotalDisplayRecords"] = total
        results["aaData"] = ds

        self.write(json.dumps(results, cls=JsonEncoder))


@ui("panel_start")
class PanelStart(IWidget):
    def render(self, id_, css_cls="panel-body"):
        return '<div id="%s_panel" class="%s">' % (id_, css_cls)


@ui("panel_end")
class PanelEnd(IWidget):
    def render(self):
        return '</div>'


@ui("form_start")
class FormStart(IWidget):
    def render(self, id_, css_cls="form-horizontal"):
        return '<form class="%s" role="form" id="%s_form"><input type="hidden" name="id" id="id"/>' % (css_cls, id_)


@ui("form_end")
class FormEnd(IWidget):
    def render(self):
        return '</form>'


@ui("datagrid_form_start")
class DataGridFormStart(IWidget):
    def render(self, id_, css_cls="form-horizontal"):
        html = list()
        html.append(
            '<form class="%s" role="form" id="%s_form"><input type="hidden" name="id" id="id"/>' % (css_cls, id_))
        html.append('<div class="form-group"><div class="col-lg-9 col-lg-offset-3">')
        html.append(
            '<input type="button" class="btn btn-white btn-sm " id="%s_form_return"  onclick="%s_.form.cancel(this);" value="返回"/>' % (
                id_, id_))
        html.append('</div></div>')
        return "".join(html)


@ui("datagrid_form_end")
class DataGridFormEnd(IWidget):
    def render(self, id_, target, type_="table"):
        """
        :param id_: dom id
        :param target: DataTable's entity property Or DataView's view property value
        :param type_: 'table' or 'view'
        :return:
        """
        key = Utils.md5(target)
        point = None
        if type_ == "table":
            point = DataTableModule.__security_points__.get(key)
        elif type_ == "view":
            point = DataViewModule.__security_points__.get(key)
        html = list()
        if AccountHelper.auth(self.current_user, {point.add, point.update, point.delete}):
            html.append('<div class="form-group"><div class="col-lg-9 col-lg-offset-3">')
            html.append(
                '<input type="button" class="btn btn-primary btn-sm" id="%s_form_save" onclick="%s_.form.save(this,%s);" value="保存"></button>' % (
                    id_, id_, "''"))
            html.append(
                ' <input type="button" class="btn btn-white btn-sm" id="%s_form_save_continue" onclick="%s_.form.save(this,%s);" value="保存并继续"></button>' % (
                    id_, id_, "'clear'"))
            html.append(
                ' <input type="button" class="btn btn-white btn-sm" id="%s_form_reset" onclick="%s_.form.reset(this);" value="重填"></button>' % (
                    id_, id_))
            html.append('</div></div>')
        html.append('</form>')
        return "".join(html)

#可以编辑树节点的控件
@ui("TermTaxonomyEditor")
class TermTaxonomyEditor(IWidget):
    def render(self, **p):
        opt = dict()
        dom_id = p["id"]
        placeholder = p["placeholder"]
        opt["taxonomy"] = p["taxonomy"]
        self.point = EmptyClass()
        self.point.list = p.get("point_list")
        self.point.add = p.get("point_add")
        self.point.update = p.get("point_update")
        self.point.delete = p.get("point_delete")
        if not self.point.list:
            self.point.list = "tinyms.view.termtaxonomy.list"
        if not self.point.add:
            self.point.add = "tinyms.view.termtaxonomy.add"
        if not self.point.update:
            self.point.update = "tinyms.view.termtaxonomy.update"
        if not self.point.delete:
            self.point.delete = "tinyms.view.termtaxonomy.delete"
        opt["point"] = self.point
        ObjectPool.treeview[opt["taxonomy"]] = self.point
        if AccountHelper.auth(self.current_user, {self.point.list}):
            return self.render_string("widgets/orgtree.html", id=dom_id, ph=placeholder, opt=opt)
        return ""

    def css_files(self):
        items = list()
        items.append("/static/jslib/ztree/zTreeStyle.css")
        return items

    def javascript_files(self):
        items = list()
        items.append("/static/jslib/ztree/jquery.ztree.core-3.5.min.js")
        items.append("/static/jslib/ztree/jquery.ztree.exedit-3.5.min.js")
        items.append("/static/jslib/ztree/jquery.ztree.excheck-3.5.min.js")
        items.append("/ajax/OrgEdit.js")
        return items

    def embedded_css(self):
        return ".ztree li span.button.add {margin-left:2px; margin-right: -1px; background-position:-144px 0; vertical-align:top; *vertical-align:middle}"


@ui("TermTaxonomyComboBox")
class TermTaxonomyComboBox(IWidget):
    def render(self, **prop):
        dom_id = prop["id"]
        items = self.list(prop["taxonomy"])
        allowed_blank = prop.get("allowed_blank")
        html = list()
        html.append("<select id='%s' name='%s' class='form-control'>" % (dom_id, dom_id))
        if allowed_blank:
            html.append("<option value=''> </option>")
        for item in items:
            html.append("<option value='%i'>%s</option>" % (item[0], item[1]))
        html.append("</select>")
        return "".join(html)

    def list(self, taxonomy):
        cnn = SessionFactory.new()
        items = cnn.query(TermTaxonomy.id, Term.name) \
            .outerjoin((Term, Term.id == TermTaxonomy.term_id)) \
            .filter(TermTaxonomy.taxonomy == taxonomy) \
            .all()
        return items


@ui("TermTaxonomyJavascript")
class TermTaxonomyJavascript(TermTaxonomyComboBox):
    def render(self, **prop):
        #Javascript 变量名称
        name = prop.get("name")
        taxonomy = prop.get("taxonomy")
        data = self.list(taxonomy)
        js = "var %s = " % name
        map_ = dict()
        for item in data:
            map_[item[0]] = item[1]
        js += json.dumps(map_)
        return js


#分类选择器,单选、多选
@ui("TreeComboBox")
class TreeComboBox(TermTaxonomyEditor):
    def render(self, **prop):
        dom_id = prop["id"]
        opt = dict()
        opt["taxonomy"] = prop["taxonomy"]
        placeholder = prop.get("placeholder")
        self.point = ObjectPool.treeview.get(opt["taxonomy"])
        if not self.point:
            self.point = EmptyClass()
            self.point.list = prop.get("point_list")
            ObjectPool.treeview[opt["taxonomy"]] = self.point
        if AccountHelper.auth(self.current_user, {self.point.list}):
            return self.render_string("widgets/treecombobox.html", id=dom_id, ph=placeholder, opt=opt)
        return ""


@ui("AutoComplete")
class AutoComplete(IWidget):
    def render(self, **p):
        self.dom_id = p.get("id") #dom id
        self.provider = p.get("provider") #datasource json url
        self.key = Utils.md5(self.provider)
        self.placeholder = p.get("placeholder") #tip
        self.at = p.get("at")
        if not self.at:
            self.at = ""
        self.item_tpl = "<li data-value='${value}' data-key='${key}'>${value}</li>"
        item_tpl = p.get("item_tpl")
        if item_tpl:
            self.item_tpl = item_tpl
        return self.render_string("widgets/autocomplete.html", id=self.dom_id, key=self.key, item_tpl=self.item_tpl,
                                  at=self.at, placeholder=self.placeholder)

    def javascript_files(self):
        files = list()
        files.append("/static/jslib/autocomplete/js/jquery.atwho.min.js")
        return files

    def css_files(self):
        files = list()
        files.append("/static/jslib/autocomplete/css/jquery.atwho.css")
        return files

    def embedded_javascript(self):
        return self.render_string("widgets/autocomplete.js")