import os
from contextlib import contextmanager
import pymysql
from meego.util.utils import time_cost


@contextmanager
def init_conn(mysql_dict):
    db_conn = pymysql.connect(
        host=mysql_dict['host'],
        user=mysql_dict['user'],
        password=mysql_dict['password'],
        database=mysql_dict['database']
    )
    try:
        yield db_conn
    finally:
        db_conn.close()


# 初始化表
def init_tables(conn, tables):

    print("初始化表开始......................")
    cursor = conn.cursor()
    try:
        # # 使用 execute() 方法执行 SQL，如果表存在则删除
        # for key, value in tables.items():
        #     cursor.execute("DROP TABLE IF EXISTS " + value)

        # 使用预处理语句创建元数据表
        proj_path = os.path.dirname(os.path.dirname(__file__))
        with open(proj_path + "/resources/meego_meta.ddl.sql", 'r+') as f:
            lines = f.readlines()
            if len(lines) > 0:
                content = "".join(lines)
                drop_sql = "truncate table " + tables['metaData']
                sql = content.format(tables['metaData'])
                cursor.execute(drop_sql)
                cursor.execute(sql)

        # 使用预处理语句创建数据表
        with open(proj_path + "/resources/meego_data.ddl.sql", 'r+') as f:
            lines = f.readlines()
            if len(lines) > 0:
                content = "".join(lines)
                drop_sql = "truncate table " + tables['workData']
                sql = content.format(tables['workData'])
                cursor.execute(drop_sql)
                cursor.execute(sql)

    except Exception as e:
        print(e)
        print(e.__context__)
    finally:
        cursor.close()
    print("初始化表完成......................")


@time_cost
def execute_update(conn, sql, data: list):
    # 使用 cursor() 方法创建一个游标对象 cursor
    cursor = conn.cursor()
    try:
        # 执行sql语句
        cursor.executemany(sql, data)
        # 提交到数据库执行
        conn.commit()
    except Exception as e:
        print(e)
        print(e.__context__)
        print(" 数据更新异常: " + sql)
    finally:
        cursor.close()
