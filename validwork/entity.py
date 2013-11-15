__author__ = 'tinyms'

from sqlalchemy import Column, Integer, String, Text, DateTime, Date, Time
from tinyms.core.orm import Simplify, Entity, many_to_one, many_to_many


#考勤机管理
class ValidWorkMachine(Entity, Simplify):
    #机器序号
    sn = Column(String(20), nullable=False, unique=True)
    stamp = Column(Integer(), default=0)
    opstamp = Column(Integer(), default=0)
    photo_stamp = Column(Integer(), default=0)
    ip = Column(String(40))
    #机器名称，人为标识，通常为机器安置位置说明
    flag = Column(String(500))
    #最后连接时间
    last_connect_time = Column(DateTime(), nullable=False)

#指纹登记客户端密钥表
@many_to_one("Account")
class ValidWorkFingerTemplateKey(Entity, Simplify):
    ukey = Column(String(60), nullable=False)
    tpl = Column(Text(), nullable=False)

#下发到考勤机命令集合
@many_to_one("ValidWorkMachine")
class ValidWorkCommands(Entity, Simplify):
    sn = Column(String(20), nullable=False)
    cmd = Column(Text(), nullable=False)
    create_date = Column(DateTime(), nullable=False)
    #validworkmachine

#人员指纹模版库
@many_to_one("Archives")
class ValidWorkFingerTemplate(Entity, Simplify):
    card_no = Column(String(20))
    finger_index = Column(Integer(), nullable=False)
    tpl = Column(Text())
    #archives


#节日
class Holiday(Entity, Simplify):
    name = Column(String(30), nullable=False, unique=True)
    start_date = Column(Date(), nullable=False)
    end_date = Column(Date(), nullable=False)


#班次/时间段,几点~几点
class ValidWorkTimeBlock(Entity, Simplify):
    name = Column(String(30), nullable=False, unique=True)
    #开始时间
    start_time = Column(Time(), nullable=False)
    #结束时间
    end_time = Column(Time(), nullable=False)
    #正常上班打卡区间,早于开始时间
    normal_in_space = Column(Integer(), default=0)
    #正常下班打卡区间,迟于下班时间
    normal_out_space = Column(Integer(), default=0)
    #迟到区间,迟于开始时间
    late_space = Column(Integer(), default=0)
    #早退区间,早于结束时间
    leave_early_space = Column(Integer(), default=0)
    #validworkscheduletasks


#任务计划，方便班次分配
@many_to_many("Archives")
@many_to_many("ValidWorkTimeBlock")
class ValidWorkScheduleTask(Entity, Simplify):
    #名称
    name = Column(String(60), nullable=False, unique=True)
    #使用人群注解等，阐明此计划任务的用途
    usage_description = Column(Text())
    #validworktimeblocks
    #archives


#打卡登记
#Archives实体内可以引用 validworkcheckons
@many_to_one("Archives")
class ValidWorkCheckOn(Entity, Simplify):
    check_time = Column(DateTime())
    #正常上下班,迟到,早退,矿工
    status = Column(Integer(), default=-1)
    #有效范围，如果指纹没及时上传也可以正确更新用户状态
    valid_start_time = Column(DateTime(), nullable=False)
    valid_end_time = Column(DateTime(), nullable=False)
    time_block_id = Column(Integer(), nullable=False)
    task_id = Column(Integer(), nullable=False)
    #archives
