__author__ = 'tinyms'

import json

from tinyms.core.orm import SessionFactory
from tinyms.core.entity import Setting
from tinyms.core.common import JsonEncoder


#用户级别设置辅助类
class UserSettingHelper():
    def __init__(self, usr_id):
        self.usr = "%s" % usr_id
        self.setting = dict()
        self.load()

    def get(self, key, default_=None):
        val = self.setting.get(key)
        if val:
            return val
        return default_

    def set(self, dic_obj):
        v = json.dumps(dic_obj, cls=JsonEncoder)
        cnn = SessionFactory.new()
        item = cnn.query(Setting).filter(Setting.owner_ == self.usr).limit(1).scalar()
        if item:
            item.val_ = v
            cnn.commit()
        else:
            obj = Setting()
            obj.owner_ = self.usr
            obj.val_ = v
            cnn.add(obj)
            cnn.commit()

    def load(self):
        cnn = SessionFactory.new()
        json_text = cnn.query(Setting.val_).filter(Setting.owner_ == self.usr).limit(1).scalar()
        if json_text:
            self.setting = json.loads(json_text)
        return self.setting


#平台级别设置辅助类
class AppSettingHelper():
    __global__ = None

    @staticmethod
    def load():
        if not AppSettingHelper.__global__:
            u = UserSettingHelper("root")
            AppSettingHelper.__global__ = u.load()
        return AppSettingHelper.__global__

    @staticmethod
    def reload():
        u = UserSettingHelper("root")
        AppSettingHelper.__global__ = u.load()
        return AppSettingHelper.__global__

    @staticmethod
    def get(key, default_=None):
        val = AppSettingHelper.__global__.get(key)
        if val:
            return val
        return default_

    @staticmethod
    def set(dic_obj):
        v = json.dumps(dic_obj, cls=JsonEncoder)
        cnn = SessionFactory.new()
        item = cnn.query(Setting).filter(Setting.owner_ == "root").limit(1).scalar()
        if item:
            item.val_ = v
            cnn.commit()
        else:
            obj = Setting()
            obj.owner_ = "root"
            obj.val_ = v
            cnn.add(obj)
            cnn.commit()
