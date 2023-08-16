import subprocess
import sys
import pandas as pd

from meego.util.utils import time_cost


@time_cost
def execute(result_lists, table, partition, client):

    df = pd.DataFrame(result_lists[1:], columns=result_lists[0])
    # analyze
    # save to local path
    df.to_parquet(table+'.parquet.gzip', compression='gzip')
    # print(pd.read_parquet(table+'.parquet.gzip'))
    # store data
    subprocess.run(
        "hdfs dfs -put -f "+table+".parquet.gzip hdfs://haruna/home/byte_eps_dsc_data/warehouse/eps_dsc_data.db/"+table+".parquet.gzip",
        shell=True)  # ignore_security_alert
    sql = "load data inpath 'hdfs://haruna/home/byte_eps_dsc_data/warehouse/eps_dsc_data.db/"+table+".parquet.gzip' OVERWRITE into table "+table+" PARTITION (date='"+partition+"');"
    job = client.execute_query(user_name='chensong.csongbj', query=sql)
    if job.is_success():
        print('--------- [store data ok: 3/3] -----------')
    else:
        # if job is faild, sys.exit() can cause dorado to retry;
        # otherwise, dorado will think task is successfully executed.
        sys.exit(1)  # non-zero for abnormal exit

