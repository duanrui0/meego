# ********************************************************************
# Author: deep as sea
# Create by: 2023/8/28
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
import json

import requests


def get_fsu_token():
    url = 'https://project.feishu.cn/open_api/authen/plugin_token'
    payload = json.dumps({
        "plugin_id": "MII_64BF73E313814002",
        "plugin_secret": "CC490B6545429495228191E74962621A"
    })
    headers = {
        'Content-Type': 'application/json',
        'Authorization':'Bearer t-7f1bcd13fc57d46bac21793a18e560'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    # print(response.text)
    data = json.loads(response.text)
    if 'data' in data and data['data'] != '':
        # print('data:%s' % data['data'])
        return data['data']['token']
    else:
        raise Exception('获取data异常!')
if __name__ == '__main__':
    print('获取token成功    '+get_fsu_token())