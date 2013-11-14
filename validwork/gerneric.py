__author__ = 'tinyms'

from sqlalchemy import asc, func
from tinyms.core.annotation import points, reg_point
from tinyms.core.common import Utils
from tinyms.core.orm import SessionFactory
from validwork.entity import *
from datetime import datetime, date, time, timedelta


class ValidWorkHelper():
    @staticmethod
    def push_command_to_machine(sn, cmd):
        sf = SessionFactory.new()
        vwc = ValidWorkCommands()
        vwc.sn = sn
        vwc.cmd = cmd
        vwc.create_date = Utils.current_datetime()
        sf.add(vwc)
        sf.commit()

    @staticmethod
    def push_user_fp_to_machine(sn, pin, name, fid, tpl):
        create = r"DATA DEL_USER PIN=%i\r\nDATA USER PIN=%i\tName=%s\r\n" % (pin, pin, name)
        update = r"DATA FP PIN=%i\tFID=%i\tTMP=%s\r\n" % (pin, fid, tpl)
        sf = SessionFactory.new()
        vwc = ValidWorkCommands()
        vwc.sn = sn
        vwc.cmd = create
        vwc.create_date = Utils.current_datetime()
        vwc1 = ValidWorkCommands()
        vwc1.sn = sn
        vwc1.cmd = update
        vwc1.create_date = Utils.current_datetime()
        sf.add_all([vwc, vwc1])
        sf.commit()

    @staticmethod
    def push_users_fp_to_machine(sn, items):
        """

        @param sn:
        @param items: [(pin, name, fid, tpl)..]
        """
        sf = SessionFactory.new()
        cmds = list()
        for item in items:
            create = r"DATA DEL_USER PIN=%i\r\nDATA USER PIN=%i\tName=%s\r\n" % (item[0], item[0], item[1])
            update = r"DATA FP PIN=%i\tFID=%i\tTMP=%s\r\n" % (item[0], item[2], item[3])
            vwc = ValidWorkCommands()
            vwc.sn = sn
            vwc.cmd = create
            vwc.create_date = Utils.current_datetime()
            vwc1 = ValidWorkCommands()
            vwc1.sn = sn
            vwc1.cmd = update
            vwc1.create_date = Utils.current_datetime()
            cmds += [vwc, vwc1]
        sf.add_all(cmds)
        sf.commit()

    #线程后台定时运动
    @staticmethod
    def organization_of_work():
        current_datetime = Utils.current_datetime()
        sf = SessionFactory.new()
        #列出所有考勤计划
        tasks = sf.query(ValidWorkScheduleTask.id).all()
        tasks = [task[0] for task in tasks]
        for task in tasks:
            #得到班次最小的时间点
            min_time = sf.query(ValidWorkTimeBlock.start_time) \
                .join(ValidWorkScheduleTask, ValidWorkTimeBlock.validworkscheduletasks) \
                .order_by(asc(ValidWorkTimeBlock.start_time)) \
                .filter(ValidWorkScheduleTask.id == task).limit(1).scalar()
            if min_time:
                #提前30分钟安排下一档工作
                min_datetime = datetime.combine(current_datetime.date(), min_time)
                start_datetime = min_datetime - timedelta(minutes=30)
                if start_datetime <= current_datetime <= min_datetime:
                    #当天是否已经安排完成
                    e = sf.query(func.count(ValidWorkCheckOn.id))\
                        .filter(ValidWorkCheckOn.task_id == task)\
                        .filter(ValidWorkCheckOn.valid_start_time.date() == current_datetime.date()).scalar()
                    if e == 0:
                        #安排新的工作
                        #1,得到拥有此考勤计划的所有人员ID
                        #2,得到此考勤计划的所有班次
                        #3,批量插入CheckOn
                        pass
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
        reg_point("tinyms.validwork.entity.ValidWorkFingerTemplate.list", "考勤", "指纹模版", "查看任务计划列表")
        reg_point("tinyms.validwork.entity.ValidWorkFingerTemplate.view", "考勤", "指纹模版", "添加任务计划明细")
        reg_point("tinyms.validwork.entity.ValidWorkFingerTemplate.add", "考勤", "指纹模版", "添加任务计划")
        reg_point("tinyms.validwork.entity.ValidWorkFingerTemplate.update", "考勤", "指纹模版", "修改任务计划")
        reg_point("tinyms.validwork.entity.ValidWorkFingerTemplate.delete", "考勤", "指纹模版", "删除任务计划")
        reg_point("tinyms.validwork.entity.ValidWorkFingerTemplate.edit", "考勤", "指纹模版", "指纹录入")
        #节日
        reg_point("tinyms.validwork.entity.Holiday.list", "考勤", "节日", "查看任务计划列表")
        reg_point("tinyms.validwork.entity.Holiday.view", "考勤", "节日", "添加任务计划明细")
        reg_point("tinyms.validwork.entity.Holiday.add", "考勤", "节日", "添加任务计划")
        reg_point("tinyms.validwork.entity.Holiday.update", "考勤", "节日", "修改任务计划")
        reg_point("tinyms.validwork.entity.Holiday.delete", "考勤", "节日", "删除任务计划")
        #考勤机管理
        reg_point("tinyms.validwork.entity.ValidWorkMachine.list", "考勤", "考勤机管理", "查看任务计划")
        #reg_point("tinyms.validwork.entity.ValidWorkMachine.view", "考勤", "考勤机管理", "查看任务计划")
        #reg_point("tinyms.validwork.entity.ValidWorkMachine.add", "考勤", "考勤机管理", "添加任务计划")
        reg_point("tinyms.validwork.entity.ValidWorkMachine.update", "考勤", "考勤机管理", "修改任务计划")
        #reg_point("tinyms.validwork.entity.ValidWorkMachine.delete", "考勤", "考勤机管理", "删除任务计划")