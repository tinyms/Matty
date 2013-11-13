__author__ = 'tinyms'

__export__ = ["DefaultWebConfig"]

from sqlalchemy import create_engine
from tinyms.core.annotation import IWebConfig


class DefaultWebConfig(IWebConfig):
    def database_driver(self):
        return create_engine("sqlite+pysqlite:///arch.data", echo=True)
        #return create_engine("postgresql+psycopg2://postgres:1@localhost/ArchX", echo=True)

    def debug(self):
        return True

    def server_port(self):
        return 8888