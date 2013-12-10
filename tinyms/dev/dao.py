__author__ = 'tinyms'

import os
from tinyms.core.annotation import ObjectPool, api
from tinyms.core.common import Utils


@api("com.tinyms.dev.project")
class ProjectApi():
    def create(self):
        if not ObjectPool.mode_dev:
            return ["failure"]
        name = self.param("name")
        if not name:
            return ["failure"]
        abs_path = self.request.get_webroot_path()
        tpl_path = abs_path + "templates/" + name + "/"
        Utils.mkdirs(tpl_path)
        page_html_file = tpl_path + "/page.html"
        if not os.path.exists(page_html_file):
            Utils.text_write(page_html_file, ProjectApi.create_page_template())
        Utils.mkdirs(abs_path + name)
        #create __init__.py
        items = list()
        pack_file = abs_path + name + "/__init__.py"
        if not os.path.exists(pack_file):
            items.append("from %s.entity import *" % name)
            items.append("from %s.controller import *" % name)
            items.append("from %s.dao import *" % name)
            items.append("from %s.common import *" % name)
            Utils.text_write(pack_file, items)
            #create sample py, example: controller.py, dao.py, common.py, entity.py
        items.clear()
        controller_file = abs_path + name + "/controller.py"
        if not os.path.exists(controller_file):
            items.append("from tinyms.core.common import Utils")
            items.append("from tinyms.core.web import IAuthRequest")
            items.append("from tinyms.core.annotation import route, ui")
            Utils.text_write(controller_file, items)
        items.clear()
        dao_file = abs_path + name + "/dao.py"
        if not os.path.exists(dao_file):
            items.append("from tinyms.core.common import Utils")
            items.append("from sqlalchemy import func, or_, cast")
            items.append("from tinyms.core.orm import SessionFactory")
            pkg = "from tinyms.core.annotation import autocomplete, datatable_provider, dataview_provider, ajax, api"
            items.append(pkg)
            Utils.text_write(dao_file, items)
        items.clear()
        common_file = abs_path + name + "/common.py"
        if not os.path.exists(common_file):
            items.append("from tinyms.core.common import Utils")
            items.append("from tinyms.core.annotation import reg_point, points, setting, server_starup")
            Utils.text_write(common_file, items)
        items.clear()
        entity_file = abs_path + name + "/entity.py"
        if not os.path.exists(entity_file):
            a = "from sqlalchemy import Column, Integer, String, DateTime, Text, Date, Numeric"
            b = "from tinyms.core.orm import Entity, Simplify, many_to_one, many_to_many"
            items.append(a)
            items.append(b)
            Utils.text_write(entity_file, items)
        return ["success"]

    @staticmethod
    def create_page_template():
        tpl = """
        {% extends "../master.html" %}
            {% block title %}Title{% end %}
            {% block header %}
            {% end %}
            {% block workspace %}
            <section class="main padder">
                <div class="clearfix">
                    <h4><i class="icon-reorder"></i>Title</h4>
                </div>
                <div class="row">
                    <div class="col-lg-12">
                    </div>
                </div>
            </section>
            {% end %}
        """
        return tpl