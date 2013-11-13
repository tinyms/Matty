__author__ = 'tinyms'

from tinyms.core.annotation import points, reg_point

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