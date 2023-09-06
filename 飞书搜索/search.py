# ********************************************************************
# Author: deep as sea
# Create by: 2023/9/6
# Description: 
# Update: Task Update Description
# ********************************************************************
# -*- coding: utf-8 -*-
# 
#                     _ooOoo_
#                    o8888888o
#                    88" . "88
#                    (| -_- |)
#                     O\ = /O
#                 ____/`---'\____
#               .   ' \\| |// `.
#                / \\||| : |||// \
#              / _||||| -:- |||||- \
#                | | \\\ - /// | |
#              | \_| ''\---/'' | |
#               \ .-\__ `-` ___/-. /
#            ___`. .' /--.--\ `. . __
#         ."" '< `.___\_<|>_/___.' >'"".
#        | | : `- \`.;`\ _ /`;.`/ - ` : | |
#          \ \ `-. \_ __\ /__ _/ .-` / /
#  ======`-.____`-.___\_____/___.-`____.-'======
#                     `=---='
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#          佛祖保佑       永无BUG
import os
import datetime

import requests
import json


# 获取token
def get_token():
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    payload = json.dumps({
        "app_id": "cli_a46f1a5de5fc900e"
        , "app_secret": "sQQSJfmQPrSavmWF5Q8LIfso7QmHTP6A"
    })
    headers = {
        'Content-Type': 'application/json;charset=utf-8'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    data = json.loads(response.text)
    print(data)
    if 'tenant_access_token' in data and data['tenant_access_token'] != '':
        # print('data:%s' % data['data'])
        return data['tenant_access_token']
    else:
        raise Exception('获取data异常!')


# 第一步创建数据范式
def post_schemas():
    url = 'https://open.feishu.cn/open-apis/search/v2/schemas'
    headers = {
        "Authorization": "Bearer " + get_token(),
        'Content-Type': 'application/json;charset=utf-8',
    }
    payload = json.dumps(
        {
            "display": {
                "card_key": "search_common_card",
                "fields_mapping": [
                    {
                        "display_field": "summary",
                        "data_field": "summary: ${summary}"
                    },
                    {
                        "display_field": "footer",
                        "data_field": "footer ${footer}"
                    }
                ]
            },
            "properties": [

                {
                    "is_searchable": 'true',
                    "search_options": {
                        "enable_number_suffix_match": 'false',
                        "enable_semantic_match": 'true',
                        "enable_camel_match": 'false',
                        "enable_exact_match": 'false',
                        "enable_prefix_match": 'false'
                    },
                    "name": "summary",
                    "type_definitions": {},
                    "type": "text",
                    "is_returnable": 'true'
                }, {
                    "is_searchable": 'true',
                    "search_options": {
                        "enable_number_suffix_match": 'false',
                        "enable_semantic_match": 'true',
                        "enable_camel_match": 'false',
                        "enable_exact_match": 'false',
                        "enable_prefix_match": 'false'
                    },
                    "name": "footer",
                    "type_definitions": {},
                    "type": "text",
                    "is_returnable": 'true'
                }
            ],
            "schema_id": "dhl_schema_id"
        }
    )
    response = requests.request("POST", url, headers=headers, data=payload)

    print(response.text)


# 第二步根据数据范式创建数据源
def post_data_sources():
    url = 'https://open.feishu.cn/open-apis/search/v2/data_sources'
    headers = {
        "Authorization": "Bearer " + get_token(),
        'Content-Type': 'application/json;charset=utf-8',
    }
    # 根据数据范式，设置数据源，就相当于搜索中的分类
    payload = json.dumps({
        "name": "zzh",
        "description": "",
        "icon_url": "",
        "schema_id": "dhl_schema_id",
        "template": "",
        "state": 0
    })
    response = requests.request("POST", url, headers=headers, data=payload)

    print(response.text)

    # 第三步根据数据源往数据源中写数据


def post_items():
    url = 'https://open.feishu.cn/open-apis/search/v2/data_sources/' + post_data_sources()['data']['id'] + '/items'
    # 这里的7274868529462476802是从第二步返回的id得到，因为第一步第二步只需要执行一次，所以就在这里将id直接放在这里
    headers = {
        "Authorization": "Bearer " + get_token(),
        'Content-Type': 'application/json;charset=utf-8',
    }
    body = json.dumps(
        {
            "id": "1", #id可传
            "acl": [
                {
                    "access": "allow",
                    "value": "everyone",
                    "type": "user"
                }
            ],
            "metadata": {
                "source_url": "https://hailongservice.atlassian.net/browse/BFCE-11",
                # 这个就传url吧，没啥说的
                "title": "B2-17",
                # 传项目空间
                "update_time": 1645595280
                #时间就传时间
            },
            "structured_data": "{\"summary\":\"学清B2-17\",\"footer\":\"测试学清会议室2楼\"}"
        #summary传的这个空间的标题，然后fotter相当于介绍
        })
    response = requests.request("POST", url, headers=headers, data=body)

    print(response.text)


# 获取hive任务
def exe_sql(sql):
    cmd = '/opt/tiger/hive_deploy/bin/hive -e "%s"' % sql
    command = (cmd)
    r = os.popen(command)
    rsp = r.readlines()
    return rsp


def select_data():
    sql = "SELECT   concat(id_app,   '##&##',name_app,  '##&##',item_key, '##&##', item_name,  '##&##', owner,   '##&##',item_type, '##&##',  create_time,'##&##',    url, '##&##',   row_id)     FROM   dataleap_operation.ods_bi_operation_details_df where p_date = '2023-08-30' ;"
    rsp = exe_sql(sql)
    bi_operation_details = []
    for data in rsp:
        item = data.split("##&##")
        bi_operation_details.append(item)

    return bi_operation_details
def search_demo():
    # 查询具体的值
    result_list = select_data()
    result_list = result_list[:-4]
    for array in result_list:
        print(array)
        项目空间 = array[1]
        名称=array[3]
        对象类型=array[5]
        owner=array[4]
        url=array[7]
        timestamp = int(datetime.datetime.strptime(array[6], '%Y-%m-%d %H:%M:%S').timestamp())
        post_items(项目空间,名称,对象类型,owner,timestamp,url)

if __name__ == "__main__":
    print("完成 bye~")
