from meego.conn.mysql import *
from meego.util import config


def load2mysql(meta: list, data: list, is_init: bool = True):
    # 初始化
    para = {
        'host': config.mysql_host,
        'user': config.mysql_user_name,
        'password': config.mysql_user_pass,
        'database': config.mysql_database
    }

    table_dict = {
        'metaData': config.mysql_stored_meego_meta_data,
        'workData': config.mysql_stored_meego_data
    }
    meego_table_sql = """
        INSERT INTO {} VALUES (
            %s,%s,%s,%s,
            %s,%s,%s,%s,
            %s,%s,%s,%s,
            %s,%s,%s,%s,
            %s,%s,%s,%s,
            %s,%s,%s,%s
        )
    """.format(config.mysql_stored_meego_data)
    meta_table_sql = """
        INSERT INTO {} VALUES (
            %s,%s,%s,%s,
            %s,%s,%s
        )
    """.format(config.mysql_stored_meego_meta_data)

    with init_conn(para) as conn:
        if is_init:
            # 初始化表
            init_tables(conn, table_dict)
        execute_update(conn, meta_table_sql, meta)
        execute_update(conn, meego_table_sql, data)