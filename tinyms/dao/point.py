__author__ = 'tinyms'

from sqlalchemy import func
from tinyms.core.orm import SessionFactory
from tinyms.core.entity import SecurityPoint


#动态权限增删改，像树节点
class DynamicPointHelper():
    def __init__(self, c, g):
        self.category = c
        self.group = g

    def add(self, key, desc):
        sf = SessionFactory.new()
        num = sf.query(func.count(SecurityPoint.id)).filter(SecurityPoint.key_ == key).limit(1).scalar()
        if num > 0:
            return False
        sp = SecurityPoint()
        sp.category = self.category
        sp.group_ = self.group
        sp.key_ = key
        sp.description = desc
        sf.add(sp)
        sf.commit()
        return True

    def update(self, key, desc):
        sf = SessionFactory.new()
        row = sf.query(SecurityPoint).filter(SecurityPoint.key_ == key).limit(1).scalar()
        if row:
            row.description = desc
            sf.commit()
            return True
        return False

    def delete(self, key):
        sf = SessionFactory.new()
        row = sf.query(SecurityPoint).filter(SecurityPoint.key_ == key).limit(1).scalar()
        sf.delete(row)
        sf.commit()
        return True