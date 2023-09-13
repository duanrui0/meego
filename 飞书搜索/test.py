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
import datetime

if __name__ == '__main__':
    a = {
        "code": 0,
        "data": {
            "data_source": {
                "description": "",
                "icon_url": "",
                "id": "7275616477498523649",
                "is_exceed_quota": 'false',
                "name": "datawind",
                "schema_id": "datawind_schema_id",
                "state": 0
            }
        },
        "msg": "success"
    }
    b=a['data']['data_source']['id']
    # print(b)
    c='2021-12-07 20:33:39'
    timestamp = str(int(datetime.datetime.strptime(c, '%Y-%m-%d %H:%M:%S').timestamp()))
    # print(timestamp)
    t=[1,3,3]
    a='仪表盘'
    b=''
    for i in t :
        if a=='数据集':
            b='lose'
        elif a=='仪表盘':
            b='win'
        print(a,b)