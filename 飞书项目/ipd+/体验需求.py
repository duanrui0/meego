# -*- coding: utf-8 -*-
# ********************************************************************
# Author: zeyu.feng
# Create by: 2023-08-22 13:15:39.000
# Description:
# Update: Task Update Description
# ********************************************************************

import requests
import json
import csv
import os
from datetime import datetime
import re

# 1.获取插件凭证
def get_fsu_token():
    url = 'https://project.feishu.cn/open_api/authen/plugin_token'
    payload = json.dumps({
        # project_to_hive插件的账号密码
        "plugin_id": "MII_64E445BB25814004",
        "plugin_secret": "49C4810E71D2A91B2A30626DF9DBB54B"
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
        # zeyu.feng的user_key
        'X-USER-KEY': '7152725637445287938'
    }
    return header


# 2.获取空间列表
def get_projects():
    url = 'https://project.feishu.cn/open_api/projects'
    header = get_header()
    body = json.dumps({
        "user_key": "7152725637445287938"
    })
    response = requests.request('POST', url, headers=header, data=body)
    # print(response.text)
    data = json.loads(response.text)
    return data['data']


# 3.获取视图列表
def get_version_list():
    url = 'https://project.feishu.cn/open_api/63f71b3c504623c16c7fbce2/view_conf/list'
    header = get_header()
    body = json.dumps({
        "project_key": "63f71b3c504623c16c7fbce2",
        "work_item_type_key": "story",
        # 通过调接口知道‘全部需求’在page_num = 3的地方
        "page_num": 3
    })
    result = requests.request('POST', url, headers=header, data=body)
    data = json.loads(result.text)
    data = data['data']
    list = []
    for re in data:
        if re['name'] == '全部需求':
            list.append(re['view_id'])

    return list


# 4.获取视图下工作项列表
def get_version_work_list():
    data = []
    for id in get_version_list():
        limit = 200
        page = 1
        while True:
            url = 'https://project.feishu.cn/open_api/63f71b3c504623c16c7fbce2/fix_view/' + id + '?page_size=' + str(
                limit) + '&page_num=' + str(page)

            # url = 'https://project.feishu.cn/open_api/63f71b3c504623c16c7fbce2/fix_view/' + id + '?page_size=70&page_num=1'
            header = get_header()
            result = requests.request('GET', url, headers=header)
            result = json.loads(result.text)
            if result['err_code'] == 0:
                aa = result['data']['work_item_id_list']
                data.append(aa)
                # print(data)
                if len(aa) < 200:
                    break
                page += 1
            else:
                break

    data = [item for sublist in data for item in sublist]

    return data


# 从列表中每次获取指定数量的元素，并将它们写入一个新的列表
def process_data(original_list, batch_size):
    processed_list = []
    while len(original_list) > 0:
        batch = original_list[:batch_size]  # 从原始列表中取出指定数量的元素
        processed_list.append(batch)  # 将批处理的数据写入新的列表
        original_list = original_list[batch_size:]  # 从原始列表中移除已经处理过的元素
    return processed_list


# 5.获取工作项详情
def get_work_item_query():
    field = []
    data = get_version_work_list()

    batch_size = 50

    result = process_data(data, batch_size)

    url = "https://project.feishu.cn/open_api/63f71b3c504623c16c7fbce2/work_item/story/query?project_key=63f71b3c504623c16c7fbce2&work_item_type_key=story"
    header = get_header()
    for i in result:
        # 取出当前批次的数据

        # 处理当前批次的数据
        # 处理item，可以根据需求进行相应的操作
        body = json.dumps({
            "work_item_ids": i
        })

        result = requests.request('POST', url, headers=header, data=body)

        aa = json.loads(result.text)

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

                json_data[field_key] = field_value

            json_str = json.dumps(json_data)
            current_time = datetime.now()
            # print("当前时间：", current_time)

            field.append(json_str)
            # 判断是否取完所有数据

    # print(field)
    return field


def write_to_file(data, filename):
    with open(filename, 'w') as file:
        for batch in data:
            file.write(batch)
            file.write('\n')


# 6.获取空间字段
def get_project_name():
    url = 'https://project.feishu.cn/open_api/63f71b3c504623c16c7fbce2/field/all'
    header = get_header()
    body = json.dumps({
        "project_key": "63f71b3c504623c16c7fbce2",
        "work_item_type_key": "story"
    })
    result = requests.request('POST', url, headers=header, data=body)
    # data = result
    field_key_name = {}
    # 存储普通字段的键值对
    data = json.loads(result.text)

    # 获取第一层数据
    subdata1 = data["data"]
    # print(subdata1)
    # 访问第二层数据的键值对
    count = len(subdata1)

    for i in range(0, count):
        key = subdata1[i]['field_key']
        name = subdata1[i]['field_name']
        field_key_name[key] = name

    return field_key_name


# 7.获取空间字段中的多选字段键值对
def get_project_option_name():
    url = 'https://project.feishu.cn/open_api/63f71b3c504623c16c7fbce2/field/all'
    header = get_header()
    body = json.dumps({
        "project_key": "63f71b3c504623c16c7fbce2",
        "work_item_type_key": "story"
    })
    result = requests.request('POST', url, headers=header, data=body)
    # data = result
    option_key_name = {}
    # 存储多选字段的键值对
    data = json.loads(result.text)

    # 获取第一层数据
    subdata1 = data["data"]
    # 访问第二层数据的键值对
    for item in subdata1:
        if 'options' in item:
            # 访问第三层数据的键值对
            options = item['options']
            for opt in options:
                option_key_name[opt['value']] = opt['label']

    return option_key_name


# 8.获取空间字段中的人员键值对
def get_project_user_name(user_key):
    batch_size = 50
    option_key_name = {}
    result = process_data(user_key, batch_size)

    url = 'https://project.feishu.cn/open_api/user/query'
    header = {
        'X-PLUGIN-TOKEN': get_fsu_token(),
        'X-USER-KEY': '7152725637445287938'
    }
    for item in result:

        body = json.dumps({
            "user_keys": item
        })
        # print(body)
        result = requests.request('POST', url, headers=header, data=body)
        data = json.loads(result.text)

        for user_info in data['data']:
            name_cn = user_info['name_cn']  # 获取名字
            username = user_info['username']  # 获取用户名
            option_key_name[username] = name_cn  # 将名字和用户名组成键值对加入结果字典
    print(option_key_name)
    return option_key_name


# 9. 将各字段中换行符删除
def replace_wrap(field):
    field1 = None
    # 当字段内容不为空时，将其转为字符串，并且将其中的换(\n)改为;符号，返回修改后的字符串
    if field is not None:
        field1 = str(field)
        if '\n' in field1:
            '''print('————原字符串————')
            print(field1)'''
            field1 = field1.replace('\n', ';')
            '''print('————修改后字符串————')
            print(field1)'''
    return field1


def flatten(lst):
    result = []
    for elem in lst:
        if isinstance(elem, list):
            result.extend(flatten(elem))
        else:
            elem_str = str(elem).replace("\'", "").replace("None", "").replace('\"', "").replace('\'', '')
            result.append(elem_str)
    return result


# 将数据写入csv
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

def get_users_all(result):
    # 获取field_name对应的具体field_key
    data = get_project_name()
    numbers = list(range(0, len(result)))
    # 计算工作项目数量
    wsd = []
    user_all = []
    for item in numbers:
        aa = result[item]
        bb = json.loads(aa)

        # deleted_by = get_project_user_name(replace_wrap(bb['deleted_by'])) if 'deleted_by' in bb else None  # 删除人
        deleted_by = replace_wrap(bb['deleted_by']) if 'deleted_by' in bb else None  # 删除人
        temp_user = replace_wrap(bb['current_status_operator']) if 'current_status_operator' in bb else None  # 当前负责人
        # owner = get_project_user_name(replace_wrap(bb['owner'])) if 'owner' in bb else None  # 创建者
        owner = replace_wrap(bb['owner']) if 'owner' in bb else None  # 创建者
        # updated_by = get_project_user_name(replace_wrap(bb['updated_by'])) if 'updated_by' in bb else None  # 更新人
        updated_by = replace_wrap(bb['updated_by']) if 'updated_by' in bb else None  # 更新人
        watchers = replace_wrap(bb['watchers']) if 'watchers' in bb else None  # 关注人
        current_time = datetime.now()
        user_all.append([deleted_by, temp_user, owner, updated_by])

    # 将人员信息提取出来 放进{}里
    pattern = re.compile(r'[\[\]\']+')
    lst_without_brackets = [re.sub(pattern, '', str(elem)) for elem in user_all]
    flat_list = flatten(lst_without_brackets)
    user_all = str(flat_list).replace('\'None', '').replace('None\'', '').replace('\',', '').replace(' ', '').replace('[','').replace(']', '')
    user_all = user_all.split(',')

    users_alls=  get_project_user_name(user_all)
    # print(users_alls)
    return users_alls

def get_user_value_all(user_value,result):
    temp_user=[]

    for user in result:
        print(user)
        print(type(user))
        print("=====")
        if re.match(r"\d{19}", user):
            temp_user.append(user_value[user])
        else:
            print()

    return temp_user

# 获取具体的值
def get_item_value(result):
    # 获取field_name对应的具体field_key
    data = get_project_name()
    option_data = get_project_option_name()
    # 获取空间字段
    result_keys = [key for key, value in data.items()]
    # print(result_keys)
    # 打印表头字段
    numbers = list(range(0, len(result)))
    # 计算工作项目数量
    wsd = []
    user_all = []
    user_value = get_users_all(result)
    # print(user_value)
    eiie=[]
    for item in numbers:
        aa = result[item]
        print("这是一条工作项详情:", aa)
        bb = json.loads(aa)

        id = bb['id'] if 'id' in bb else None
        archiving_date = replace_wrap(bb['archiving_date'] if 'archiving_date' in bb else None)  # 归档日期
        # deleted_by = get_project_user_name(replace_wrap(bb['deleted_by'])) if 'deleted_by' in bb else None  # 删除人
        deleted_by = replace_wrap(bb['deleted_by']) if 'deleted_by' in bb else None  # 删除人
        eiie.append(deleted_by)
        business = replace_wrap(bb['business']) if 'business' in bb else None  # 业务线
        temp_user = replace_wrap(bb['current_status_operator']) if 'current_status_operator' in bb else None  # 当前负责人
        print("temp_user的值为", temp_user)
        temp_user=str(temp_user).replace('\'None', '').replace('None\'', '').replace('\'', '').replace(' ', '').replace('[','').replace(']', '').split(',')
        print("temp_user的type为", type(temp_user))
        print("temp_user的值为", temp_user)
        temp_user=get_user_value_all(user_value,temp_user)
        print(temp_user)
        if temp_user is not None and len(temp_user) > 0:
            # current_status_operator = get_project_user_name(temp_user)
            current_status_operator = ''
        else:
            current_status_operator = ''
        deleted_at = replace_wrap(bb['deleted_at']) if 'deleted_at' in bb else None  # 删除时间
        description = replace_wrap(bb['description']) if 'description' in bb else None  # 需求描述
        finish_time = replace_wrap(bb['finish_time']) if 'finish_time' in bb else None  # 完成时间
        priority = replace_wrap(bb['priority']['label']) if 'label' in bb else None  # 优先级
        name = replace_wrap(bb['name']) if 'name' in bb else None  # 需求名称
        owned_project = replace_wrap(bb['owned_project']) if 'owned_project' in bb else None  # 所属空间
        # owner = get_project_user_name(replace_wrap(bb['owner'])) if 'owner' in bb else None  # 创建者
        owner = replace_wrap(bb['owner']) if 'owner' in bb else None  # 创建者
        schedule = replace_wrap(bb['schedule']) if 'schedule' in bb else None  # 排期
        tags = replace_wrap(bb['tags']['label']) if 'label' in bb else None  # 标签
        date = replace_wrap(bb['date']) if 'date' in bb else None  # 提出时间
        # updated_by = get_project_user_name(replace_wrap(bb['updated_by'])) if 'updated_by' in bb else None  # 更新人
        updated_by = replace_wrap(bb['updated_by']) if 'updated_by' in bb else None  # 更新人
        wiki = replace_wrap(bb['wiki']) if 'wiki' in bb else None  # 需求文档
        updated_at = replace_wrap(bb['updated_at']) if 'updated_at' in bb else None  # 更新时间
        watchers = replace_wrap(bb['watchers']) if 'watchers' in bb else None  # 关注人
        work_item_id = replace_wrap(bb['work_item_id']) if 'work_item_id' in bb else None  # 工作项id
        work_item_type_key = replace_wrap(bb['work_item_type_key']['label']) if 'label' in bb else None  # 工作项
        field_478e51 = replace_wrap(bb['field_478e51']) if 'field_478e51' in bb else None  # 建议的方案
        field_0aa003 = replace_wrap(bb['field_0aa003']) if 'field_0aa003' in bb else None  # 预期收益
        field_a8772e = replace_wrap(bb['field_a8772e']) if 'field_a8772e' in bb else None  # PETS 三级体验维度
        field_46bad0 = replace_wrap(bb['field_46bad0']) if 'field_46bad0' in bb else None  # R1 评审会议
        field_693940 = replace_wrap(bb['field_693940']) if 'field_693940' in bb else None  # 软硬件协同
        field_2c595c = replace_wrap(bb['field_2c595c']) if 'field_2c595c' in bb else None  # 适用车型
        field_aba774 = replace_wrap(bb['field_aba774']) if 'field_aba774' in bb else None  # 目标软件版本
        field_d56473 = replace_wrap(bb['field_d56473']) if 'field_d56473' in bb else None  # 关联的WTI需求
        field_f29b07 = replace_wrap(bb['field_f29b07']) if 'field_f29b07' in bb else None  # VDR追踪
        field_0b7e67 = replace_wrap(bb['field_0b7e67']['label']) if 'label' in bb else None  # 适用区域
        field_950dc4 = replace_wrap(bb['field_950dc4']['label']) if 'label' in bb else None  # Leo 选装策略
        field_20e79e = replace_wrap(bb['field_20e79e']['label']) if 'label' in bb else None  # Centaurus 选装策略
        field_5f5851 = replace_wrap(bb['field_5f5851']['label']) if 'label' in bb else None  # Phoenix 选装策略
        field_9b95ea = replace_wrap(bb['field_9b95ea']['label']) if 'label' in bb else None  # Sagitta 选装策略
        field_384544 = replace_wrap(bb['field_384544']['label']) if 'label' in bb else None  # Perseus 选装策略
        field_7e5bf5 = replace_wrap(bb['field_7e5bf5']['label']) if 'label' in bb else None  # Draco 选装策略
        field_a86fff = replace_wrap(bb['field_a86fff']['label']) if 'label' in bb else None  # Hercules 选装策略
        field_7b36c2 = replace_wrap(bb['field_7b36c2']['label']) if 'label' in bb else None  # Pisces 选装策略
        field_54f49c = replace_wrap(bb['field_54f49c']['label']) if 'label' in bb else None  # Vega 选装策略
        field_3650f3 = replace_wrap(bb['field_3650f3']) if 'field_3650f3' in bb else None  # Leo take rate
        field_4383a0 = replace_wrap(bb['field_4383a0']) if 'field_4383a0' in bb else None  # Centaurus take rate
        field_028025 = replace_wrap(bb['field_028025']) if 'field_028025' in bb else None  # Phoenix take rate
        field_84c89b = replace_wrap(bb['field_84c89b']) if 'field_84c89b' in bb else None  # Sagitta take rate
        field_dfeb1a = replace_wrap(bb['field_dfeb1a']) if 'field_dfeb1a' in bb else None  # Perseus take rate
        field_aa38f7 = replace_wrap(bb['field_aa38f7']) if 'field_aa38f7' in bb else None  # Draco take rate
        field_16da83 = replace_wrap(bb['field_16da83']) if 'field_16da83' in bb else None  # Hercules take rate
        field_92ef9d = replace_wrap(bb['field_92ef9d']) if 'field_92ef9d' in bb else None  # Pisces take rate
        field_71b04d = replace_wrap(bb['field_71b04d']) if 'field_71b04d' in bb else None  # Vega take rate
        field_84292e = replace_wrap(bb['field_84292e']) if 'field_84292e' in bb else None  # PETS 一级体验维度
        field_693139 = replace_wrap(bb['field_693139']) if 'field_693139' in bb else None  # PETS 二级体验维度
        template = replace_wrap(bb['template']['label']) if 'label' in bb else None  # 需求审批流程
        work_item_status = replace_wrap(bb['work_item_status']['label']) if 'label' in bb else None  # 需求状态
        field_609710 = replace_wrap(bb['field_609710']['label']) if 'label' in bb else None  # 整车平台策略
        field_98b3eb = replace_wrap(bb['field_98b3eb']['label']) if 'label' in bb else None  # PD数字协作团队
        field_0ada37 = replace_wrap(bb['field_0ada37']) if 'field_0ada37' in bb else None  # 关联的车型需求
        field_e941bf = replace_wrap(bb['field_e941bf']['label']) if 'label' in bb else None  # R2 评审会议
        field_c029b1 = replace_wrap(bb['field_c029b1']) if 'field_c029b1' in bb else None  # NT3 平台通用
        field_fe922d = replace_wrap(bb['field_fe922d']) if 'field_fe922d' in bb else None  # 首发车型
        field_2e2be1 = replace_wrap(bb['field_2e2be1']['label']) if 'label' in bb else None  # Gemini G1.3 选装策略
        field_295df1 = replace_wrap(bb['field_295df1']['label']) if 'label' in bb else None  # Orion G1.2 选装策略
        field_6647e5 = replace_wrap(bb['field_6647e5']['label']) if 'label' in bb else None  # Pegasus G1.2 选装策略
        field_728f95 = replace_wrap(bb['field_728f95']['label']) if 'label' in bb else None  # Force G1.F 选装策略
        field_f75f76 = replace_wrap(bb['field_f75f76']['label']) if 'label' in bb else None  # Force G1.3 选装策略
        field_e70224 = replace_wrap(bb['field_e70224']['label']) if 'label' in bb else None  # Libra G1.1 选装策略
        field_29fb34 = replace_wrap(bb['field_29fb34']['label']) if 'label' in bb else None  # Lyra G1.1 选装策略
        field_0c5a16 = replace_wrap(bb['field_0c5a16']['label']) if 'label' in bb else None  # Sirius G1.1 选装策略
        field_97e739 = replace_wrap(bb['field_97e739']['label']) if 'label' in bb else None  # Gemini G1.1 选装策略
        field_ad5928 = replace_wrap(bb['field_ad5928']['label']) if 'label' in bb else None  # Pegasus G1.1 选装策略
        field_b482f9 = replace_wrap(bb['field_b482f9']['label']) if 'label' in bb else None  # Force G1.1 选装策略
        field_030e59 = replace_wrap(bb['field_030e59']['label']) if 'label' in bb else None  # Aries G1.1 选装策略
        field_f7a203 = replace_wrap(bb['field_f7a203']) if 'field_f7a203' in bb else None  # R1评审意见
        field_d1563b = replace_wrap(bb['field_d1563b']) if 'field_d1563b' in bb else None  # R2评审意见
        field_023d10 = replace_wrap(bb['field_023d10']['label']) if 'label' in bb else None  # 长周期件
        field_bcccb9 = replace_wrap(bb['field_bcccb9']['label']) if 'label' in bb else None  # 会议标签
        field_3ec9c8 = replace_wrap(bb['field_3ec9c8']['label']) if 'label' in bb else None  # 预算审批会议
        field_3eaa87 = replace_wrap(bb['field_3eaa87']) if 'field_3eaa87' in bb else None  # R2.5 评审意见
        field_36de0b = replace_wrap(bb['field_36de0b']['label']) if 'label' in bb else None  # 批量触发
        field_89c432 = replace_wrap(bb['field_89c432']['label']) if 'label' in bb else None  # 平台标签
        field_bf35a9 = replace_wrap(bb['field_bf35a9']['label']) if 'label' in bb else None  # 新建角色刷新历史数据
        field_739521 = replace_wrap(bb['field_739521']['label']) if 'label' in bb else None  # Centaurus车型选装策略
        field_2a9429 = replace_wrap(bb['field_2a9429']['label']) if 'label' in bb else None  # Draco车型选装策略
        wsd.append(
            [id, archiving_date, deleted_by, business, current_status_operator, deleted_at, description, finish_time,
             priority, name, owned_project, owner, schedule, tags, date, updated_by, wiki, updated_at, watchers,
             work_item_id, work_item_type_key, field_478e51, field_0aa003, field_a8772e, field_46bad0, field_693940,
             field_2c595c, field_aba774, field_d56473, field_f29b07, field_0b7e67, field_950dc4, field_20e79e,
             field_5f5851, field_9b95ea, field_384544, field_7e5bf5, field_a86fff, field_7b36c2, field_54f49c,
             field_3650f3, field_4383a0, field_028025, field_84c89b, field_dfeb1a, field_aa38f7, field_16da83,
             field_92ef9d, field_71b04d, field_84292e, field_693139, template, work_item_status, field_609710,
             field_98b3eb, field_0ada37, field_e941bf, field_c029b1, field_fe922d, field_2e2be1, field_295df1,
             field_6647e5, field_728f95, field_f75f76, field_e70224, field_29fb34, field_0c5a16, field_97e739,
             field_ad5928, field_b482f9, field_030e59, field_f7a203, field_d1563b, field_023d10, field_bcccb9,
             field_3ec9c8, field_3eaa87, field_36de0b, field_89c432, field_bf35a9, field_739521, field_2a9429])
        print([id, archiving_date, deleted_by, business, current_status_operator, deleted_at, description, finish_time,
               priority, name, owned_project, owner, schedule, tags, date, updated_by, wiki, updated_at, watchers,
               work_item_id, work_item_type_key, field_478e51, field_0aa003, field_a8772e, field_46bad0, field_693940,
               field_2c595c, field_aba774, field_d56473, field_f29b07, field_0b7e67, field_950dc4, field_20e79e,
               field_5f5851, field_9b95ea, field_384544, field_7e5bf5, field_a86fff, field_7b36c2, field_54f49c,
               field_3650f3, field_4383a0, field_028025, field_84c89b, field_dfeb1a, field_aa38f7, field_16da83,
               field_92ef9d, field_71b04d, field_84292e, field_693139, template, work_item_status, field_609710,
               field_98b3eb, field_0ada37, field_e941bf, field_c029b1, field_fe922d, field_2e2be1, field_295df1,
               field_6647e5, field_728f95, field_f75f76, field_e70224, field_29fb34, field_0c5a16, field_97e739,
               field_ad5928, field_b482f9, field_030e59, field_f7a203, field_d1563b, field_023d10, field_bcccb9,
               field_3ec9c8, field_3eaa87, field_36de0b, field_89c432, field_bf35a9, field_739521, field_2a9429])
        current_time = datetime.now()
        print("当前时间：", current_time)
        print("已处理" + str(item+1) + "条")
        user_all.append([deleted_by, temp_user, owner, updated_by])
        print("---")

        # print(owner1)
        # print(owner)
        # writer.writerow(
        #     [id, archiving_date, deleted_by, business, current_status_operator, deleted_at, description, finish_time,
        #      priority, name, owned_project, owner, schedule, tags, date, updated_by, wiki, updated_at, watchers,
        #      work_item_id, work_item_type_key, field_478e51, field_0aa003, field_a8772e, field_46bad0, field_693940,
        #      field_2c595c, field_aba774, field_d56473, field_f29b07, field_0b7e67, field_950dc4, field_20e79e,
        #      field_5f5851, field_9b95ea, field_384544, field_7e5bf5, field_a86fff, field_7b36c2, field_54f49c,
        #      field_3650f3, field_4383a0, field_028025, field_84c89b, field_dfeb1a, field_aa38f7, field_16da83,
        #      field_92ef9d, field_71b04d, field_84292e, field_693139, template, work_item_status, field_609710,
        #      field_98b3eb, field_0ada37, field_e941bf, field_c029b1, field_fe922d, field_2e2be1, field_295df1,
        #      field_6647e5, field_728f95, field_f75f76, field_e70224, field_29fb34, field_0c5a16, field_97e739,
        #      field_ad5928, field_b482f9, field_030e59, field_f7a203, field_d1563b, field_023d10, field_bcccb9,
        #      field_3ec9c8, field_3eaa87, field_36de0b, field_89c432, field_bf35a9, field_739521, field_2a9429]
        # )

    # 将人员信息提取出来 放进{}里
    pattern = re.compile(r'[\[\]\']+')
    lst_without_brackets = [re.sub(pattern, '', str(elem)) for elem in user_all]
    flat_list = flatten(lst_without_brackets)
    user_all = str(flat_list).replace('\'None', '').replace('None\'', '').replace('\',', '').replace(' ', '').replace('[','').replace(']', '')
    user_all = user_all.split(',')
    print("3242434")
    print(eiie)
    get_project_user_name(user_all)

    return wsd


if __name__ == '__main__':
    # print(len(get_work_item_query()))
    # a = [get_work_item_query(), get_project_name()]
    # print(a)
    # 需要设置csv格式编码,不然后面写入有可能报错
    # csv_name = 'feishu_hive_hf.csv'
    # csvfile = open(csv_name, 'w', newline='', encoding='utf-8-sig')  # python3下
    # writer = csv.writer(csvfile, delimiter='^')
    # 后面需要新建一个表
    # table_name = 'dop_plm_myplm_prod.ods_ipd_feishu_to_hive_hf'
    # a=get_item_value()
    # print(a)

    # 示例用法
    # data =get_project_option_name() # 包含多个批次数据的列表
    # filename = 'output.txt'  # 要写入的文件名
    # print(data)

    # get_item_value(data)
    result = get_work_item_query()
    # print(result)
    user_value = get_item_value(result)
    print(type(user_value))
    print(user_value)
    # write_to_file(data, filename)
    # csvfile.close()

    # # 打开CSV文件
    # with open('feishu_hive_hf.csv', 'r') as file:
    #     # 创建CSV读取器
    #     csv_reader = csv.reader(file)
    #
    #     # 逐行读取并打印CSV文件内容
    #     for row in csv_reader:
    #         print(row)
    # hive_load_table(table_name, csv_name)
