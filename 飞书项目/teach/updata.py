# -*- coding: utf-8 -*-
# ********************************************************************
# Author: 今晚大老虎先森
# Create by: 2023-08-03 11:38:02.000
# Description:
# Update: Task Update Description
# ********************************************************************
import requests
import json
import csv
import os


# 1.获取插件凭证
def get_fsu_token():
    url = 'https://project.feishu.cn/open_api/authen/plugin_token'
    payload = json.dumps({
        "plugin_id": "MII_64BF73E313814002",
        "plugin_secret": "CC490B6545429495228191E74962621A"
    })
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    # print(response.text)
    data = json.loads(response.text)
    if 'data' in data and data['data'] != '':
        # print('data:%s' % data['data'])
        return data['data']['token']
    else:
        raise Exception('获取data异常!')


def get_header():
    header = {
        'Content-Type': 'application/json',
        'X-Plugin-Token': get_fsu_token(),
        'X-USER-KEY': '7137587176702885916'
    }
    return header


# 2.获取空间列表
def get_projects():
    url = 'https://project.feishu.cn/open_api/projects'
    header = get_header()
    body = json.dumps({
        "user_key": "7137587176702885916"
    })
    response = requests.request('POST', url, headers=header, data=body)
    print(response.text)
    data = json.loads(response.text)
    return data['data']


# 3.更新测试
def put_item():
    # 经过获取数据的field_key,field_type_key,field_value,确定测试下面的数据
    # name:主计划9_VM,  "id": 13212756,
    # 测试节点{
    #         "field_alias": "",
    #         "field_key": "field_cd2a76",
    #         "field_type_key": "radio",
    #         "field_value": {
    #             "label": "N",
    #             "value": "k2uezo1hr"
    #         }
    #     }
    # RM01 需求来源是否完整？
    url = 'https://project.feishu.cn/open_api/64b9ea9a523ec554280f4247/work_item/story/13212756'
    header = get_header()
    body = json.dumps({
        "update_fields": [
            {
                "field_alias": "",
                "field_key": "field_cd2a76",
                "field_type_key": "radio",
                "field_value": {
                    "label": "N",
                    "value": "k2uezo1hr"
                }
            }
        ]
    })
    response = requests.request('PUT', url, headers=header, data=body)
    print(response)
    return response


if __name__ == '__main__':
    put_item()
