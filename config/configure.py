__author__ = 'tinyms'

__export__ = ["DefaultWebConfig"]

from sqlalchemy import create_engine
from tinyms.core.annotation import IWebConfig


class DefaultWebConfig(IWebConfig):
    def database_driver(self):
        #return create_engine("sqlite+pysqlite:///arch.data", echo=True)
        #return create_engine("postgresql+psycopg2://postgres:1@localhost/ArchX", echo=True)
        return create_engine("mssql+pyodbc://sa:1@localhost/tinyms",
                             echo=True, convert_unicode=True, pool_size=500, max_overflow=50)

    def debug(self):
        return True

    def server_port(self):
        return 8080