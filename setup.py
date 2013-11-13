__author__ = 'tinyms'

#import sys
from cx_Freeze import setup, Executable

base = None
# if sys.platform == "win32":
#     base = "Win32GUI"

setup(
    name="ValidWork",
    version="1.0",
    description="Valid Work For Company",
    options={"build_exe": {"includes": ["psycopg2._psycopg", "tinyms.core.orm",
                                        "sqlalchemy.dialects.sqlite", "sqlalchemy.dialects.postgresql"]}},
    executables=[Executable(script="ArchiveX.py",
                            targetName="ValidWork.exe",
                            icon="static/images/web_card.ico",
                            base=base)])
