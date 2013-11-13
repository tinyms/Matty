__author__ = 'tinyms'

from sqlalchemy import Column, Integer, String, Text, LargeBinary, DateTime
from tinyms.core.orm import Simplify, Entity, many_to_one, many_to_many

#通知引擎处理节点
@many_to_one("BPMProcessInstance")
class BPMWorkflow(Entity, Simplify):
    node_id = Column(Integer(), nullable=False)
    #行为: 'execute','leave','execute-leave'
    behavior = Column(String(20))
    params = Column(Text())


#流程定义
class BPMProcessDef(Entity, Simplify):
    name = Column(String(100), nullable=False, unique=True)
    #Json格式或者类全名
    define = Column(Text(), nullable=False)
    #是否发布为可用流程，1是，0否
    release = Column(Integer(), default=0)
    #只有允许的人才可以使用此流程
    security_point = Column(String(60))


#流程实例
@many_to_one("BPMProcessDef")
@many_to_one("Archives")
class BPMProcessInstance(Entity, Simplify):
    #序列化
    bin = Column(LargeBinary(), nullable=False)
    #实例是否完成，1完成，0未完成
    finish = Column(Integer(), default=0)
    start_time = Column(DateTime(), nullable=False)
    end_time = Column(DateTime())


#流程实例值
@many_to_one("BPMProcessInstance")
class BPMProcessVars(Entity, Simplify):
    name = Column(String(255), nullable=False)
    val = Column(Text())


@many_to_one("BPMProcessInstance")
class BPMProcessInstanceNotify(Entity, Simplify):
    node_id = Column(Integer(), nullable=False)
    tip_content = Column(Text(), nullable=False)
    #wait,finish
    result = Column(String(20))

@many_to_one("BPMProcessInstance")
class BPMWorklist(Entity, Simplify):
    task_name = Column(String(255), nullable=False)
    forms = Column(Text(), nullable=False)
    #多少小时内过期，则流程自动结束
    valid_time_space = Column(Integer(), default=0)
    expired = Column(Integer(), default=0)
    create_time = Column(DateTime(), nullable=False)
    finish_time = Column(DateTime())
    #完成者 from Archives
    worker = Column(Integer())

@many_to_one("BPMWorklist")
@many_to_one("Archives")
class BPMWorklistAuth(Entity, Simplify):
    #是否允许编辑
    editable = Column(Integer(), nullable=False)

