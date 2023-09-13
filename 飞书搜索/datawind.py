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
                        "data_field": "assignee: ${summary}"
                    },
                    {
                        "display_field": "footer",
                        "data_field": "this is created by ${owner_name}|${assign_time}"
                    },
                    {
                        "display_field": "tag1",
                        "data_field": "${result}"
                    }
                ]
            },
            "properties": [

                {
                    "is_searchable": 'false',
                    "name": "meeting",
                    "type_definitions": {},
                    "type": "text",
                    "is_returnable": 'true',
                    "is_filterable": 'true',
                    "filter_options": {
                        "display_name": "所在项目空间",
                        "filter_type": "searchable",
                        "reference_datasource_id": "id"
                        # 这个reference_datasource_id填上一步search里面的source_id
                    }
                },
                {
                    "is_searchable": 'true',
                    "search_options": {
                        "enable_number_suffix_match": 'true',
                        "enable_semantic_match": 'false',
                        "enable_camel_match": 'true',
                        "enable_exact_match": 'true',
                        "enable_prefix_match": 'true'
                    },
                    "name": 'owner_name',
                    "type_definitions": {},
                    "is_returnable": 'true',
                    "type": "tinytext"
                },
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
                },
                {
                    "is_searchable": 'false',
                    "name": "assign_time",
                    "type_definitions": {},
                    "type": "timestamp",
                    "is_returnable": 'true',
                    "is_filterable": 'true',
                    "filter_options": {
                        "display_name": "执行时间",
                        "associated_smart_filter": "date",
                        "filter_type": "time"
                    }
                },
                {
                    "name": "result",
                    "type_definitions": {
                        "tag": [
                            {
                                "color": "blue",
                                "name": "win",
                                "text": "数据集"
                            },
                            {
                                "color": "blue",
                                "name": "lose",
                                "text": "仪表盘"
                            }
                        ]
                    },
                    "type": "tag",
                    "is_returnable": 'true',
                    "is_filterable": 'true',
                    "filter_options": {
                        "display_name": "对象类型",
                        "filter_type": "predefine_enum",
                        "predefine_enum_values": [
                            {
                                "name": "win",
                                "text": "数据集"
                            },
                            {
                                "name": "lose",
                                "text": "仪表盘"
                            }
                        ]
                    }
                }
            ],
            "schema_id": "datawind_schema_id"
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
        "name": "datawind",
        "description": "",
        "icon_url": "",
        "schema_id": "datawind_schema_id",
        "template": "search_common_card",
        "state": 0
    })
    response = requests.request("POST", url, headers=headers, data=payload)

    print(response.text)

    # 第三步根据数据源往数据源中写数据


# 第三步根据数据源往数据源中写数据
def post_items(项目空间,名称,owner,timestamp,urls,searid,idr,仪表盘还是数据集):
    url = 'https://open.feishu.cn/open-apis/search/v2/data_sources/7276391157616754691/items'
    # 这里的7274868529462476802是从第二步返回的id得到，因为第一步第二步只需要执行一次，所以就在这里将id直接放在这里
    headers = {
        "Authorization": "Bearer " + get_token(),
        'Content-Type': 'application/json;charset=utf-8',
    }
    body = json.dumps(
        {
            "id": idr,
            "acl": [
                {
                    "access": "allow",
                    "value": "everyone",
                    "type": "user"
                }
            ],
            "metadata": {
                "source_url": urls,
                "title": 名称,
                "update_time":timestamp
            },
            "structured_data": "{\"owner_name\":\""+owner+"\",\"summary\":\""+项目空间+"\",\"assign_time\":\""+timestamp+"\",\"result\":\""+仪表盘还是数据集+"\", \"meeting\":\""+searid+"\"}"
        })
    response = requests.request("POST", url, headers=headers, data=body)
    print(body)
    print(response.text)

def delete_item(idr):
    url='https://open.feishu.cn/open-apis/search/v2/data_sources/7276391157616754691/items/'+idr+'\''
    headers = {
        "Authorization":"Bearer "+get_token()
    }
    payload={}
    response = requests.request("DELETE", url, headers=headers, data=payload)
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
        if 对象类型 == '数据集':
            b = 'win'
        elif 对象类型 == '仪表盘':
            b = 'lose'
        elif 对象类型 == '可视化建模':
            b = 'jianmo'
        elif 对象类型 == '大屏':
            b = 'daping'
        仪表盘还是数据集=b
        owner=array[4]
        url=array[7]
        timestamp = str(int(datetime.datetime.strptime(array[6], '%Y-%m-%d %H:%M:%S').timestamp()))
        searid=str(array[0])
        idr=str(array[8])
        type=''
        print(项目空间,名称,owner,timestamp,url,searid,idr)
        if type=='删除':
            delete_item(idr)
        else:
            post_items(项目空间,名称,owner,timestamp,url,searid,idr,仪表盘还是数据集)

if __name__ == "__main__":
    search_demo()
    print('bye~')
