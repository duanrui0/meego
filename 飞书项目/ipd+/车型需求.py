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
    print(response.text)
    data = json.loads(response.text)
    return data['data']


# 3.获取视图列表
def get_version_list():
    url = 'https://project.feishu.cn/open_api/63f71b3c504623c16c7fbce2/view_conf/list'
    header = get_header()
    body = json.dumps({
        "project_key": "63f71b3c504623c16c7fbce2",
        "work_item_type_key": "62e7c97b7712a022a6280af2",
        # 通过调接口知道‘全部型谱’在page_num = 2的地方
        "page_num": 1
    })
    result = requests.request('POST', url, headers=header, data=body)
    data = json.loads(result.text)
    data = data['data']
    list = []
    for re in data:
        if re['name'] == '全部型谱':
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


# 数据打平
def flatten(lst):
    result = []
    for elem in lst:
        if isinstance(elem, list):
            result.extend(flatten(elem))
        else:
            elem_str = str(elem).replace("\'", "").replace("None", "").replace('\"', "").replace('\'', '')
            result.append(elem_str)
    return result


# 获取所有人员key
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
    user_all = str(flat_list).replace('\'None', '').replace('None\'', '').replace('\',', '').replace(' ', '').replace(
        '[', '').replace(']', '')
    user_all = user_all.split(',')

    users_alls = get_project_user_name(user_all)
    # print(users_alls)
    return users_alls


# 将key转为name
def get_user_value_all(user_value, result):
    temp_user = []

    if result is not None and result != '[':

        for user in result:
            print(user)
            print(type(user))
            print("=====")
            if re.match(r"\d{19}", user):
                temp_user.append(user_value[user])
            else:
                temp_user = []

    else:
        print()

    return temp_user


# 5.获取工作项详情
def get_work_item_query():
    field = []
    data = get_version_work_list()

    batch_size = 50

    result = process_data(data, batch_size)
    url = "https://project.feishu.cn/open_api/63f71b3c504623c16c7fbce2/work_item/62e7c97b7712a022a6280af2/query?project_key=63f71b3c504623c16c7fbce2&work_item_type_key=62e7c97b7712a022a6280af2"
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
            work_item_status11 = 'work_item_status'
            work_item_status = item['work_item_status']['state_key']

            json_data = {}
            json_data[work_id11] = work_id
            json_data[work_name11] = work_name
            json_data[work_item_status11] = work_item_status
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


# 6.获取空间字段
def get_project_name():
    url = 'https://project.feishu.cn/open_api/63f71b3c504623c16c7fbce2/field/all'
    header = get_header()
    body = json.dumps({
        "project_key": "63f71b3c504623c16c7fbce2",
        "work_item_type_key": "62e7c97b7712a022a6280af2"
    })
    result = requests.request('POST', url, headers=header, data=body)
    # data = result
    field_key_name = {}
    # 存储普通字段的键值对
    data = json.loads(result.text)

    # 获取第一层数据
    subdata1 = data["data"]
    print(subdata1)
    # 访问第二层数据的键值对
    count = len(subdata1)

    for i in range(0, count):
        key = subdata1[i]['field_key']
        name = subdata1[i]['field_name']
        field_key_name[key] = name

    return field_key_name


# 7.获取空间字段中的多选字段键值对
def get_project_option_name(a):
    url = 'https://project.feishu.cn/open_api/63f71b3c504623c16c7fbce2/field/all'
    header = get_header()
    body = json.dumps({
        "project_key": "63f71b3c504623c16c7fbce2",
        "work_item_type_key": "62e7c97b7712a022a6280af2"
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
    result = option_key_name[a]
    return result


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

# 10. 获取流程角色配置详情
def get_user_perpores():
    url = 'https://project.feishu.cn/open_api/63f71b3c504623c16c7fbce2/flow_roles/62e7c97b7712a022a6280af2'
    header = get_header()
    body = json.dumps({
        "project_key": "63f71b3c504623c16c7fbce2",
        "work_item_type_key": "62e7c97b7712a022a6280af2"
    })
    result = requests.request('GET', url, headers=header, data=body)
    data = json.loads(result.text)
    option_key_name = {}
    for user_info in data['data']:
        name_cn = user_info['id']  # 角色key
        username = user_info['name']  # 角色name
        option_key_name[username] = name_cn  # 将角色key和name组成键值对加入结果字典
    return option_key_name
# 11. 获取空间下工作项类型
def get_item_type():
    url='https://project.feishu.cn/open_api/63f71b3c504623c16c7fbce2/work_item/all-types'
    header = get_header()
    body = json.dumps({
        "project_key": "63f71b3c504623c16c7fbce2"
    })
    result = requests.request('GET', url, headers=header, data=body)
    data = json.loads(result.text)
    return data
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


# 获取具体的值
def get_item_value(result, writer):
    # 获取field_name对应的具体field_key
    data = get_project_name()
    # option_data = get_project_option_name()
    # 获取空间字段
    result_keys = [key for key, value in data.items()]
    # print(result_keys)
    # 打印表头字段
    numbers = list(range(0, len(result)))
    # 计算工作项目数量
    wsd = []
    user_value = get_users_all(result)
    for item in numbers:
        aa = result[item]
        # print("这是一条工作项详情:",aa)
        bb = json.loads(aa)
        # id = bb['id']
        # name=bb[result_keys[0]]
        # business=option_data[bb['business']] if 'business' in bb else None #业务线
        # field_9caa40=get_project_user_name(bb['field_9caa40'][0]) if 'field_9caa40' in bb else None #废弃-负责人
        # for item in bb['field_69ca92']:
        #     field_69ca92 = item['label'] if 'field_69ca92' in bb else None  #需求状态
        #     break
        # field_54bd08=replace_wrap(bb['field_54bd08']) if 'field_54bd08' in bb else None  #最新进展同步
        # field_ef3e43=bb['field_ef3e43']['label'] if 'label' in bb else None  #需求优先级
        # field_da6062=bb['field_da6062'] if 'field_da6062' in bb else None  #Vision
        # field_16605a=bb['field_16605a'] if 'field_16605a' in bb else None  #Action
        # wsd.append([id,name,business,field_9caa40,field_69ca92,field_54bd08,field_ef3e43,field_da6062,field_16605a])
        # writer.writerow(
        #     [id,name,business,field_9caa40,field_69ca92,field_54bd08,field_ef3e43,field_da6062,field_16605a]
        #     )
        id = bb['id']
        archiving_date = replace_wrap(bb['archiving_date']) if 'archiving_date' in bb and bb[
            'archiving_date'] is not None else None  # 归档日期

        deleted_by = replace_wrap(bb['deleted_by']) if 'deleted_by' in bb and bb[
            'deleted_by'] is not None else None  # 删除人
        deleted_by = str(deleted_by).replace('\'None', '').replace('None\'', '').replace('\'', '').replace(' ',
                                                                                                           '').replace(
            '[', '').replace(']', '').split(',')
        deleted_by = get_user_value_all(user_value, deleted_by)

        archiving_status = replace_wrap(bb['archiving_status']) if 'archiving_status' in bb and bb[
            'archiving_status'] is not None else None  # 是否归档
        business = replace_wrap(bb['business']['label']) if 'business' in bb and bb[
            'business'] is not None and 'label' in bb['business'] else None  # 业务线

        current_status_operator = replace_wrap(bb['current_status_operator']) if 'current_status_operator' in bb and bb[
            'current_status_operator'] is not None else None  # 当前负责人
        current_status_operator = str(current_status_operator).replace('\'None', '').replace('None\'', '').replace('\'',
                                                                                                                   '').replace(
            ' ', '').replace('[', '').replace(']', '').split(',')
        current_status_operator = get_user_value_all(user_value, current_status_operator)

        current_status_operator_role = replace_wrap(
            bb['current_status_operator_role']['label']) if 'current_status_operator_role' in bb and bb[
            'current_status_operator_role'] is not None and 'label' in bb[
                                                                'current_status_operator_role'] else None  # 当前状态授权角色
        deleted_at = replace_wrap(bb['deleted_at']) if 'deleted_at' in bb and bb[
            'deleted_at'] is not None else None  # 删除时间
        description = replace_wrap(bb['description']) if 'description' in bb and bb[
            'description'] is not None else None  # 描述
        finish_time = replace_wrap(bb['finish_time']) if 'finish_time' in bb and bb[
            'finish_time'] is not None else None  # 完成时间
        priority = replace_wrap(bb['priority']['label']) if 'priority' in bb and bb[
            'priority'] is not None and 'label' in bb['priority'] else None  # 优先级
        name = replace_wrap(bb['name']) if 'name' in bb and bb['name'] is not None else None  # 车款
        owned_project = replace_wrap(bb['owned_project']) if 'owned_project' in bb and bb[
            'owned_project'] is not None else None  # 所属空间

        owner = replace_wrap(bb['owner']) if 'owner' in bb and bb['owner'] is not None else None  # 创建者
        owner = str(owner).replace('\'None', '').replace('None\'', '').replace('\'', '').replace(' ', '').replace('[',
                                                                                                                  '').replace(
            ']', '').split(',')
        owner = get_user_value_all(user_value, owner)

        tags = replace_wrap(bb['tags']['label']) if 'tags' in bb and bb['tags'] is not None and 'label' in bb[
            'tags'] else None  # 标签
        start_time = replace_wrap(bb['start_time']) if 'start_time' in bb and bb[
            'start_time'] is not None else None  # 提出时间
        template = replace_wrap(bb['template']['label']) if 'template' in bb and bb[
            'template'] is not None and 'label' in bb['template'] else None  # 工作项类型

        updated_by = replace_wrap(bb['updated_by']) if 'updated_by' in bb and bb[
            'updated_by'] is not None else None  # 更新人
        updated_by = str(updated_by).replace('\'None', '').replace('None\'', '').replace('\'', '').replace(' ',
                                                                                                           '').replace(
            '[', '').replace(']', '').split(',')
        updated_by = get_user_value_all(user_value, updated_by)

        updated_at = replace_wrap(bb['updated_at']) if 'updated_at' in bb and bb[
            'updated_at'] is not None else None  # 更新时间

        watchers = replace_wrap(bb['watchers']) if 'watchers' in bb and bb['watchers'] is not None else None  # 关注人
        watchers = str(watchers).replace('\'None', '').replace('None\'', '').replace('\'', '').replace(' ', '').replace(
            '[', '').replace(']', '').split(',')
        watchers = get_user_value_all(user_value, watchers)

        work_item_id = replace_wrap(bb['work_item_id']) if 'work_item_id' in bb and bb[
            'work_item_id'] is not None else None  # 工作项id
        work_item_status = replace_wrap(bb['work_item_status']['label']) if 'work_item_status' in bb and bb[
            'work_item_status'] is not None and 'label' in bb['work_item_status'] else None  # 当前节点
        work_item_type_key = replace_wrap(bb['work_item_type_key']['label']) if 'work_item_type_key' in bb and bb[
            'work_item_type_key'] is not None and 'label' in bb['work_item_type_key'] else None  # 工作项
        field_f41d15 = replace_wrap(bb['field_f41d15']) if 'field_f41d15' in bb and bb[
            'field_f41d15'] is not None else None  # 备注
        field_2370b4 = replace_wrap(bb['field_2370b4']) if 'field_2370b4' in bb and bb[
            'field_2370b4'] is not None else None  # 相关软件版本
        field_ab5b49 = replace_wrap(bb['field_ab5b49']) if 'field_ab5b49' in bb and bb[
            'field_ab5b49'] is not None else None  # 车型
        field_bb1111 = replace_wrap(bb['field_bb1111']) if 'field_bb1111' in bb and bb[
            'field_bb1111'] is not None else None  # 车型项目
        field_160c55 = replace_wrap(bb['field_160c55']['label']) if 'field_160c55' in bb and bb[
            'field_160c55'] is not None and 'label' in bb['field_160c55'] else None  # 改款
        field_f8daf8 = replace_wrap(bb['field_f8daf8']) if 'field_f8daf8' in bb and bb[
            'field_f8daf8'] is not None else None  # 商业计划书
        field_87aa82 = replace_wrap(bb['field_87aa82']['label']) if 'field_87aa82' in bb and bb[
            'field_87aa82'] is not None and 'label' in bb['field_87aa82'] else None  # 物理平台
        field_6f3723 = replace_wrap(bb['field_6f3723']['label']) if 'field_6f3723' in bb and bb[
            'field_6f3723'] is not None and 'label' in bb['field_6f3723'] else None  # 销售区域
        field_589d18 = replace_wrap(bb['field_589d18']) if 'field_589d18' in bb and bb[
            'field_589d18'] is not None else None  # 整车参数
        field_eae953 = replace_wrap(bb['field_eae953']) if 'field_eae953' in bb and bb[
            'field_eae953'] is not None else None  # KO节点时间
        field_249961 = replace_wrap(bb['field_249961']) if 'field_249961' in bb and bb[
            'field_249961'] is not None else None  # G1节点时间
        field_3f7cb2 = replace_wrap(bb['field_3f7cb2']) if 'field_3f7cb2' in bb and bb[
            'field_3f7cb2'] is not None else None  # G2节点时间
        field_b5519e = replace_wrap(bb['field_b5519e']) if 'field_b5519e' in bb and bb[
            'field_b5519e'] is not None else None  # G3节点时间
        field_b96d04 = replace_wrap(bb['field_b96d04']) if 'field_b96d04' in bb and bb[
            'field_b96d04'] is not None else None  # G4节点时间
        field_219299 = replace_wrap(bb['field_219299']) if 'field_219299' in bb and bb[
            'field_219299'] is not None else None  # G5节点时间
        field_7d3046 = replace_wrap(bb['field_7d3046']) if 'field_7d3046' in bb and bb[
            'field_7d3046'] is not None else None  # G6节点时间
        field_413642 = replace_wrap(bb['field_413642']) if 'field_413642' in bb and bb[
            'field_413642'] is not None else None  # G7节点时间
        field_09f15d = replace_wrap(bb['field_09f15d']) if 'field_09f15d' in bb and bb[
            'field_09f15d'] is not None else None  # G0节点时间
        field_73d52f = replace_wrap(bb['field_73d52f']) if 'field_73d52f' in bb and bb[
            'field_73d52f'] is not None else None  # G8节点时间
        field_a77c02 = replace_wrap(bb['field_a77c02']) if 'field_a77c02' in bb and bb[
            'field_a77c02'] is not None else None  # G5.5节点时间
        field_2208b5 = replace_wrap(bb['field_2208b5']) if 'field_2208b5' in bb and bb[
            'field_2208b5'] is not None else None  # G6.5节点时间
        field_450169 = replace_wrap(bb['field_450169']['label']) if 'field_450169' in bb and bb[
            'field_450169'] is not None and 'label' in bb['field_450169'] else None  # 车系
        field_d5640f = replace_wrap(bb['field_d5640f']['label']) if 'field_d5640f' in bb and bb[
            'field_d5640f'] is not None and 'label' in bb['field_d5640f'] else None  # 下一个节点
        field_d37ca2 = replace_wrap(bb['field_d37ca2']['label']) if 'field_d37ca2' in bb and bb[
            'field_d37ca2'] is not None and 'label' in bb['field_d37ca2'] else None  # 软件平台
        field_2a7b75 = replace_wrap(bb['field_2a7b75']) if 'field_2a7b75' in bb and bb[
            'field_2a7b75'] is not None else None  # 相关周期规划
        field_7f1c99 = replace_wrap(bb['field_7f1c99']) if 'field_7f1c99' in bb and bb[
            'field_7f1c99'] is not None else None  # 车型Jira映射字段
        role_owners = replace_wrap(bb['role_owners']) if 'role_owners' in bb and bb[
            'role_owners'] is not None else None  # 车型Jira映射字段

        wsd.append([id, archiving_date, deleted_by, archiving_status, business, current_status_operator,
                    current_status_operator_role, deleted_at, description, finish_time, priority, name, owned_project,
                    owner, tags, start_time, template, updated_by, updated_at, watchers, work_item_id, work_item_status,
                    work_item_type_key, field_f41d15, field_2370b4, field_ab5b49, field_bb1111, field_160c55,
                    field_f8daf8, field_87aa82, field_6f3723, field_589d18, field_eae953, field_249961, field_3f7cb2,
                    field_b5519e, field_b96d04, field_219299, field_7d3046, field_413642, field_09f15d, field_73d52f,
                    field_a77c02, field_2208b5, field_450169, field_d5640f, field_d37ca2, field_2a7b75, field_7f1c99])
        current_time = datetime.now()
        print([id, archiving_date, deleted_by, archiving_status, business, current_status_operator,
               current_status_operator_role, deleted_at, description, finish_time, priority, name, owned_project, owner,
               tags, start_time, template, updated_by, updated_at, watchers, work_item_id, work_item_status,
               work_item_type_key, field_f41d15, field_2370b4, field_ab5b49, field_bb1111, field_160c55, field_f8daf8,
               field_87aa82, field_6f3723, field_589d18, field_eae953, field_249961, field_3f7cb2, field_b5519e,
               field_b96d04, field_219299, field_7d3046, field_413642, field_09f15d, field_73d52f, field_a77c02,
               field_2208b5, field_450169, field_d5640f, field_d37ca2, field_2a7b75, field_7f1c99])
        print("当前时间：", current_time)

        print("已处理" + str(item) + "条")
        writer.writerow(
            [id, archiving_date, deleted_by, archiving_status, business, current_status_operator,
             current_status_operator_role, deleted_at, description, finish_time, priority, name, owned_project, owner,
             tags, start_time, template, updated_by, updated_at, watchers, work_item_id, work_item_status,
             work_item_type_key, field_f41d15, field_2370b4, field_ab5b49, field_bb1111, field_160c55, field_f8daf8,
             field_87aa82, field_6f3723, field_589d18, field_eae953, field_249961, field_3f7cb2, field_b5519e,
             field_b96d04, field_219299, field_7d3046, field_413642, field_09f15d, field_73d52f, field_a77c02,
             field_2208b5, field_450169, field_d5640f, field_d37ca2, field_2a7b75, field_7f1c99]
        )
    return wsd


if __name__ == '__main__':
    print(get_work_item_query())
    print(get_user_perpores())
    # a = [get_work_item_query(), get_project_name()]
    # # print(a)
    # # 需要设置csv格式编码,不然后面写入有可能报错
    # csv_name = 'feishu_hive_hf.csv'
    # csvfile = open(csv_name, 'w', newline='', encoding='utf-8-sig')  # python3下
    # writer = csv.writer(csvfile, delimiter='^')
    # # 后面需要新建一个表
    # table_name = 'dop_plm_myplm_prod.ods_ipd_vehicle_spectrum_feishu_to_hive_hf'
    # # a=get_item_value()
    # # print(a)
    # result = get_work_item_query()
    # get_item_value(result=result, writer=writer)
    #
    # csvfile.close()
    #
    # # 打开CSV文件
    # with open('feishu_hive_hf.csv', 'r') as file:
    #     # 创建CSV读取器
    #     csv_reader = csv.reader(file)
    #
    #     # 逐行读取并打印CSV文件内容
    #     for row in csv_reader:
    #         print(row)
    # hive_load_table(table_name, csv_name)