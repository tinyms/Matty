__author__ = 'tinyms'

import random
import uuid

from sqlalchemy import func, asc

from tinyms.core.web import IAuthRequest, IRequest
from tinyms.core.annotation import route, sidebar, datatable_provider, ajax, auth, dataview_provider, api
from tinyms.core.orm import SessionFactory
from tinyms.core.entity import Archives
from tinyms.core.common import Utils
from validwork.entity import *


@sidebar("/validwork", "/validwork/schedule/task", "考勤系统", "tinyms.sidebar.validwork.main.show")
@sidebar("/validwork/schedule_task", "/validwork/schedule/task", "任务计划",
         "tinyms.sidebar.validwork.sub.scheduletask.show")
@route("/validwork/schedule/task")
class ScheduleTaskController(IAuthRequest):
    def get(self, *args, **kwargs):
        data = dict()
        data["timeblocks"] = ScheduleTaskController.list_timeblocks()
        return self.render("validwork/schedule.task.html", data=data)

    @staticmethod
    def list_timeblocks():
        sf = SessionFactory.new()
        rows = sf.query(ValidWorkTimeBlock.id, ValidWorkTimeBlock.name, ValidWorkTimeBlock.start_time,
                        ValidWorkTimeBlock.end_time).all()
        return rows


@sidebar("/validwork/timeblock", "/validwork/timeblock", "班次/时间段", "tinyms.sidebar.validwork.sub.timeblock.show")
@route("/validwork/timeblock")
class TimeBlockController(IAuthRequest):
    def get(self, *args, **kwargs):
        return self.render("validwork/timeblock.html")


@sidebar("/validwork/finger_template", "/validwork/finger/template", "人员指纹模版",
         "tinyms.sidebar.validwork.sub.fingertemplate.show")
@route("/validwork/finger/template")
class FingerTemplateController(IAuthRequest):
    def get(self, *args, **kwargs):
        data = dict()
        data["schedule_task"] = FingerTemplateController.list_schedule_task()
        return self.render("validwork/finger.template.html", data=data)

    @staticmethod
    def list_schedule_task():
        sf = SessionFactory.new()
        rows = sf.query(ValidWorkScheduleTask.id, ValidWorkScheduleTask.name).all()
        return rows


@sidebar("/validwork/holiday", "/validwork/holiday", "节日", "tinyms.sidebar.validwork.sub.hodiday.show")
@route("/validwork/holiday")
class HolidayController(IAuthRequest):
    def get(self, *args, **kwargs):
        return self.render("validwork/holiday.html")


@sidebar("/validwork/machine", "/validwork/machine", "考勤机管理", "tinyms.sidebar.validwork.sub.machine.show")
@route("/validwork/machine")
class MachineController(IAuthRequest):
    def get(self, *args, **kwargs):
        return self.render("validwork/machine.html")


#DataProvider
@datatable_provider("validwork.entity.ValidWorkTimeBlock")
class TimeBlockDataProvider():
    def before_add(self, entity_obj, sf, req):
        num = sf.query(func.count(ValidWorkTimeBlock.id)).filter(ValidWorkTimeBlock.name == entity_obj.name).scalar()
        if num > 0:
            return "名称已经存在!"
        num = sf.query(func.count(ValidWorkTimeBlock.id)) \
            .filter(ValidWorkTimeBlock.start_time == entity_obj.start_time) \
            .filter(ValidWorkTimeBlock.end_time == entity_obj.end_time).scalar()
        if num > 0:
            return "班次/时间段已经存在!"
        return ""


@datatable_provider("validwork.entity.ValidWorkScheduleTask")
class ValidWorkScheduleTaskDataProvider():
    def before_add(self, entity_obj, sf, req):
        num = sf.query(func.count(ValidWorkScheduleTask.id)) \
            .filter(ValidWorkScheduleTask.name == entity_obj.name).scalar()
        if num > 0:
            return "名称已经存在!"
        return ""


@ajax("tinyms.ValidWorkScheduleTask.TimeBlock")
class ValidWorkScheduleTask4TimeBlock():
    __export__ = ["list", "save"]

    @auth({"tinyms.validwork.entity.ValidWorkScheduleTask.TimeBlock.view"}, [])
    def list(self):
        sf = SessionFactory.new()
        ds = sf.query(ValidWorkTimeBlock.id) \
            .join(ValidWorkScheduleTask, ValidWorkTimeBlock.validworkscheduletasks) \
            .filter(ValidWorkScheduleTask.id == Utils.parse_int(self.param("id"))).all()
        return [row[0] for row in ds]

    @auth({"tinyms.validwork.entity.ValidWorkScheduleTask.TimeBlock.edit"}, ["UnAuth"])
    def save(self):
        id_ = Utils.parse_int(self.param("id"))
        tb_id = Utils.parse_int(self.param("tb_id"))
        state = self.param("s")
        if id_ > 0 and tb_id > 0:
            if state == "1":
                sf = SessionFactory.new()
                task = sf.query(ValidWorkScheduleTask).get(id_)
                timeblock = sf.query(ValidWorkTimeBlock).get(tb_id)
                task.validworktimeblocks.append(timeblock)
                sf.commit()
            else:
                sf = SessionFactory.new()
                task = sf.query(ValidWorkScheduleTask).get(id_)
                timeblock = sf.query(ValidWorkTimeBlock).get(tb_id)
                task.validworktimeblocks.remove(timeblock)
                sf.commit()
            return ["success"]
        return ["failure"]


@dataview_provider("validwork.view.ValidWorkArchives")
class ValidWorkArchivesDataView():
    def count(self, keywords, http_req):
        sf = SessionFactory.new()
        q = sf.query(func.count(Archives.id)).outerjoin(ValidWorkScheduleTask, Archives.validworkscheduletasks)
        q = q.filter(Archives.name != "超级管理员")
        if keywords:
            q = q.filter(Archives.name.like("%" + keywords + "%"))
        return q.scalar()

    def list(self, keywords, start, limit, http_req):
        org_id = Utils.parse_int(http_req.get_argument("org_id"))
        sf = SessionFactory.new()
        q = sf.query(Archives.id, Archives.name, Archives.sex, Archives.org_id, ValidWorkScheduleTask.name,
                     ValidWorkScheduleTask.id) \
            .outerjoin(ValidWorkScheduleTask, Archives.validworkscheduletasks)
        q = q.filter(Archives.name != "超级管理员")
        if keywords:
            q = q.filter(Archives.name.like("%" + keywords + "%"))
        if org_id:
            q = q.filter(Archives.org_id == org_id)

        rows = q.offset(start).limit(limit).all()
        items = list()
        for row in rows:
            item = dict()
            item["id"] = row[0]
            item["name"] = row[1]
            item["sex"] = row[2]
            item["org_id"] = row[3]
            item["st_name"] = row[4]
            if not row[4]:
                item["st_name"] = ""
            item["st_id"] = row[5]
            if not row[5]:
                item["st_id"] = 0
            items.append(item)
        return items


@ajax("tinyms.validwork.FingerAndTaskAssign")
class FingerAndTaskAssign():
    __export__ = ["task_assign", "finger_tpl_save"]

    def task_assign(self):
        archives_id = Utils.parse_int(self.param("id"))
        task_id = Utils.parse_int(self.param("st_id"))
        if archives_id and task_id:
            sf = SessionFactory.new()
            usr = sf.query(Archives).get(archives_id)
            if usr:
                usr.validworkscheduletasks = []
                task = sf.query(ValidWorkScheduleTask).get(task_id)
                usr.validworkscheduletasks.append(task)
                sf.commit()
                return ["success"]
        return ["failure"]

    def finger_tpl_save(self):
        index = Utils.parse_int(self.param("index"))
        tpl = self.param("tpl")
        archives_id = Utils.parse_int(self.param("archives_id"))
        sf = SessionFactory.new()
        obj = sf.query(ValidWorkFingerTemplate) \
            .filter(ValidWorkFingerTemplate.archives_id == archives_id) \
            .filter(ValidWorkFingerTemplate.finger_index == index).limit(1).scalar()
        if obj:
            obj.tpl = tpl
            sf.commit()
            return ["success"]
        else:
            if archives_id:
                sf = SessionFactory.new()
                obj = ValidWorkFingerTemplate()
                obj.card_no = ""
                obj.finger_index = index
                obj.tpl = tpl
                obj.archives_id = archives_id
                sf.add(obj)
                sf.commit()
                return ["success"]
        return ["failure"]


#指纹登记
@api("tinyms.validwork.finger.template")
class FingerTemplateSign():
    def sign(self):
        sf = SessionFactory.new()
        obj = sf.query(ValidWorkFingerTemplateKey) \
            .filter(ValidWorkFingerTemplateKey.ukey == self.param("ukey")).scalar()
        tpl = self.param("tpl")
        if obj and tpl:
            obj.tpl = tpl
            sf.commit()
            return "success"
        return "failure"

    def value(self):
        sf = SessionFactory.new()
        val = sf.query(ValidWorkFingerTemplateKey.tpl) \
            .filter(ValidWorkFingerTemplateKey.account_id == self.request.current_user).limit(1).scalar()
        if val:
            return [val]
        return [""]

    def clear(self):
        sf = SessionFactory.new()
        obj = sf.query(ValidWorkFingerTemplateKey) \
            .filter(ValidWorkFingerTemplateKey.account_id == self.request.current_user).limit(1).scalar()
        if obj:
            obj.tpl = ""
            sf.commit()
            return ["success"]
        return ["failure"]

    def kengen(self):
        str_random = ['3', '4', '5', '6', '7', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k']
        seed = "%i@%s" % (self.request.current_user, random.choice(str_random))
        sf = SessionFactory.new()
        obj = sf.query(ValidWorkFingerTemplateKey) \
            .filter(ValidWorkFingerTemplateKey.account_id == self.request.current_user).limit(1).scalar()
        if obj:
            obj.ukey = str(uuid.uuid3(uuid.NAMESPACE_DNS, seed))
            sf.commit()
            return [obj.ukey]
        else:
            ukey = ValidWorkFingerTemplateKey()
            ukey.account_id = self.request.current_user
            ukey.tpl = ""
            ukey.ukey = str(uuid.uuid3(uuid.NAMESPACE_DNS, seed))
            sf.add(ukey)
            sf.commit()
            return [ukey.ukey]


@route("/fingerSign")
class FingerSignTest(IRequest):
    def get(self, *args, **kwargs):
        self.render("validwork/test.html")


#考勤机交互

# GET /iclock/cdata?SN=xxxxxx
@route("/iclock/cdata")
class IClockCData(IRequest):
    def get(self, *args, **kwargs):
        sn = self.get_argument("SN")
        opts = self.get_argument("options")
        stamp = Utils.parse_int(self.get_argument("Stamp"))
        op_stamp = Utils.parse_int(self.get_argument("OpStamp"))
        self.set_header("Content-Type", "text/plain;charset=utf-8")
        if opts == "all":
            self.write("GET OPTION FROM:" + sn + r"\n")
            self.write(r"ErrorDelay=60\n")
            self.write(r"Delay=15\n")
            self.write(r"TransInterval=1\n")
            self.write(r"TransFlag=1111000000\n")
            self.write(r"Realtime=1\n")
            self.write(r"Encrypt=0\n")
            self.write(r"TransTimes=00:00;14:05\n")
            sf = SessionFactory.new()
            machine = sf.query(ValidWorkMachine).filter(ValidWorkMachine.sn == sn).limit(1).scalar()
            if machine:
                if machine.stamp:
                    self.write("Stamp=" + machine.stamp + r"\n")
                if machine.opstamp:
                    self.write("OpStamp=" + machine.opstamp + r"\n")
                if machine.photo_stamp:
                    self.write("PhotoStamp=" + machine.photo_stamp + r"\n")
            else:
                #初始化一个起始交互日期
                a = 10000000
                self.write("Stamp=" + a + r"\n")
                self.write("OpStamp=" + a + r"\n")
                self.write("PhotoStamp=" + a + r"\n")
        else:
            #记录机器访问数据
            sf = SessionFactory.new()
            machine = sf.query(ValidWorkMachine).filter(ValidWorkMachine.sn == sn).limit(1).scalar()
            if machine:
                machine.opstamp = op_stamp
                machine.stamp = stamp
                sf.commit()
                #登记指纹
            if stamp and stamp > 0:
                records = list()
                for r in records:
                    archives_id = r[0]
                    touch_time = r[1]
                self.write("OK")
            elif not op_stamp:
                self.write("OK")


#GET /iclock/getrequest?SN=xxxxxx
#服务器发送到考勤机命令处理
@route("/iclock/getrequest")
class IClockCommand(IRequest):
    def get(self, *args, **kwargs):
        self.set_header("Content-Type", "text/plain;charset=utf-8")
        sn = self.get_argument("SN")
        ip = self.get_argument("INFO")
        #记录当前机器信息
        sf = SessionFactory.new()
        obj = sf.query(ValidWorkMachine).filter(ValidWorkMachine.sn == sn).limit(1).scalar()
        if not obj:
            m = ValidWorkMachine()
            m.sn = sn
            m.ip = ip
            m.last_connect_time = Utils.current_datetime()
            sf.add(m)
            sf.commit()
        else:
            obj.ip = ip
            obj.last_connect_time = Utils.current_datetime()
            sf.commit()

        #取出一条命令下发给机器执行
        cmd = sf.query(ValidWorkCommands.id, ValidWorkCommands.cmd) \
            .filter(ValidWorkCommands.sn == sn) \
            .order_by(asc(ValidWorkCommands.id)).limit(1).scalar()
        if cmd:
            self.write("C:%s:%s" % (cmd[0], cmd[1]))
            pass


# POST /iclock/devicecmd?SN=xxxxxx&&ID=iiii&Return=vvvv&CMD=ssss
#机器执行完命令后的反馈
@route("/iclock/devicecmd")
class IClockDeviceCommandReturn(IRequest):
    def post(self, *args, **kwargs):
        self.set_header("Content-Type", "text/plain;charset=utf-8")
        sn = self.get_argument("SN")
        id_ = self.get_argument("ID")
        rt = self.get_argument("Return")
        sf = SessionFactory.new()
        obj = sf.query(ValidWorkCommands).get(Utils.parse_int(id_))
        sf.delete(obj)
        sf.commit()
        self.write("OK")
