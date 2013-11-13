__author__ = 'tinyms'

from inspect import isfunction
from tornado.util import import_object


class NodeType():
    End = "End"
    Action = "Action"
    Fork = "Fork"
    Join = "Join"
    Form = "Form"


class Node():
    def __init__(self, id_, name, parent_id, act=None, type_=None):
        self.id = id_
        self.name = name
        self.parent = parent_id
        self.action = act
        self.type = type_
        self.process_vars = dict()
        self.start = False
        self.current_user = 0
        self.to = None
        self.cc = None

    #执行节点
    def execute(self):
        pass

    #请求离开
    def leave(self):
        pass


class EndNode(Node):
    def __init__(self, id_, name, parent_id, act=None):
        Node.__init__(id_, name, parent_id, act, NodeType.End)

    def execute(self):
        if type(self.action) == str:
            obj = import_object(self.action)()
            if hasattr(obj, "execute"):
                obj.execute()


class ActionNode(Node):
    def __init__(self, id_, name, parent_id, act=None):
        Node.__init__(id_, name, parent_id, act, NodeType.Action)

    def execute(self):
        if type(self.action) == str:
            obj = import_object(self.action)()
            if hasattr(obj, "execute"):
                obj.execute()
        elif isfunction(self.action):
            self.action()


class ForkNode(Node):
    def __init__(self, id_, name, parent_id):
        Node.__init__(id_, name, parent_id, None, NodeType.Fork)
        #child id list
        self.children = list()


class JoinNode(Node):
    def __init__(self, id_, name, parent_id):
        Node.__init__(id_, name, parent_id, None, NodeType.Join)
        #签到的上一个节点
        self.signs = list()
        #parent id list
        self.parents = list()


class FormNode(ActionNode):
    def __init__(self, id_, name, parent_id, act=None):
        ActionNode.__init__(id_, name, parent_id, act, NodeType.Form)
        #表单集合,[{"title":"formName","path":"tpl_path"}..]
        self.forms = list()

    def execute(self):
        if type(self.action) == str:
            obj = import_object(self.action)()
            if hasattr(obj, "execute"):
                obj.execute()
                #do form

    #表单提交时，做数据校验
    def valid(self, http_req):
        obj = None
        if type(self.action) == str:
            obj = import_object(self.action)()
        if hasattr(obj, "valid"):
            return obj.valid()
        return ""

    def submit(self, http_req):
        pass