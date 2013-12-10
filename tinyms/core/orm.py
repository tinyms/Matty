__author__ = 'tinyms'

import json
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import relationship, backref, class_mapper
from sqlalchemy import Column, Integer, ForeignKey, Table, String
from sqlalchemy.orm import sessionmaker
from tinyms.core.common import Utils


Entity = declarative_base()


class SessionFactory():
    entitys = dict()
    __engine__ = None
    __table_name_prefix__ = "archx_"

    @staticmethod
    def table_name_prefix(name):
        SessionFactory.__table_name_prefix__ = name

    @staticmethod
    def new():
        if SessionFactory.__engine__:
            return sessionmaker(bind=SessionFactory.__engine__)()
        return None

    @staticmethod
    def create_tables():
        if SessionFactory.__engine__:
            Entity.metadata.create_all(SessionFactory.__engine__)


def entity_manager():
    def ref_pattern(cls):
        if not SessionFactory.entitys.get(cls):
            key = "%s.%s" % (cls.__module__, cls.__qualname__)
            SessionFactory.entitys[cls.__tablename__] = key
        return cls

    return ref_pattern


class Simplify():
    """
    简化实体创建及可以JSON化实体数据
    """
    id = Column(Integer, primary_key=True)

    @declared_attr
    def __tablename__(self):
        print(self)
        return "%s%s" % (SessionFactory.__table_name_prefix__, self.__name__.lower())

    def dict(self, dict_=None):
        """
        1, object to map
        2, map to object
        :param dict_:
        :return:
        """
        if not dict_:
            columns = [c.key for c in class_mapper(self.__class__).columns]
            return dict((c, getattr(self, c)) for c in columns)
        else:
            metas = self.cols_meta()
            for k, v in dict_.items():
                print(k, v)
                if not hasattr(self, k):
                    continue
                for m in metas:
                    if m["name"] == k:
                        if m["type"] == "int":
                            if type(v) == str:
                                setattr(self, k, Utils.parse_int(v))
                            else:
                                setattr(self, k, v)
                        elif m["type"] == "numeric":
                            if type(v) == str:
                                setattr(self, k, Utils.parse_float(v))
                            else:
                                setattr(self, k, v)
                        elif m["type"] == "datetime":
                            if type(v) == str:
                                setattr(self, k, Utils.parse_datetime(v))
                            else:
                                setattr(self, k, v)
                        elif m["type"] == "date":
                            if type(v) == str:
                                setattr(self, k, Utils.parse_date(v))
                            else:
                                setattr(self, k, v)
                        elif m["type"] == "time":
                            if type(v) == str:
                                setattr(self, k, Utils.parse_time(v))
                            else:
                                setattr(self, k, v)
                        else:
                            setattr(self, k, v)
                pass
            pass

    def cols_meta(self):
        cols = class_mapper(self.__class__).columns
        metas = list()
        for col in cols:
            meta = dict()
            meta["pk"] = col.primary_key
            # is a set()
            meta["fk"] = col.foreign_keys
            meta["name"] = col.key
            meta["nullable"] = col.nullable
            meta["unique"] = col.unique
            meta["autoincrement"] = col.autoincrement
            meta["default"] = col.default
            if isinstance(col.type, String) and col.type.length:
                meta["length"] = col.type.length
            else:
                meta["length"] = 0
            type_name = col.type.__visit_name__
            if ["string", "text", "unicode", "unicode_text"].count(type_name) == 1:
                type_name = "string"
            elif ["integer", "small_integer", "big_integer", "boolean"].count(type_name) == 1:
                type_name = "int"
            elif ["numeric", "float"].count(type_name) == 1:
                type_name = "numeric"
                # elif ["datetime","date","time"].count(type_name)==1:
            #     type_name = "date"
            meta["type"] = type_name
            metas.append(meta)
        return metas

    def json(self):
        return json.dumps(self.dict())

    def __repr__(self):
        return "<%s%s>" % (self.__tablename__.capitalize(), self.dict())


def one_to_one(foreign_entity_name):
    """
    一对一，比如: 从表对主表
    一旦映射成功，彼此获取到对方表名实体对象变量，也就是你可以直接访问我，我可以直接访问你
    :param foreign_entity_name: 目标实体名
    :return:
    """

    def ref_table(cls):
        foreign_entity_name_lower = foreign_entity_name.lower()
        foreign_table_name = "%s%s" % (SessionFactory.__table_name_prefix__, foreign_entity_name_lower)
        setattr(cls, '{0}_id'.format(foreign_entity_name_lower),
                Column(Integer, ForeignKey('{0}.id'.format(foreign_table_name), ondelete="CASCADE")))
        setattr(cls, foreign_entity_name_lower,
                relationship(foreign_entity_name,
                             backref=backref(cls.__name__.lower(), uselist=False)))
        return cls

    return ref_table


def many_to_one(foreign_entity_name):
    """
    多对一，一对多共用这种形式
    一旦映射成功，one的一方将自动拥有many一方集合变量名`表名s`
    :param foreign_entity_name: 目标实体名
    :return:
    """

    def ref_table(cls):
        foreign_entity_name_lower = foreign_entity_name.lower()
        foreign_table_name = "%s%s" % (SessionFactory.__table_name_prefix__, foreign_entity_name_lower)

        if foreign_entity_name == cls.__name__:
            foreign_entity_name_lower = "parent"

        if foreign_entity_name == cls.__name__:
            setattr(cls, '{0}_id'.format(foreign_entity_name_lower),
                    Column(Integer, ForeignKey('{0}.id'.format(foreign_table_name))))
            setattr(cls, foreign_entity_name_lower,
                    relationship(foreign_entity_name, backref=backref("children", remote_side=cls.id)))
        else:
            setattr(cls, '{0}_id'.format(foreign_entity_name_lower),
                    Column(Integer, ForeignKey('{0}.id'.format(foreign_table_name), ondelete="CASCADE")))
            setattr(cls, foreign_entity_name_lower,
                    relationship(foreign_entity_name, backref=backref(cls.__name__.lower() + 's')))

        return cls

    return ref_table


def many_to_many(foreign_entity_name):
    """
    多对多，装饰到有关联关系的任意实体之上
    一旦映射成功，彼此皆可获取对方`表名s`集合变量
    :param foreign_entity_name: 目标实体名
    :return:
    """

    def ref_table(cls):
        target_name = foreign_entity_name.lower()
        self_name = cls.__name__.lower()
        association_table = Table(
            '{0}{1}_{2}_relationships'.format(SessionFactory.__table_name_prefix__, self_name, target_name),
            Entity.metadata,
            Column('{0}_id'.format(target_name), Integer,
                   ForeignKey('{0}{1}.id'.format(SessionFactory.__table_name_prefix__, target_name),
                              ondelete="CASCADE")),
            Column('{0}_id'.format(self_name), Integer,
                   ForeignKey('{0}{1}.id'.format(SessionFactory.__table_name_prefix__, self_name), ondelete="CASCADE"))
        )

        setattr(cls, target_name + 's',
                relationship(foreign_entity_name, secondary=association_table,
                             backref=backref(cls.__name__.lower() + 's', lazy='dynamic')))
        return cls

    return ref_table