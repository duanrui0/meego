import re
from typing import Optional

from core.cache import user_dict

from util import request, config
import os
import json
import csv
def get_header():
    header = {
        'Content-Type': 'application/json',
        'X-Plugin-Token': get_fsu_token(),
        'X-USER-KEY': '7137587176702885916'
    }
    return header

# 1.获取插件凭证
def get_fsu_token():
    url = 'https://project.feishu.cn/open_api/authen/plugin_token'
    header = {'Content-Type': 'application/json'}
    payload = {
        "plugin_id": "MII_64BF73E313814002",
        "plugin_secret":"CC490B6545429495228191E74962621A"
    }
    result = request.post(url, header=header, payload=payload)
    token = result['data']['token']
    return token
# 2.获取空间列表
def get_projects():
    url='https://project.feishu.cn/open_api/projects'
    header = get_header()
    body = {
        "user_key": "7137587176702885916"
    }
    result = request.post(url,header=header,payload=body)
    project_key=result['data']
    return project_key
# 获取空间详情
def get_projects_detail():
    url='https://project.feishu.cn/open_api/projects/detail'
    header=get_header()
    body={
        "user_key": "7137587176702885916",
        "project_keys": get_projects(),
        "simple_names": [
            "sdotest"
        ]
    }
    result=request.post(url,header=header,payload=body)
    data=result['data']
    return data
# 3.获取视图列表
def get_version_list():
    url='https://project.feishu.cn/open_api/64b9ea9a523ec554280f4247/view_conf/list'
    header=get_header()
    body={
        "project_key": "64b9ea9a523ec554280f4247",
        "work_item_type_key": "story"
    }
    result=request.post(url,header=header,payload=body)
    data=result['data']
    list = []
    for re in data :
        list.append(re['view_id'])

    return  list
#4.获取视图下工作项列表
def get_version_work_list():
    data=[]
    for id in get_version_list():
        url='https://project.feishu.cn/open_api/64b9ea9a523ec554280f4247/fix_view/'+id+'?page_size=22&page_num=1'
        header=get_header()
        result=request.get(url,header=header)
        aa=result['data']['work_item_id_list']
        data.append(aa)
    data = [item for sublist in data for item in sublist]

    return data
# 5.获取工作项详情
def get_work_item_query():
    url="https://project.feishu.cn/open_api/64b9ea9a523ec554280f4247/work_item/story/query?project_key=64b9ea9a523ec554280f4247&work_item_type_key=story"
    header=get_header()

    body={
        "work_item_ids":get_version_work_list()
        }
    result = request.post(url, header=header, payload=body)
    data=json.dumps(result)

    aa=json.loads(data)
    # ww=aa['data']
    numbers = list(range(0, len(get_version_work_list())))
    field = []
    for item in aa['data']:
        work_id=item['id']
        work_id11='id'
        work_name=item['name']
        fields=item['fields']
        work_name11='name'
        json_data={}
        json_data[work_id11] = work_id
        json_data[work_name11] = work_name

        for item2 in fields:
            field_key=item2['field_key']
            field_value=item2['field_value']
            # aa = {field_key: field_value}
            json_data[field_key]=field_value
            # json_str=json.dumps(aa)
            # print(json_str)
        json_str=json.dumps(json_data)

        field.append(json_str)


    return  field
# 6.获取空间字段
def get_project_name():
    url='https://project.feishu.cn/open_api/64b9ea9a523ec554280f4247/field/all'
    header=get_header()
    body={
        "project_key": "64b9ea9a523ec554280f4247",
        "work_item_type_key":"story"
    }
    result =request.post(url,header=header,payload=body)
    # data = result
    field_key_name={}
    # for i in result():
    data=json.dumps(result)
    data=json.loads(data)
    # 获取第一层数据
    subdata1 = data["data"]
    # 访问第二层数据的键值对
    for i in range(0,561):
        key = subdata1[i]['field_key']
        name = subdata1[i]['field_name']
        field_key_name[key]=name
        # field_key_name.append(name)
    # value1 = subdata1["subkey1"]

    return field_key_name


# 2.1将数据写入csv
def api_load_excel(result, item_result,writer):
# def api_load_excel():

    # print(result)
    result=get_work_item_query()
    item_result=get_project_name()
    # print([result,item_result])
    writer.writerow([result,item_result])
    # print(result)

# 2.2将数据写入hive表
def hive_load_table(table_name, csv_name):
    # 分区字段
    # udt = (datetime.date.today() + datetime.timedelta(days=-1)).strftime("%Y-%m-%d")
    udt = '${date}'
    hour = '${hour}'
    # hive load command
    c = "/opt/tiger/hive_deploy/bin/hive -e " + "\"load data local inpath '" + csv_name + "' overwrite into table " + table_name + " partition (p_date='"+udt+"',hour='"+hour+"') ;\""
    print(c)
    command = (c)
    os.system(command)
# 获取具体的值
def get_item_value():
    # return get_project_name()['RM09 VDR是否符合健康度/成熟度规则？']
    numbers = list(range(0, len(get_work_item_query())))
    wsd=[]


    for item in numbers:
        # 获取field_name对应的具体field_key
        data = get_project_name()
        result_keys = [key for key, value in data.items() if value == '需求简述']

        aa=get_work_item_query()[item]
        bb=json.loads(aa)
        id=bb['id']
        name=bb[result_keys[0]]
        rm09=bb['field_044cf4']['label'] if 'field_044cf4' in bb else None #RM09 VDR是否符合健康度/成熟度规则？

        alive=bb['field_5849dc'] if 'field_5849dc' in str(bb) else None #人工确认
        nc_number=bb['field_210f1a'] if 'field_210f1a' in bb else None #NC数量1-7
        nobody=bb['field_2e534b'] if 'field_2e534b' in bb else None  #自动检查信息
        use_version=bb['field_9348b6'] if 'field_9348b6' in bb else None
        wsd.append([id,name,rm09,alive,nc_number,nobody,use_version])

    return wsd
# 获取要更新的值
def get_item_updata():
    numbers = list(range(0, len(get_work_item_query())))
    wsd = []

    for item in numbers:
        # 获取field_name对应的具体field_key
        data = get_project_name()
        result_keys = [key for key, value in data.items() if value == '需求简述']

        aa = get_work_item_query()[item]
        bb = json.loads(aa)
        print(bb)
    return numbers

def find_key(dictionary, target_value):
    for key, value in dictionary.items():
        if value == target_value:
            return key
    return None
if __name__ == '__main__':
    # data=json.loads(get_project_name())
    # target_value = "人工确认"
    # result_key = find_key(data, target_value)
    # if result_key:
    #     print(f"找到值为 {target_value} 的 key: {result_key}")
    # else:
    #     print("未找到匹配的 key")
    # data=get_project_name()
    # result_keys = [key for key, value in data.items() if value == '需求简述']
    # print(result_keys[0])
    print(get_item_updata())