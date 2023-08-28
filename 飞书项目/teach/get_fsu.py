# -*- coding: utf-8 -*-
# ********************************************************************
# Author: 大瓶矿泉水掺水了
# Create by: 2023-08-02 16:11:10.000
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


# 3.获取视图列表
def get_version_list():
    url = 'https://project.feishu.cn/open_api/64b9ea9a523ec554280f4247/view_conf/list'
    header = get_header()
    body = json.dumps({
        "project_key": "64b9ea9a523ec554280f4247",
        "work_item_type_key": "story"
    })
    result = requests.request('POST', url, headers=header, data=body)
    data = json.loads(result.text)
    data = data['data']
    list = []
    for re in data:
        list.append(re['view_id'])

    return list


# 4.获取视图下工作项列表
def get_version_work_list():
    data = []
    for id in get_version_list():
        url = 'https://project.feishu.cn/open_api/64b9ea9a523ec554280f4247/fix_view/' + id + '?page_size=22&page_num=1'
        header = get_header()
        result = requests.request('GET', url, headers=header)
        result = json.loads(result.text)
        aa = result['data']['work_item_id_list']
        data.append(aa)
    data = [item for sublist in data for item in sublist]

    return data


# 5.获取工作项详情
def get_work_item_query():
    url = "https://project.feishu.cn/open_api/64b9ea9a523ec554280f4247/work_item/story/query?project_key=64b9ea9a523ec554280f4247&work_item_type_key=story"
    header = get_header()
    body = json.dumps({
        "work_item_ids": get_version_work_list()
    })
    result = requests.request('POST', url, headers=header, data=body)
    # data=json.dumps(result.text)
    # print(data)
    aa = json.loads(result.text)
    numbers = list(range(0, len(get_version_work_list())))
    field = []
    for item in aa['data']:
        work_id = item['id']
        work_id11 = 'id'
        work_name = item['name']
        fields = item['fields']
        work_name11 = 'name'
        json_data = {}
        json_data[work_id11] = work_id
        json_data[work_name11] = work_name

        for item2 in fields:
            field_key = item2['field_key']
            field_value = item2['field_value']
            # aa = {field_key: field_value}
            json_data[field_key] = field_value
            # json_str=json.dumps(aa)
            # print(json_str)
        json_str = json.dumps(json_data)

        field.append(json_str)

    return field


# 6.获取空间字段
def get_project_name():
    url = 'https://project.feishu.cn/open_api/64b9ea9a523ec554280f4247/field/all'
    header = get_header()
    body = json.dumps({
        "project_key": "64b9ea9a523ec554280f4247",
        "work_item_type_key": "story"
    })
    result = requests.request('POST', url, headers=header, data=body)
    # data = result
    field_key_name = {}
    # for i in result():
    # data=json.dumps(result.text)
    data = json.loads(result.text)

    # 获取第一层数据
    subdata1 = data["data"]
    # 访问第二层数据的键值对
    for i in range(0, 561):
        key = subdata1[i]['field_key']
        name = subdata1[i]['field_name']
        field_key_name[key] = name
        # field_key_name.append(name)
    # value1 = subdata1["subkey1"]

    return field_key_name


# 将数据写入csv
def api_load_excel(result, writer):
    # print(result)
    # items_list = [result,item_result]
    writer.writerow(result)


def hive_load_table(table_name, csv_name):
    # 分区字段
    # udt = (datetime.date.today() + datetime.timedelta(days=-1)).strftime("%Y-%m-%d")
    udt = '${date}'
    hour = '${hour}'
    # hive load command
    c = "/opt/tiger/hive_deploy/bin/hive -e " + "\"load data local inpath '" + csv_name + "' overwrite into table " + table_name + " partition (p_date='" + udt + "',hour='" + hour + "') ;\""
    print(c)
    command = (c)
    os.system(command)


# 获取具体的值
def get_item_value(result, writer):
    # 获取field_name对应的具体field_key
    data = get_project_name()
    # result=get_work_item_query()
    result_keys = [key for key, value in data.items() if value == '需求简述']
    # return get_project_name()['RM09 VDR是否符合健康度/成熟度规则？']
    numbers = list(range(0, len(result)))
    wsd = []
    for item in numbers:
        aa = get_work_item_query()[item]
        bb = json.loads(aa)
        id = bb['id']
        name = bb[result_keys[0]]
        print(name)
        rm09 = bb['field_044cf4']['label'] if 'field_044cf4' in bb else None  # RM09 VDR是否符合健康度/成熟度规则？
        # print(rm09)
        alive = bb['field_5849dc'] if 'field_5849dc' in bb else None  # 人工确认
        nc_number = bb['field_210f1a'] if 'field_210f1a' in bb else None  # NC数量1-7
        nobody = bb['field_2e534b'] if 'field_2e534b' in bb else None  # 自动检查信息
        use_version = bb['field_9348b6'] if 'field_9348b6' in bb else None
        wsd.append([id, name, rm09, alive, nc_number, nobody, use_version])
        writer.writerow(
            [id, name, rm09, alive, nc_number, nobody, use_version]
        )
    return wsd


if __name__ == '__main__':
    # a=[get_work_item_query(),get_project_name()]
    # print(a)
    # 需要设置csv格式编码,不然后面写入有可能报错
    csv_name = 'feishu_hive_hf.csv'
    csvfile = open(csv_name, 'w', newline='', encoding='utf-8-sig')  # python3下
    writer = csv.writer(csvfile, delimiter='^')
    # 后面需要新建一个表
    table_name = 'quality_prod.ods_feishu_hive_hf'
    # a=get_item_value()
    # print(a)
    result = get_work_item_query()
    get_item_value(result=result, writer=writer)

    csvfile.close()
    hive_load_table(table_name, csv_name)
