__author__ = 'tinyms'

from sqlalchemy import func
from tinyms.core.common import Utils
from tinyms.core.orm import SessionFactory
from tinyms.core.entity import Term, TermTaxonomy
from tinyms.dao.point import DynamicPointHelper


class CategoryHelper():
    def __init__(self, taxonomy="Org", tt_desc="组织/部门"):
        self.taxonomy = taxonomy
        self.dph = DynamicPointHelper("分类视图", tt_desc)

    def list(self):
        cnn = SessionFactory.new()
        items = cnn.query(TermTaxonomy).filter(TermTaxonomy.term.has(Term.name != "ROOT")).filter(
            TermTaxonomy.taxonomy == self.taxonomy).all()
        nodes = list()
        for item in items:
            node = dict()
            node["id"] = item.id
            node["pId"] = item.parent_id
            node["name"] = item.term.name
            nodes.append(node)
        return nodes

    def create_term(self, name):
        name_ = Utils.trim(name)
        cnn = SessionFactory.new()
        id = cnn.query(Term.id).filter(Term.name == name_).limit(1).scalar()
        if not id:
            term = Term()
            term.name = name_
            term.slug = name_
            cnn.add(term)
            cnn.commit()
            return term.id
        return id

    def update(self, id, name_, parent_id):
        term_id = self.create_term(name_)
        parent_path = self.get_path(parent_id)
        cnn = SessionFactory.new()
        tt = cnn.query(TermTaxonomy).filter(TermTaxonomy.id == id).limit(1).scalar()
        if tt:
            tt.term_id = term_id
            tt.parent_id = parent_id
            tt.path = "%s/%s" % (parent_path, tt.id)
            cnn.commit()
            if self.taxonomy == "Org":
                self.dph.update("tinyms.treeview.%s.%s" % (self.taxonomy, tt.id), name_)
            return "Success"
        else:
            return "Failure"

    def create(self, name_, parent_id=None):
        term_id = self.create_term(name_)
        parent_path = self.get_path(parent_id)
        cnn = SessionFactory.new()
        tt = TermTaxonomy()
        tt.parent_id = parent_id
        tt.term_id = term_id
        tt.taxonomy = self.taxonomy
        tt.object_count = 0
        tt.path = parent_path
        cnn.add(tt)
        cnn.commit()
        tt.path = "%s/%s" % (parent_path, tt.id)
        cnn.commit()
        if self.taxonomy == "Org":
            self.dph.add("tinyms.treeview.%s.%s" % (self.taxonomy, tt.id), name_)
        return tt.id

    def remove(self, id_):
        cnn = SessionFactory.new()
        node = cnn.query(TermTaxonomy).filter(TermTaxonomy.id == id_).filter(
            TermTaxonomy.term.has(Term.name != "ROOT")).limit(1).scalar()
        path = node.path
        cnn.query(TermTaxonomy).filter(TermTaxonomy.path.like(path+"%")).delete(synchronize_session="fetch")
        cnn.commit()
        if self.taxonomy == "Org":
            self.dph.delete("tinyms.treeview.%s.%s" % (self.taxonomy, id_))
        return "Success"

    def exists(self, name_):
        cnn = SessionFactory.new()
        num = cnn.query(func.count(TermTaxonomy.id)).filter(TermTaxonomy.term.has(name=Utils.trim(name_))) \
            .filter(TermTaxonomy.taxonomy == self.taxonomy) \
            .limit(1).scalar()
        if num > 0:
            return True
        return False

    def exists_other(self, id, name_):
        cnn = SessionFactory.new()
        num = cnn.query(func.count(TermTaxonomy.id)).filter(TermTaxonomy.id != id) \
            .filter(TermTaxonomy.term.has(name=Utils.trim(name_))) \
            .filter(TermTaxonomy.taxonomy == self.taxonomy) \
            .limit(1).scalar()
        if num > 0:
            return True
        return False


    def get_path(self, id):
        cnn = SessionFactory.new()
        path = cnn.query(TermTaxonomy.path).filter(TermTaxonomy.id == id).limit(1).scalar()
        if not path:
            return ""
        return path


    def get_name(self, id):
        cnn = SessionFactory.new()
        tt = cnn.query(TermTaxonomy).filter(TermTaxonomy.id == id).limit(1).scalar()
        if tt:
            return tt.term.name
        return ""


    def get_object_count(self, id):
        cnn = SessionFactory.new()
        object_count = cnn.query(TermTaxonomy.object_count).filter(TermTaxonomy.id == id).limit(1).scalar()
        return object_count


    def set_object_count(self, id, chang_num=0):
        cnn = SessionFactory.new()
        tt = cnn.query(TermTaxonomy).filter(TermTaxonomy.id == id).limit(1).scalar()
        if tt:
            tt.object_count += chang_num
            cnn.commit()
            return True
        return False
