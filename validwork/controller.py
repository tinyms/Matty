__author__ = 'tinyms'

import random
import os
from zipfile import ZipFile, ZIP_DEFLATED
import uuid
from datetime import datetime, timedelta

from sqlalchemy import func, asc

from tinyms.core.web import IAuthRequest, IRequest
from tinyms.core.annotation import route, sidebar, datatable_provider, ajax, auth, dataview_provider, api
from tinyms.core.orm import SessionFactory
from tinyms.core.entity import Archives
from tinyms.core.common import Utils
from tinyms.dao.account import AccountHelper
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

@route("/validwork/download/client")
class DownloadFingerClient(IAuthRequest):
    def get(self, *args, **kwargs):
        file = self.pack_client()
        self.set_header("Content-Disposition", "attachment; filename=指纹采集助手.zip")
        f = open(file, "rb")
        self.write(f.read())
        f.close()

    def pack_client(self):
        user_id = self.get_current_user()
        root_path = self.get_webroot_path()
        download_path = root_path + "/download/validwork/"
        Utils.mkdirs(download_path)

        client_zip_name = download_path + Utils.md5("%i_client" % user_id) + ".zip"
        key_file_name = download_path + Utils.md5("%i_keyfile" % user_id)
        ip_file_name = download_path + "ip.txt"
        exe_file_name = download_path + "FingerTemplateHelper.exe"
        libcurl = download_path + "libcurl.dll"
        zlib1 = download_path + "zlib1.dll"

        if os.path.exists(key_file_name):
            os.remove(key_file_name)
        key = self.kengen()
        Utils.text_write(key_file_name, [key], "")

        if not os.path.exists(ip_file_name):
            Utils.text_write(ip_file_name, [self.request.host], "")

        if os.path.exists(client_zip_name):
            os.remove(client_zip_name)
        f = ZipFile(client_zip_name, "w")
        self.compress(f, ip_file_name, "ip.txt")
        self.compress(f, key_file_name, "temp.key")
        self.compress(f, exe_file_name, "指纹采集助手.exe")
        self.compress(f, libcurl, "libcurl.dll")
        self.compress(f, zlib1, "zlib1.dll")
        f.close()
        return client_zip_name

    def compress(self, zip_file, file_name, alias_name=""):
        if os.path.exists(file_name):
            zip_file.write(file_name, alias_name, ZIP_DEFLATED)

    def kengen(self):
        str_random = ['3', '4', '5', '6', '7', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k']
        seed = "%i@%s" % (self.get_current_user(), random.choice(str_random))
        sf = SessionFactory.new()
        obj = sf.query(ValidWorkFingerTemplateKey) \
            .filter(ValidWorkFingerTemplateKey.account_id == self.get_current_user()).limit(1).scalar()
        if obj:
            obj.ukey = str(uuid.uuid3(uuid.NAMESPACE_DNS, seed))
            sf.commit()
            return obj.ukey
        else:
            ukey = ValidWorkFingerTemplateKey()
            ukey.account_id = self.get_current_user()
            ukey.tpl = ""
            ukey.ukey = str(uuid.uuid3(uuid.NAMESPACE_DNS, seed))
            sf.add(ukey)
            sf.commit()
            return ukey.ukey

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
    __export__ = ["task_assign", "finger_tpl_save", "list_fingers"]

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

    #注册登记指纹模板
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

    #列出某一账户拥有多少个指头的指纹
    def list_fingers(self):
        sf = SessionFactory.new()
        archives_id = Utils.parse_int(self.param("archives_id"))
        items = sf.query(ValidWorkFingerTemplate.finger_index)\
            .filter(ValidWorkFingerTemplate.archives_id == archives_id).all()
        items = [item[0] for item in items]
        return items


#指纹登记
@api("tinyms.validwork.finger.template")
class FingerTemplateSign():
    def sign(self):
        sf = SessionFactory.new()
        obj = sf.query(ValidWorkFingerTemplateKey) \
            .filter(ValidWorkFingerTemplateKey.ukey == self.param("ukey")).scalar()
        body = self.body
        if obj and body:
            tpl = body.decode("utf-8")
            if tpl:
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
    def post(self, *args, **kwargs):

        #记录机器访问数据
        params_ = self.wrap_params_to_dict()
        sn = params_.get("SN")
        sf = SessionFactory.new()
        machine = sf.query(ValidWorkMachine).filter(ValidWorkMachine.sn == sn).limit(1).scalar()
        table = params_.get("table")
        if table == "OPERLOG":
            op_stamp = params_.get("OpStamp")
            if op_stamp and machine:
                machine.opstamp = Utils.parse_int(op_stamp)
                sf.commit()
            self.write("OK")
        elif table == "ATTLOG":
            stamp = params_.get("Stamp")
            if stamp and machine:
                stamp = Utils.parse_int(stamp)
                machine.stamp = stamp
                sf.commit()

            if stamp and stamp > 0:
                records_text = self.request.body
                if records_text:
                    records_text = records_text.decode("utf-8")
                    records = list()
                    for line in records_text.split("\n"):
                        items = line.split("\t")
                        if len(items) >= 2:
                            records.append((items[0], items[1]))
                    print(records)
                    for r in records:
                        archives_id = r[0]
                        touch_time = datetime.strptime(r[1], "%Y-%m-%d %H:%M:%S")
                        print(archives_id, touch_time)
                        self.detect_chkon_status(archives_id, touch_time)
                    self.write("OK")

    def get(self, *args, **kwargs):
        sn = self.get_argument("SN")
        opts = self.get_argument("options")
        self.set_header("Content-Type", "text/plain;charset=utf-8")
        if opts == "all":
            self.write("GET OPTION FROM:" + sn + "\n")
            self.write("ErrorDelay=60\n")
            self.write("Delay=15\n")
            self.write("TransInterval=1\n")
            self.write("TransFlag=1111000000\n")
            self.write("Realtime=1\n")
            self.write("Encrypt=0\n")
            self.write("TransTimes=00:00;14:05\n")
            sf = SessionFactory.new()
            machine = sf.query(ValidWorkMachine).filter(ValidWorkMachine.sn == sn).limit(1).scalar()
            if machine:
                if machine.stamp:
                    self.write("Stamp=" + str(machine.stamp) + "\n")
                if machine.opstamp:
                    self.write("OpStamp=" + str(machine.opstamp) + "\n")
                if machine.photo_stamp:
                    self.write("PhotoStamp=" + str(machine.photo_stamp) + "\n")
            else:
                #初始化一个起始交互日期
                a = "100000000"
                self.write("Stamp=" + a + "\n")
                self.write("OpStamp=" + a + "\n")
                self.write("PhotoStamp=" + a + "\n")


    #得到当前打卡用户的状态，正常上班(1)，正常下班(2)，还是迟到(3)，早退(4)，旷工(0)另外计算
    def detect_chkon_status(self, archives_id, touch_time):
        sf = SessionFactory.new()
        obj = sf.query(ValidWorkCheckOn) \
            .filter(ValidWorkCheckOn.archives_id == archives_id) \
            .filter(ValidWorkCheckOn.valid_start_time <= touch_time) \
            .filter(ValidWorkCheckOn.valid_end_time >= touch_time).limit(1).scalar()
        if obj:
            timeblock = sf.query(ValidWorkTimeBlock).get(obj.time_block_id)
            if timeblock:
                #探测用户状态
                current_date = Utils.current_datetime().date()
                #正常上班时间
                work_start_time = datetime.combine(current_date, timeblock.start_time)
                #正常下班时间
                normal_out_time = datetime.combine(current_date, timeblock.end_time)
                #正常上班打卡的开始时间(上班时间-正常上班打卡区间)
                touchin_starttime = work_start_time - timedelta(minutes=timeblock.normal_in_space)
                if touchin_starttime <= touch_time < work_start_time:
                    status = 1
                else:
                    #视为迟到的结束时间(上班时间+视为迟到打卡区间)
                    late_endtime = work_start_time + timedelta(minutes=timeblock.late_space)
                    if work_start_time <= touch_time <= late_endtime:
                        status = 3
                    else:
                        #正常下班打卡的结束时间(下班时间+视为正常打卡区间)
                        touchout_endtime = normal_out_time + timedelta(minutes=timeblock.normal_out_space)
                        if normal_out_time < touch_time <= touchout_endtime:
                            status = 2
                        else:
                            #视为早退的打卡开始时间(下班时间-视为早退打卡区间)
                            early_leave_starttime = normal_out_time - timedelta(minutes=timeblock.leave_early_space)
                            if early_leave_starttime <= touch_time <= normal_out_time:
                                status = 4
                            else:
                                #视为旷工
                                status = 0
                pass
                #更新CheckOn用户状态
                obj.check_time = touch_time
                obj.status = status
                sf.commit()


#GET /iclock/getrequest?SN=xxxxxx
#服务器发送到考勤机命令处理
@route("/iclock/getrequest")
class IClockCommand(IRequest):
    def get(self, *args, **kwargs):
        self.set_header("Content-Type", "text/plain;charset=utf-8")
        params_ = self.wrap_params_to_dict()
        sn = params_.get("SN")
        ip = self.request.remote_ip
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
        print(self.request.arguments)
        print(self.request.files)
        self.set_header("Content-Type", "text/plain;charset=utf-8")
        sn = self.get_argument("SN")
        id_ = self.get_argument("ID")
        rt = self.get_argument("Return")
        sf = SessionFactory.new()
        obj = sf.query(ValidWorkCommands).get(Utils.parse_int(id_))
        sf.delete(obj)
        sf.commit()
        self.write("OK")

