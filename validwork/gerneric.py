__author__ = 'tinyms'

from datetime import datetime, timedelta
import threading

from sqlalchemy import func, or_, cast

from tinyms.core.annotation import points, reg_point
from tinyms.core.common import Utils
from tinyms.core.orm import SessionFactory
from validwork.entity import *
from tinyms.core.entity import Archives


class ValidWorkHelper():
    __scheduler__ = None

    @staticmethod
    def start_scheduler():
        ValidWorkHelper.__scheduler__ = ValidWorkSchedulerThread()
        ValidWorkHelper.__scheduler__.start()

    @staticmethod
    def push_command_to_machine(sn, cmd):
        sf = SessionFactory.new()
        id_ = sf.query(ValidWorkCommands.id).filter(ValidWorkCommands.sn == sn).limit(1).scalar()
        vwc = ValidWorkCommands()
        vwc.sn = sn
        vwc.validworkmachine_id = id_
        vwc.cmd = cmd
        vwc.create_date = Utils.current_datetime()
        sf.add(vwc)
        sf.commit()

    @staticmethod
    def push_user_fp_to_machine(sn, pin, name, fid, tpl):
        create = r"DATA DEL_USER PIN=%i\r\nDATA USER PIN=%i\tName=%s\r\n" % (pin, pin, name)
        update = r"DATA FP PIN=%i\tFID=%i\tTMP=%s\r\n" % (pin, fid, tpl)
        sf = SessionFactory.new()
        id_ = sf.query(ValidWorkCommands.id).filter(ValidWorkCommands.sn == sn).limit(1).scalar()
        vwc = ValidWorkCommands()
        vwc.sn = sn
        vwc.validworkmachine_id = id_
        vwc.cmd = create
        vwc.create_date = Utils.current_datetime()
        vwc1 = ValidWorkCommands()
        vwc1.sn = sn
        vwc1.validworkmachine_id = id_
        vwc1.cmd = update
        vwc1.create_date = Utils.current_datetime()
        sf.add_all([vwc, vwc1])
        sf.commit()

    @staticmethod
    def push_users_fp_to_machine(sn, items):
        """

        @param sn:
        @param items: [[pin, name, fid, tpl]..]
        """
        sf = SessionFactory.new()
        id_ = sf.query(ValidWorkCommands.id).filter(ValidWorkCommands.sn == sn).limit(1).scalar()
        cmds = list()
        for item in items:
            create = r"DATA DEL_USER PIN=%i\r\nDATA USER PIN=%i\tName=%s\r\n" % (item[0], item[0], item[1])
            update = r"DATA FP PIN=%i\tFID=%i\tTMP=%s\r\n" % (item[0], item[2], item[3])
            vwc = ValidWorkCommands()
            vwc.sn = sn
            vwc.validworkmachine_id = id_
            vwc.cmd = create
            vwc.create_date = Utils.current_datetime()
            vwc1 = ValidWorkCommands()
            vwc1.sn = sn
            vwc1.validworkmachine_id = id_
            vwc1.cmd = update
            vwc1.create_date = Utils.current_datetime()
            cmds += [vwc, vwc1]
        sf.add_all(cmds)
        sf.commit()


#定时任务线程
class ValidWorkSchedulerThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        import time

        while True:
            ValidWorkSchedulerThread.organization_of_work()
            time.sleep(60 * 5)

    #线程后台定时运动，休眠5分钟
    @staticmethod
    def organization_of_work():
        current_datetime = Utils.current_datetime()
        sf = SessionFactory.new()
        #标识-1的状态为旷工，这种情况是没有按指纹的，CheckOn 有效时间段结束时间已经过期的时候
        updates = sf.query(ValidWorkCheckOn) \
            .filter(or_(ValidWorkCheckOn.status_in == -1, ValidWorkCheckOn.status_out == -1)) \
            .filter(ValidWorkCheckOn.valid_end_time < current_datetime).all()
        for row in updates:
            row.status_no_sign = 1
        sf.commit()
        #列出所有考勤计划
        tasks = sf.query(ValidWorkScheduleTask.id).all()
        tasks = [task[0] for task in tasks]
        for task_id in tasks:
        #得到班次最小的时间点
        #min_time = sf.query(ValidWorkTimeBlock.start_time) \
        #    .join(ValidWorkScheduleTask, ValidWorkTimeBlock.validworkscheduletasks) \
        #    .order_by(asc(ValidWorkTimeBlock.start_time)) \
        #    .filter(ValidWorkScheduleTask.id == task_id).limit(1).scalar()
        #if min_time:
        #    #提前30分钟安排下一档工作
        #    min_datetime = datetime.combine(current_datetime.date(), min_time)
        #    start_datetime = min_datetime - timedelta(minutes=30)
        #    if start_datetime <= current_datetime <= min_datetime:
            #当天是否已经安排完成
            e = sf.query(func.count(ValidWorkCheckOn.id)) \
                .filter(ValidWorkCheckOn.task_id == task_id) \
                .filter(cast(ValidWorkCheckOn.valid_start_time, DateTime) == Utils.format_date(current_datetime)).scalar()

            if e == 0:
                #安排新的工作
                #1,得到拥有此考勤计划的所有人员ID
                usrs = sf.query(Archives.id).join(ValidWorkScheduleTask, Archives.validworkscheduletasks) \
                    .filter(ValidWorkScheduleTask.id == task_id).all()
                usrs = [u[0] for u in usrs]
                #2,得到此考勤计划的所有班次
                time_blocks = sf.query(ValidWorkTimeBlock) \
                    .join(ValidWorkScheduleTask, ValidWorkTimeBlock.validworkscheduletasks) \
                    .filter(ValidWorkScheduleTask.id == task_id).all()

                #3,批量插入CheckOn
                workers_tb = list()
                for usr_id in usrs:
                    for tb in time_blocks:
                        vwco = ValidWorkCheckOn()
                        vwco.archives_id = usr_id
                        vwco.task_id = task_id
                        vwco.time_block_id = tb.id
                        start = datetime.combine(current_datetime.date(), tb.start_time)
                        end = datetime.combine(current_datetime.date(), tb.end_time)
                        start = start - timedelta(minutes=tb.normal_in_space)
                        end = end + timedelta(minutes=tb.normal_out_space)
                        vwco.valid_start_time = start
                        vwco.valid_end_time = end
                        workers_tb.append(vwco)
                        pass
                    pass
                pass
                sf.add_all(workers_tb)
                sf.commit()
            pass
        pass
        pass


@points()
class ValidWorkPoints():
    def reg(self):
        reg_point("tinyms.sidebar.validwork.main.show", "菜单", "侧边栏", "考勤系统")
        reg_point("tinyms.sidebar.validwork.sub.scheduletask.show", "菜单", "考勤", "任务计划")
        reg_point("tinyms.sidebar.validwork.sub.timeblock.show", "菜单", "考勤", "班次/时间段")
        reg_point("tinyms.sidebar.validwork.sub.fingertemplate.show", "菜单", "考勤", "指纹模版")
        reg_point("tinyms.sidebar.validwork.sub.askforleave.show", "菜单", "考勤", "请假")
        reg_point("tinyms.sidebar.validwork.sub.overtime.show", "菜单", "考勤", "加班")
        reg_point("tinyms.sidebar.validwork.sub.hodiday.show", "菜单", "考勤", "节日")
        reg_point("tinyms.sidebar.validwork.sub.machine.show", "菜单", "考勤", "考勤机管理")

        #任务计划
        reg_point("tinyms.validwork.entity.ValidWorkScheduleTask.list", "考勤", "任务计划", "查看任务计划列表")
        reg_point("tinyms.validwork.entity.ValidWorkScheduleTask.view", "考勤", "任务计划", "查看任务计划明细")
        reg_point("tinyms.validwork.entity.ValidWorkScheduleTask.add", "考勤", "任务计划", "添加任务计划")
        reg_point("tinyms.validwork.entity.ValidWorkScheduleTask.update", "考勤", "任务计划", "修改任务计划")
        reg_point("tinyms.validwork.entity.ValidWorkScheduleTask.delete", "考勤", "任务计划", "删除任务计划")
        reg_point("tinyms.validwork.entity.ValidWorkScheduleTask.TimeBlock.view", "考勤", "任务计划", "查看班次/时间段")
        reg_point("tinyms.validwork.entity.ValidWorkScheduleTask.TimeBlock.edit", "考勤", "任务计划", "编辑班次/时间段/任务计划")

        #班次/时间段
        reg_point("tinyms.validwork.entity.ValidWorkTimeBlock.list", "考勤", "班次/时间段", "查看任务计划列表")
        reg_point("tinyms.validwork.entity.ValidWorkTimeBlock.view", "考勤", "班次/时间段", "查看任务计划明细")
        reg_point("tinyms.validwork.entity.ValidWorkTimeBlock.add", "考勤", "班次/时间段", "添加任务计划")
        reg_point("tinyms.validwork.entity.ValidWorkTimeBlock.update", "考勤", "班次/时间段", "修改任务计划")
        reg_point("tinyms.validwork.entity.ValidWorkTimeBlock.delete", "考勤", "班次/时间段", "删除任务计划")

        #指纹模版
        reg_point("tinyms.validwork.entity.ValidWorkFingerTemplate.list", "考勤", "指纹模版", "查看指纹模版列表")
        reg_point("tinyms.validwork.entity.ValidWorkFingerTemplate.view", "考勤", "指纹模版", "查看指纹模版明细")
        reg_point("tinyms.validwork.entity.ValidWorkFingerTemplate.add", "考勤", "指纹模版", "添加指纹模版")
        reg_point("tinyms.validwork.entity.ValidWorkFingerTemplate.update", "考勤", "指纹模版", "修改指纹模版")
        reg_point("tinyms.validwork.entity.ValidWorkFingerTemplate.delete", "考勤", "指纹模版", "删除指纹模版")
        reg_point("tinyms.validwork.entity.ValidWorkFingerTemplate.edit", "考勤", "指纹模版", "指纹录入")

        #节日
        reg_point("tinyms.validwork.entity.Holiday.list", "考勤", "节日", "查看节日列表")
        reg_point("tinyms.validwork.entity.Holiday.view", "考勤", "节日", "查看节日明细")
        reg_point("tinyms.validwork.entity.Holiday.add", "考勤", "节日", "添加节日")
        reg_point("tinyms.validwork.entity.Holiday.update", "考勤", "节日", "修改节日")
        reg_point("tinyms.validwork.entity.Holiday.delete", "考勤", "节日", "删除节日")

        #请假
        reg_point("tinyms.validwork.entity.AskForLeave.list", "考勤", "请假", "查看请假列表")
        reg_point("tinyms.validwork.entity.AskForLeave.view", "考勤", "请假", "查看请假明细")
        reg_point("tinyms.validwork.entity.AskForLeave.add", "考勤", "请假", "添加请假")
        reg_point("tinyms.validwork.entity.AskForLeave.update", "考勤", "请假", "修改请假")
        reg_point("tinyms.validwork.entity.AskForLeave.delete", "考勤", "请假", "删除请假")

        #加班
        reg_point("tinyms.validwork.entity.Overtime.list", "考勤", "加班", "查看加班列表")
        reg_point("tinyms.validwork.entity.Overtime.view", "考勤", "加班", "查看加班明细")
        reg_point("tinyms.validwork.entity.Overtime.add", "考勤", "加班", "添加加班")
        reg_point("tinyms.validwork.entity.Overtime.update", "考勤", "加班", "修改加班")
        reg_point("tinyms.validwork.entity.Overtime.delete", "考勤", "加班", "删除加班")

        #考勤机管理
        reg_point("tinyms.validwork.entity.ValidWorkMachine.list", "考勤", "考勤机管理", "查看考勤机列表")
        reg_point("tinyms.validwork.entity.ValidWorkMachine.update", "考勤", "考勤机管理", "修改考勤机")


        #启动任务分配管理器
        ValidWorkHelper.start_scheduler()