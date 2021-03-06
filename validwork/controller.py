__author__ = 'tinyms'

import random
import os
from zipfile import ZipFile, ZIP_DEFLATED
import uuid
from datetime import datetime, timedelta

from sqlalchemy import func, asc, cast

from tinyms.core.web import IAuthRequest, IRequest
from tinyms.core.annotation import route, sidebar, datatable_provider, ajax, auth, dataview_provider, api, EmptyClass
from tinyms.core.orm import SessionFactory, MinuteDiff
from tinyms.core.common import Utils
from tinyms.core.entity import Term, TermTaxonomy
from validwork.gerneric import ValidWorkHelper
from validwork.entity import *


@sidebar("/validwork/askforleave", "/validwork/askforleave", "请假登记",
         "tinyms.sidebar.validwork.sub.askforleave.show")
@route("/validwork/askforleave")
class AskForLeaveController(IAuthRequest):
    def get(self, *args, **kwargs):
        current_date = Utils.format_date(Utils.current_datetime())
        opt = dict()
        opt["current_date"] = current_date + " 00:00"
        opt["current_date_short"] = current_date
        return self.render("validwork/ask_for_leave.html", context=opt)


@sidebar("/validwork/overtime", "/validwork/overtime", "加班登记",
         "tinyms.sidebar.validwork.sub.overtime.show")
@route("/validwork/overtime")
class OvertimeController(IAuthRequest):
    def get(self, *args, **kwargs):
        current_date = Utils.format_date(Utils.current_datetime())+" 00:00"
        opt = dict()
        opt["current_date"] = current_date
        return self.render("validwork/overtime.html", context=opt)

@sidebar("/validwork", "/validwork/schedule/task", "考勤系统", "tinyms.sidebar.validwork.main.show", 0, "icon-calendar")
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
        items = list()
        for row in rows:
            items.append((row[0], row[1], Utils.format_time(row[2]), Utils.format_time(row[3])))

        return items


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

#日明细报表
@sidebar("/validwork/report", "/validwork/report/day_details", "报表", "tinyms.sidebar.validwork.sub.machine.show")
@route("/validwork/report/day_details")
class DayDetailsReportController(IAuthRequest):
    def get(self, *args, **kwargs):
        return self.render("validwork/report_day_details.html")


#加班登记数据提供
@dataview_provider("validwork.view.Overtime")
class OvertimeDataViewProvider():
    def count(self, kw, http_req):
        sf = SessionFactory.new()
        q = sf.query(func.count(ValidWorkOvertime.id))\
            .join(Archives, ValidWorkOvertime.archives_id == Archives.id)
        if kw:
            q = q.filter(Archives.name.contains(kw))
        return q.limit(1).scalar()

    def list(self, kw, start, limit, http_req):
        sf = SessionFactory.new()
        subq = sf.query(Archives.id, Archives.name).subquery()
        q = sf.query(ValidWorkOvertime, Archives.name, subq.c.name.label("creator"))\
            .join(Archives, ValidWorkOvertime.archives_id == Archives.id)\
            .outerjoin(subq, ValidWorkOvertime.creator == subq.c.id)
        if kw:
            q = q.filter(Archives.name.contains(kw))
        dataset = q.order_by(ValidWorkOvertime.id.desc()).offset(start).limit(limit).all()
        items = list()
        for row in dataset:
            ot = row[0]
            name = row[1]
            creator = row[2]
            item = dict()
            item["id"] = ot.id
            item["start_datetime"] = Utils.format_datetime_short(ot.start_datetime)
            item["end_datetime"] = Utils.format_datetime_short(ot.end_datetime)
            item["create_datetime"] = Utils.format_datetime_short(ot.create_datetime)
            item["name"] = name
            item["creator"] = creator
            items.append(item)
        return items

    def add(self, http_req):
        obj = ValidWorkOvertime()
        http_req.wrap_entity(obj)
        obj.creator = http_req.get_current_user()
        obj.create_datetime = Utils.current_datetime()
        sf = SessionFactory.new()
        sf.add(obj)
        sf.commit()
        return obj.id

    def modify(self, id_, http_req):
        sf = SessionFactory.new()
        obj = sf.query(ValidWorkOvertime).get(id_)
        if obj:
            http_req.wrap_entity(obj)
            obj.creator = http_req.get_current_user()
            obj.create_datetime = Utils.current_datetime()
            sf.commit()
            return ""
        return "failure"

    def delete(self, id_, http_req):
        sf = SessionFactory.new()
        num = sf.query(ValidWorkOvertime).filter(ValidWorkOvertime.id == id_).delete(synchronize_session='fetch')
        sf.commit()
        if num > 0:
            return ""
        return "failure"

    def view(self, id_, http_req):
        sf = SessionFactory.new()
        obj = sf.query(ValidWorkOvertime).get(id_)
        return obj.dict()

#加班登记数据提供
@dataview_provider("validwork.view.AskForLeave")
class AskForLeaveDataViewProvider():
    def count(self, kw, http_req):
        sf = SessionFactory.new()
        q = sf.query(func.count(ValidWorkAskForLeave.id))\
            .join(Archives, ValidWorkAskForLeave.archives_id == Archives.id)
        if kw:
            q = q.filter(Archives.name.contains(kw))
        return q.limit(1).scalar()

    def list(self, kw, start, limit, http_req):
        sf = SessionFactory.new()
        subq = sf.query(Archives.id, Archives.name).subquery()
        q = sf.query(ValidWorkAskForLeave, Archives.name, subq.c.name.label("creator"))\
            .join(Archives, ValidWorkAskForLeave.archives_id == Archives.id)\
            .outerjoin(subq, ValidWorkAskForLeave.creator == subq.c.id)
        if kw:
            q = q.filter(Archives.name.contains(kw))
        dataset = q.order_by(ValidWorkAskForLeave.id.desc()).offset(start).limit(limit).all()
        items = list()
        for row in dataset:
            ot = row[0]
            name = row[1]
            creator = row[2]
            item = dict()
            item["id"] = ot.id
            item["kind"] = ot.kind
            item["ask_date"] = Utils.format_date(ot.ask_date)
            item["start_datetime"] = Utils.format_datetime_short(ot.start_datetime)
            item["end_datetime"] = Utils.format_datetime_short(ot.end_datetime)
            item["create_datetime"] = Utils.format_datetime_short(ot.create_datetime)
            item["name"] = name
            item["creator"] = creator
            items.append(item)
        return items

    def add(self, http_req):
        obj = ValidWorkAskForLeave()
        http_req.wrap_entity(obj)
        obj.creator = http_req.get_current_user()
        obj.create_datetime = Utils.current_datetime()
        sf = SessionFactory.new()
        sf.add(obj)
        sf.commit()
        return obj.id

    def modify(self, id_, http_req):
        sf = SessionFactory.new()
        obj = sf.query(ValidWorkAskForLeave).get(id_)
        if obj:
            http_req.wrap_entity(obj)
            obj.creator = http_req.get_current_user()
            obj.create_datetime = Utils.current_datetime()
            sf.commit()
            return ""
        return "failure"

    def delete(self, id_, http_req):
        sf = SessionFactory.new()
        num = sf.query(ValidWorkAskForLeave).filter(ValidWorkAskForLeave.id == id_).delete(synchronize_session='fetch')
        sf.commit()
        if num > 0:
            return ""
        return "failure"

    def view(self, id_, http_req):
        sf = SessionFactory.new()
        obj = sf.query(ValidWorkAskForLeave).get(id_)
        return obj.dict()

#考勤日报表数据提供
@dataview_provider("validwork.view.report.DayReportView")
class DayDetailsReportDataProvider():
    def count(self, search_text, http_req):
        current_date = None
        if not current_date:
            current_date = Utils.format_date(Utils.current_datetime())
        sf = SessionFactory.new()
        subq = sf.query(Term.name.label("term_name"), TermTaxonomy.id).filter(TermTaxonomy.term_id == Term.id).subquery()
        q = sf.query(func.count(ValidWorkCheckOn.id))\
            .join(Archives, ValidWorkCheckOn.archives_id == Archives.id)\
            .outerjoin(subq, subq.c.id == Archives.org_id)
        if search_text:
            q = q.filter(Archives.name.contains(search_text))
        q = q.filter(cast(ValidWorkCheckOn.valid_start_time, Date) == current_date)
        return q.scalar()

    def list(self, search_text, start, limit, http_req):
        current_date = None
        if not current_date:
            current_date = Utils.format_date(Utils.current_datetime())
        sf = SessionFactory.new()
        subq = sf.query(Term.name.label("term_name"), TermTaxonomy.id).filter(TermTaxonomy.term_id == Term.id).subquery()
        q = sf.query(ValidWorkCheckOn.id,
                     Archives.code,
                     Archives.name,
                     ValidWorkTimeBlock.name,
                     ValidWorkTimeBlock.start_time,
                     ValidWorkTimeBlock.end_time,
                     ValidWorkCheckOn.status_in,
                     ValidWorkCheckOn.status_out,
                     ValidWorkCheckOn.status_no_sign,
                     ValidWorkCheckOn.check_in_time,
                     ValidWorkCheckOn.check_out_time,
                     subq.c.term_name,
                     MinuteDiff(ValidWorkCheckOn.valid_start_time, ValidWorkCheckOn.valid_end_time).label("diff")
                     ).select_from(ValidWorkCheckOn)\
            .join(ValidWorkTimeBlock, ValidWorkCheckOn.time_block_id == ValidWorkTimeBlock.id)\
            .join(Archives, ValidWorkCheckOn.archives_id == Archives.id)\
            .outerjoin(subq, subq.c.id == Archives.org_id)
        if search_text:
            q = q.filter(Archives.name.contains(search_text))
        q = q.order_by(Archives.name).filter(cast(ValidWorkCheckOn.valid_start_time, Date) == current_date)
        ds = q.offset(start).limit(limit).all()
        items = list()
        for row in ds:
            obj = EmptyClass()
            obj.id = row[0]
            obj.code = row[1]
            obj.name = row[2]
            obj.tb_name = row[3]
            obj.start_time = Utils.format_time(row[4])
            obj.end_time = Utils.format_time(row[5])
            obj.status_in = row[6]
            obj.status_out = row[7]
            obj.status_no_sign = row[8]
            obj.check_in_time = Utils.format_time(row[9])
            obj.check_out_time = Utils.format_time(row[10])
            obj.org_name = row[11]
            obj.no_work_timediff = row[12]
            items.append(obj.__dict__)
        return items

#考勤月报表数据提供
@dataview_provider("validwork.view.report.MonthReportView")
class MonthDetailsReportDataProvider():
    def count(self, search_text, http_req):
        current_date = None
        if not current_date:
            current_date = Utils.format_date(Utils.current_datetime())
        cur_datetime = Utils.parse_datetime(current_date+" 00:00")
        year = cur_datetime.year
        month = cur_datetime.month
        sf = SessionFactory.new()
        #某月考勤人员，分组统计
        q = sf.query(func.count(ValidWorkCheckOn.id))\
            .join(Archives, ValidWorkCheckOn.archives_id == Archives.id)\
            .filter(func.YEAR(ValidWorkCheckOn.valid_start_time) == year)\
            .filter(func.MONTH(ValidWorkCheckOn.valid_start_time) == month)\
            .group_by(ValidWorkCheckOn.archives_id, Archives.name)

        if search_text:
            q = q.filter(Archives.name.contains(search_text))

        return q.scalar()

    def list(self, search_text, start, limit, http_req):
        current_date = None
        if not current_date:
            current_date = Utils.format_date(Utils.current_datetime())
        cur_datetime = Utils.parse_datetime(current_date+" 00:00")
        year = cur_datetime.year
        month = cur_datetime.month

        sf = SessionFactory.new()
        #group by all people with the month
        checkon_subq = sf.query(ValidWorkCheckOn.archives_id)\
            .join(Archives, ValidWorkCheckOn.archives_id == Archives.id)\
            .filter(func.YEAR(ValidWorkCheckOn.valid_start_time) == year)\
            .filter(func.MONTH(ValidWorkCheckOn.valid_start_time) == month)\
            .group_by(ValidWorkCheckOn.archives_id).subquery()

        #迟到,早退,旷工,请假,加班分组统计
        late_subq = sf.query(ValidWorkCheckOn.archives_id, (func.count(1)).label("total"))\
            .filter(ValidWorkCheckOn.status_in == 1)\
            .filter(func.YEAR(ValidWorkCheckOn.valid_start_time) == year)\
            .filter(func.MONTH(ValidWorkCheckOn.valid_start_time) == month)\
            .group_by(ValidWorkCheckOn.archives_id).subquery()

        early_leave_subq = sf.query(ValidWorkCheckOn.archives_id, (func.count(1)).label("total"))\
            .filter(ValidWorkCheckOn.status_out == 1)\
            .filter(func.YEAR(ValidWorkCheckOn.valid_start_time) == year)\
            .filter(func.MONTH(ValidWorkCheckOn.valid_start_time) == month)\
            .group_by(ValidWorkCheckOn.archives_id).subquery()

        no_work_subq = sf.query(ValidWorkCheckOn.archives_id,
                                (func.sum(MinuteDiff(ValidWorkCheckOn.valid_start_time,
                                                     ValidWorkCheckOn.valid_end_time))/(60*24)).label("total"))\
            .filter(ValidWorkCheckOn.status_no_sign == 1)\
            .filter(func.YEAR(ValidWorkCheckOn.valid_start_time) == year)\
            .filter(func.MONTH(ValidWorkCheckOn.valid_start_time) == month)\
            .group_by(ValidWorkCheckOn.archives_id).subquery()
        #事假
        askforleave_subq1 = sf.query(ValidWorkAskForLeave.archives_id,
                                    (func.sum(MinuteDiff(ValidWorkAskForLeave.start_datetime,
                                                         ValidWorkAskForLeave.end_datetime))/(60*24)).label("total"))\
            .filter(func.YEAR(ValidWorkAskForLeave.start_datetime) == year)\
            .filter(func.MONTH(ValidWorkAskForLeave.start_datetime) == month)\
            .filter(ValidWorkAskForLeave.kind == 0)\
            .group_by(ValidWorkAskForLeave.archives_id).subquery()
        #病假
        askforleave_subq2 = sf.query(ValidWorkAskForLeave.archives_id,
                                    (func.sum(MinuteDiff(ValidWorkAskForLeave.start_datetime,
                                                         ValidWorkAskForLeave.end_datetime))/(60*24)).label("total"))\
            .filter(func.YEAR(ValidWorkAskForLeave.start_datetime) == year)\
            .filter(func.MONTH(ValidWorkAskForLeave.start_datetime) == month)\
            .filter(ValidWorkAskForLeave.kind == 1)\
            .group_by(ValidWorkAskForLeave.archives_id).subquery()
        #其它假
        askforleave_subq3 = sf.query(ValidWorkAskForLeave.archives_id,
                                    (func.sum(MinuteDiff(ValidWorkAskForLeave.start_datetime,
                                                         ValidWorkAskForLeave.end_datetime))/(60*24)).label("total"))\
            .filter(func.YEAR(ValidWorkAskForLeave.start_datetime) == year)\
            .filter(func.MONTH(ValidWorkAskForLeave.start_datetime) == month)\
            .filter(ValidWorkAskForLeave.kind == 2)\
            .group_by(ValidWorkAskForLeave.archives_id).subquery()

        overtime_subq = sf.query(ValidWorkOvertime.archives_id,
                                    (func.sum(MinuteDiff(ValidWorkOvertime.start_datetime,
                                                         ValidWorkOvertime.end_datetime))/60).label("total"))\
            .filter(func.YEAR(ValidWorkOvertime.start_datetime) == year)\
            .filter(func.MONTH(ValidWorkOvertime.start_datetime) == month)\
            .group_by(ValidWorkOvertime.archives_id).subquery()

        term_subq = sf.query(Term.name.label("term_name"), TermTaxonomy.id)\
            .filter(TermTaxonomy.term_id == Term.id).subquery()

        subq = sf.query(Archives.id, Archives.code, Archives.name, term_subq.c.term_name)\
            .select_from(Archives).outerjoin(term_subq, Archives.org_id == term_subq.c.id).subquery()

        q = sf.query(checkon_subq.c.archives_id,
                     subq.c.code,
                     subq.c.name,
                     late_subq.c.total,
                     early_leave_subq.c.total,
                     no_work_subq.c.total,
                     askforleave_subq1.c.total,
                     askforleave_subq2.c.total,
                     askforleave_subq3.c.total,
                     overtime_subq.c.total,
                     subq.c.term_name).select_from(checkon_subq)\
            .outerjoin(late_subq, checkon_subq.c.archives_id == late_subq.c.archives_id)\
            .outerjoin(early_leave_subq, checkon_subq.c.archives_id == early_leave_subq.c.archives_id)\
            .outerjoin(no_work_subq, checkon_subq.c.archives_id == no_work_subq.c.archives_id)\
            .outerjoin(askforleave_subq1, checkon_subq.c.archives_id == askforleave_subq1.c.archives_id)\
            .outerjoin(askforleave_subq2, checkon_subq.c.archives_id == askforleave_subq2.c.archives_id)\
            .outerjoin(askforleave_subq3, checkon_subq.c.archives_id == askforleave_subq3.c.archives_id)\
            .outerjoin(overtime_subq, checkon_subq.c.archives_id == overtime_subq.c.archives_id)\
            .join(subq, checkon_subq.c.archives_id == subq.c.id)

        if search_text:
            q = q.filter(checkon_subq.c.name.contains(search_text))

        ds = q.order_by(checkon_subq.c.archives_id).offset(start).limit(limit).all()
        items = list()
        for row in ds:
            obj = EmptyClass()
            obj.id = row[0]
            obj.code = row[1]
            obj.name = row[2]
            obj.late_total = row[3]
            obj.early_leave_total = row[4]
            obj.no_work_total = row[5]
            obj.askforleave_total1 = row[6]
            obj.askforleave_total2 = row[7]
            obj.askforleave_total3 = row[8]
            obj.overtime_total = row[9]
            obj.org_name = row[10]
            items.append(obj.__dict__)
        return items

#月分组汇总
@route("/validwork/report/month_groupby")
class MonthGroupByReportController(IAuthRequest):
    def get(self, *args, **kwargs):
        return self.render("validwork/report_month_details.html")


@route("/validwork/download/client")
class DownloadFingerClientController(IAuthRequest):
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
            .filter(cast(ValidWorkTimeBlock.start_time, Time) == Utils.format_time(entity_obj.start_time)) \
            .filter(cast(ValidWorkTimeBlock.end_time, Time) == Utils.format_time(entity_obj.end_time)).scalar()
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

        rows = q.order_by(Archives.name).offset(start).limit(limit).all()
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
    __export__ = ["task_assign", "finger_tpl_save", "list_fingers", "push_finger_tpl_to_machine"]

    @auth({"tinyms.validwork.entity.ValidWorkScheduleTask.TimeBlock.edit"}, ["UnAuth"])
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
    @auth({"tinyms.validwork.entity.ValidWorkFingerTemplate.edit"}, ["UnAuth"])
    def finger_tpl_save(self):
        index = Utils.parse_int(self.param("index"))
        tpl = self.param("tpl")
        archives_id = Utils.parse_int(self.param("archives_id"))
        sf = SessionFactory.new()
        obj = sf.query(ValidWorkFingerTemplate) \
            .filter(ValidWorkFingerTemplate.archives_id == archives_id) \
            .filter(ValidWorkFingerTemplate.finger_index == index).limit(1).scalar()

        machines_sn = sf.query(ValidWorkMachine.sn).all()
        machines_sn = [sn[0] for sn in machines_sn]
        name = sf.query(Archives.name).filter(Archives.id == archives_id).limit(1).scalar()
        for sn in machines_sn:
            ValidWorkHelper.push_user_fp_to_machine(sn, archives_id, name, index, tpl)

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
    @auth({"tinyms.validwork.entity.ValidWorkFingerTemplate.list"}, [])
    def list_fingers(self):
        sf = SessionFactory.new()
        archives_id = Utils.parse_int(self.param("archives_id"))
        items = sf.query(ValidWorkFingerTemplate.finger_index) \
            .filter(ValidWorkFingerTemplate.archives_id == archives_id).all()
        items = [item[0] for item in items]
        return items

    #推送所有指纹至机器
    @auth({"tinyms.validwork.entity.ValidWorkFingerTemplate.edit"}, ["UnAuth"])
    def push_finger_tpl_to_machine(self):
        sf = SessionFactory.new()
        sn = sf.query(ValidWorkMachine.sn) \
            .filter(ValidWorkMachine.id == Utils.parse_int(self.param("machine_id"))).limit(1).scalar()
        peoples = sf.query(ValidWorkFingerTemplate.archives_id, Archives.name,
                           ValidWorkFingerTemplate.finger_index, ValidWorkFingerTemplate.tpl) \
            .join((Archives, ValidWorkFingerTemplate.archives)).all()
        finger_tpl_list = list()
        for p in peoples:
            finger_tpl_list.append(p)
        ValidWorkHelper.push_users_fp_to_machine(sn, finger_tpl_list)
        return ["success"]

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
class IClockCDataController(IRequest):
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
                    for r in records:
                        archives_id = r[0]
                        touch_time = datetime.strptime(r[1], "%Y-%m-%d %H:%M:%S")
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
                    obj.check_in_time = touch_time
                    obj.status_in = 0
                else:
                    #视为迟到的结束时间(上班时间+视为迟到打卡区间)
                    late_endtime = work_start_time + timedelta(minutes=timeblock.late_space)
                    if work_start_time <= touch_time <= late_endtime:
                        obj.status_in = 1
                        obj.check_in_time = touch_time
                    else:
                        #正常下班打卡的结束时间(下班时间+视为正常打卡区间)
                        touchout_endtime = normal_out_time + timedelta(minutes=timeblock.normal_out_space)
                        if normal_out_time < touch_time <= touchout_endtime:
                            obj.status_out = 0
                            obj.check_out_time = touch_time
                        else:
                            #视为早退的打卡开始时间(下班时间-视为早退打卡区间)
                            early_leave_starttime = normal_out_time - timedelta(minutes=timeblock.leave_early_space)
                            if early_leave_starttime <= touch_time <= normal_out_time:
                                obj.status_out = 1
                                obj.check_out_time = touch_time
                pass
                sf.commit()


#GET /iclock/getrequest?SN=xxxxxx
#服务器发送到考勤机命令处理
@route("/iclock/getrequest")
class IClockCommandController(IRequest):
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
class IClockDeviceCommandReturnController(IRequest):
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

