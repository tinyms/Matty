__author__ = 'tinyms'

from sqlalchemy.engine import reflection
from tinyms.core.orm import SessionFactory
from tinyms.core.annotation import route, api
from tinyms.core.web import IAuthRequest
from tinyms.core.common import Utils


@route("/workbench/dev/project")
class ProjectController(IAuthRequest):
    def get(self, *args, **kwargs):
        return self.render("workbench/dev.project.html")


@route("/workbench/dev/widgets")
class WidgetsController(IAuthRequest):
    def get(self, *args, **kwargs):
        insp = reflection.Inspector.from_engine(SessionFactory.__engine__)
        context_data = dict()
        context_data["entity_map"] = Utils.encode(SessionFactory.entitys)
        table_cols = dict()
        table_cols_text = dict()
        for table_name in SessionFactory.entitys:
            cols_def = insp.get_columns(table_name)
            cols = list()
            for col_def in cols_def:
                cols.append(col_def["name"])
            table_cols[table_name] = cols
            table_cols_text[table_name] = Utils.encode(cols)
        context_data["table_cols"] = table_cols
        context_data["table_cols_text"] = table_cols_text
        return self.render("workbench/dev.widgets.html", context=context_data)


@route("/workbench/dev/entity")
class EntityController(IAuthRequest):
    def get(self, *args, **kwargs):
        return self.render("workbench/dev.entity.html")


@api("tinyms.dev.template")
class WidgetsTemplateApi():
    def get(self):
        tpl_datatable = """
        {% module DataTable(id="{{id}}",
            entity="{{entity_name}}",
            cols={{& cols}},
            titles={{& cols}},
            search_fields={{& cols}},
            search_tip="可搜索",
            autoform=False,
            point_list = "{{point_prefix}}.list",
            point_view = "{{point_prefix}}.view",
            point_add = "{{point_prefix}}.add",
            point_update = "{{point_prefix}}.update",
            point_delete = "{{point_prefix}}.delete"
            ) %}
          {% module panel_start("{{id}}") %}
          {% module datagrid_form_start("{{id}}") %}
            {{#fields}}
            <div class="form-group">
            <label for="start_date" class="col-lg-3 control-label">{{name}}</label>
            <div class="col-lg-8">
            <input type="text" class="form-control" id="{{name}}" name="{{name}}">
            </div>
            </div>
            {{/fields}}
          {% module datagrid_form_end("{{id}}","{{entity_name}}") %}
          {% module panel_end() %}
        """
        tpl_dataview = """
        {% module DataTable(id="{{id}}",
            view="{{view_name}}",
            cols={{& cols}},
            titles={{& cols}},
            search_tip="可搜索",
            autoform=False,
            point_list = "{{point_prefix}}.list",
            point_view = "{{point_prefix}}.view",
            point_add = "{{point_prefix}}.add",
            point_update = "{{point_prefix}}.update",
            point_delete = "{{point_prefix}}.delete"
            ) %}
          {% module panel_start("{{id}}") %}
          {% module datagrid_form_start("{{id}}") %}
            {{#fields}}
            <div class="form-group">
            <label for="start_date" class="col-lg-3 control-label">{{name}}</label>
            <div class="col-lg-8">
            <input type="text" class="form-control" id="{{name}}" name="{{name}}">
            </div>
            </div>
            {{/fields}}
          {% module datagrid_form_end("{{id}}","{{view_name}}", "view") %}
          {% module panel_end() %}
        """
        tpls = dict()
        tpls["datatable"] = tpl_datatable
        tpls["dataview"] = tpl_dataview
        return tpls