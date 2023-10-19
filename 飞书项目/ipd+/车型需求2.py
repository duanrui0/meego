# ********************************************************************
# Author: deep as sea
# Create by: 2023/10/18
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
        "work_item_type_key": "649aaf06998b267124f3fb52",
        # 通过调接口知道‘全部需求’在page_num = 2的地方
        "page_num": 2
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
        limit = 1
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
    url = "https://project.feishu.cn/open_api/63f71b3c504623c16c7fbce2/work_item/649aaf06998b267124f3fb52/query?project_key=63f71b3c504623c16c7fbce2&work_item_type_key=649aaf06998b267124f3fb52"
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
            current_nodes11 = 'current_nodes'
            current_nodes_temp = item['current_nodes'][0]
            current_nodes = current_nodes_temp['name']
            work_item_status11 = 'work_item_status'
            work_item_status = item['work_item_status']['state_key']

            json_data = {}
            json_data[work_id11] = work_id
            json_data[work_name11] = work_name
            json_data[current_nodes11] = current_nodes
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
        "work_item_type_key": "649aaf06998b267124f3fb52"
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
        "work_item_type_key": "649aaf06998b267124f3fb52"
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
    result = {}
    for item in a:
        result[item] = option_key_name[item]
    print("这是所有的option和对应的value", result)
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


# # 10. 将field_value中的所有label取出
# def get_all_label(field):
#     if len(field) = 1
#     # 当字段内容不为空时，将其转为字符串，并且将其中的换(\n)改为;符号，返回修改后的字符串
#     if field is not None:
#         field1 = str(field)
#         if '\n' in field1:
#             '''print('————原字符串————')
#             print(field1)'''
#             field1 = field1.replace('\n', ';')
#             '''print('————修改后字符串————')
#             print(field1)'''
#     return field1

# 11.获取所有key值
def get_option_key_all(result):
    # 获取field_name对应的具体field_key
    data = get_project_name()
    numbers = list(range(0, len(result)))
    # 计算工作项目数量
    wsd = []
    key_all = []
    for item in numbers:
        aa = result[item]
        bb = json.loads(aa)
        work_item_status = bb['work_item_status'] if 'work_item_status' in bb and bb[
            'work_item_status'] is not None else None  # 状态
        current_time = datetime.now()
        key_all.append(work_item_status)
    print("这是所有的key：", key_all, "这是所有key的类型", type(key_all))

    # 将options信息提取出来 放进{}里
    # pattern = re.compile(r'[\[\]\']+')
    # lst_without_brackets = [re.sub(pattern, '', str(elem)) for elem in key_all]
    # flat_list = flatten(lst_without_brackets)
    # key_all = str(flat_list).replace('\'None', '').replace('None\'', '').replace('\',', '').replace(' ', '').replace('[','').replace(']', '')
    # key_all = key_all.split(',')
    print("key_all的值是：", key_all, "key_all的类型是：", type(key_all))
    key_alls = get_project_option_name(key_all)
    print("key_alls的值是：", key_alls, "key_alls的类型是：", type(key_alls))
    return key_alls


# 将key转为name
def get_option_value_all(option_value, result):
    temp_value = []
    if result is not None and result != '[':

        temp_value.append(option_value[result])

    else:
        print()

    return temp_value


# 12. 获取多个label对应的value
def get_label_all(field):
    print("field的值是这样：", field)
    print("field的类型是这样：", type(field))
    field = json.loads(field.replace("'", "\""))
    print("field的类型是这样：", type(field))
    temp_label = []
    str_label = str(field)
    if str_label.count("label") > 1:
        for item in field:
            print("item的值是这样：", item)
            label = item["label"]
            temp_label.append([label])
    elif str_label.count("label") == 1:
        label = field[0]["label"]
        temp_label.append([label])

    else:
        temp_label = None

    print("这是temp_label的值：", temp_label)
    return temp_label

# 获取所有流程角色的key
def get_users_config_all(result):
    numbers = list(range(0, len(result)))
    user_all = []
    for item in numbers:
        aa = result[item]
        bb = json.loads(aa)
        role_owners =bb['role_owners']
        for item in role_owners:
            for item2 in item["owners"]:
                user_all.append(item2)
                owners = item["owners"]


    # 将人员信息提取出来 放进{}里

    flat_list = str(user_all)
    user_all = str(flat_list).replace('\'None', '').replace('None\'', '').replace('\'', '').replace(' ', '').replace(
        '[', '').replace(']', '').replace("\"","").replace("\'",'')
    user_all = user_all.split(',')

    users_alls = get_project_user_name(user_all)
    return users_alls

# 将流程角色的key转化为name

def get_user_config_value_all(user_value, result):
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
# 13. 获取流程角色配置详情
def get_user_perpores():
    url = 'https://project.feishu.cn/open_api/63f71b3c504623c16c7fbce2/flow_roles/649aaf06998b267124f3fb52'
    header = get_header()
    body = json.dumps({
        "project_key": "63f71b3c504623c16c7fbce2",
        "work_item_type_key": "649aaf06998b267124f3fb52"
    })
    result = requests.request('GET', url, headers=header, data=body)
    data = json.loads(result.text)
    option_key_name = {}
    for user_info in data['data']:
        name_cn = user_info['id']  # 角色key
        username = user_info['name']  # 角色name
        option_key_name[username] = name_cn  # 将角色key和name组成键值对加入结果字典
    return option_key_name

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
def get_item_value(result):
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
    user_config_value=get_users_config_all(result)
    option_value = get_option_key_all(result)
    user_config = get_user_perpores()
    for item in numbers:
        aa = result[item]
        # print("这是一条工作项详情:",aa)
        bb = json.loads(aa)
        id = bb['id']
        name = replace_wrap(bb['name']) if 'name' in bb and bb['name'] is not None else None  # 车型需求名称
        template = replace_wrap(bb['template']['label']) if 'template' in bb and bb[
            'template'] is not None and 'label' in bb['template'] else None  # 车型需求审批流程
        priority = replace_wrap(bb['priority']['label']) if 'priority' in bb and bb[
            'priority'] is not None and 'label' in bb['priority'] else None  # 优先级
        start_time = replace_wrap(bb['start_time']) if 'start_time' in bb and bb[
            'start_time'] is not None else None  # 创建时间

        owner = replace_wrap(bb['owner']) if 'owner' in bb else None  # 创建者
        owner = str(owner).replace('\'None', '').replace('None\'', '').replace('\'', '').replace(' ', '').replace('[',
                                                                                                                  '').replace(
            ']', '').split(',')
        owner = get_user_value_all(user_value, owner)

        watchers = replace_wrap(bb['watchers']) if 'watchers' in bb else None  # 关注人
        watchers = str(watchers).replace('\'None', '').replace('None\'', '').replace('\'', '').replace(' ', '').replace(
            '[', '').replace(']', '').split(',')
        watchers = get_user_value_all(user_value, watchers)

        description = replace_wrap(bb['description']) if 'description' in bb and bb[
            'description'] is not None else None  # 体验需求描述
        business = replace_wrap(bb['business']['label']) if 'business' in bb and bb[
            'business'] is not None and 'label' in bb['business'] else None  # 业务线
        owned_project = replace_wrap(bb['owned_project']) if 'owned_project' in bb and bb[
            'owned_project'] is not None else None  # 所属空间
        work_item_id = replace_wrap(bb['work_item_id']) if 'work_item_id' in bb and bb[
            'work_item_id'] is not None else None  # 工作项id

        current_status_operator = replace_wrap(
            bb['current_status_operator']) if 'current_status_operator' in bb else None  # 当前负责人
        current_status_operator = str(current_status_operator).replace('\'None', '').replace('None\'', '').replace('\'',
                                                                                                                   '').replace(
            ' ', '').replace('[', '').replace(']', '').split(',')
        current_status_operator = get_user_value_all(user_value, current_status_operator)

        work_item_type_key = replace_wrap(bb['work_item_type_key']['label']) if 'work_item_type_key' in bb and bb[
            'work_item_type_key'] is not None and 'label' in bb['work_item_type_key'] else None  # 工作项
        finish_time = replace_wrap(bb['finish_time']) if 'finish_time' in bb and bb[
            'finish_time'] is not None else None  # 完成时间

        work_item_status = bb['work_item_status'] if 'work_item_status' in bb and bb[
            'work_item_status'] is not None else None  # 状态
        work_item_status = get_option_value_all(option_value, work_item_status)

        field_693940 = replace_wrap(bb['field_693940']['label']) if 'field_693940' in bb and bb[
            'field_693940'] is not None and 'label' in bb['field_693940'] else None  # 软硬件协同
        field_f29b07 = replace_wrap(bb['field_f29b07']) if 'field_f29b07' in bb and bb[
            'field_f29b07'] is not None else None  # VDR追踪
        field_0b7e67 = bb['field_0b7e67'] if 'field_0b7e67' in bb and bb['field_0b7e67'] is not None else None  # 车型适用区域
        # print("这是field_0b7e67的值：", field_0b7e67)
        field_0b7e67 = get_label_all(replace_wrap(bb['field_0b7e67'])) if 'field_0b7e67' in bb and bb[
            'field_0b7e67'] is not None else None  # 车型适用区域
        # print("这是field_0b7e67的值：", field_0b7e67)
        field_950dc4 = replace_wrap(bb['field_950dc4']['label']) if 'field_950dc4' in bb and bb[
            'field_950dc4'] is not None and 'label' in bb['field_950dc4'] else None  # Leo 选装策略
        field_20e79e = replace_wrap(bb['field_20e79e']['label']) if 'field_20e79e' in bb and bb[
            'field_20e79e'] is not None and 'label' in bb['field_20e79e'] else None  # Centaurus 选装策略
        field_5f5851 = replace_wrap(bb['field_5f5851']['label']) if 'field_5f5851' in bb and bb[
            'field_5f5851'] is not None and 'label' in bb['field_5f5851'] else None  # Phoenix 选装策略
        field_9b95ea = replace_wrap(bb['field_9b95ea']['label']) if 'field_9b95ea' in bb and bb[
            'field_9b95ea'] is not None and 'label' in bb['field_9b95ea'] else None  # Sagitta 选装策略
        field_384544 = replace_wrap(bb['field_384544']['label']) if 'field_384544' in bb and bb[
            'field_384544'] is not None and 'label' in bb['field_384544'] else None  # Perseus 选装策略
        field_7e5bf5 = replace_wrap(bb['field_7e5bf5']['label']) if 'field_7e5bf5' in bb and bb[
            'field_7e5bf5'] is not None and 'label' in bb['field_7e5bf5'] else None  # Draco 选装策略
        field_a86fff = replace_wrap(bb['field_a86fff']['label']) if 'field_a86fff' in bb and bb[
            'field_a86fff'] is not None and 'label' in bb['field_a86fff'] else None  # Hercules 选装策略
        field_7b36c2 = replace_wrap(bb['field_7b36c2']['label']) if 'field_7b36c2' in bb and bb[
            'field_7b36c2'] is not None and 'label' in bb['field_7b36c2'] else None  # Pisces 选装策略
        field_54f49c = replace_wrap(bb['field_54f49c']['label']) if 'field_54f49c' in bb and bb[
            'field_54f49c'] is not None and 'label' in bb['field_54f49c'] else None  # Vega 选装策略
        field_3650f3 = replace_wrap(bb['field_3650f3']) if 'field_3650f3' in bb and bb[
            'field_3650f3'] is not None else None  # Leo take rate
        field_4383a0 = replace_wrap(bb['field_4383a0']) if 'field_4383a0' in bb and bb[
            'field_4383a0'] is not None else None  # Centaurus take rate
        field_028025 = replace_wrap(bb['field_028025']) if 'field_028025' in bb and bb[
            'field_028025'] is not None else None  # Phoenix take rate
        field_84c89b = replace_wrap(bb['field_84c89b']) if 'field_84c89b' in bb and bb[
            'field_84c89b'] is not None else None  # Sagitta take rate
        field_dfeb1a = replace_wrap(bb['field_dfeb1a']) if 'field_dfeb1a' in bb and bb[
            'field_dfeb1a'] is not None else None  # Perseus take rate
        field_aa38f7 = replace_wrap(bb['field_aa38f7']) if 'field_aa38f7' in bb and bb[
            'field_aa38f7'] is not None else None  # Draco take rate
        field_16da83 = replace_wrap(bb['field_16da83']) if 'field_16da83' in bb and bb[
            'field_16da83'] is not None else None  # Hercules take rate
        field_92ef9d = replace_wrap(bb['field_92ef9d']) if 'field_92ef9d' in bb and bb[
            'field_92ef9d'] is not None else None  # Pisces take rate
        field_71b04d = replace_wrap(bb['field_71b04d']) if 'field_71b04d' in bb and bb[
            'field_71b04d'] is not None else None  # Vega take rate
        field_609710 = replace_wrap(bb['field_609710']['label']) if 'field_609710' in bb and bb[
            'field_609710'] is not None and 'label' in bb['field_609710'] else None  # 整车平台策略
        field_98b3eb = replace_wrap(bb['field_98b3eb']['label']) if 'field_98b3eb' in bb and bb[
            'field_98b3eb'] is not None and 'label' in bb['field_98b3eb'] else None  # PD数字协作团队
        field_919365 = replace_wrap(bb['field_919365']) if 'field_919365' in bb and bb[
            'field_919365'] is not None else None  # PETS一级体验维度
        field_e80907 = replace_wrap(bb['field_e80907']) if 'field_e80907' in bb and bb[
            'field_e80907'] is not None else None  # PETS二级体验维度
        field_c3ba8b = replace_wrap(bb['field_c3ba8b']) if 'field_c3ba8b' in bb and bb[
            'field_c3ba8b'] is not None else None  # PETS三级体验维度
        field_e29d7a = replace_wrap(bb['field_e29d7a']) if 'field_e29d7a' in bb and bb[
            'field_e29d7a'] is not None else None  # 体验需求文档
        field_478e51 = replace_wrap(bb['field_478e51']) if 'field_478e51' in bb and bb[
            'field_478e51'] is not None else None  # 建议的需求方案
        field_fae060 = replace_wrap(bb['field_fae060']) if 'field_fae060' in bb and bb[
            'field_fae060'] is not None else None  # 关联的体验需求
        field_f65322 = replace_wrap(bb['field_f65322']) if 'field_f65322' in bb and bb[
            'field_f65322'] is not None else None  # 交付车型
        field_889457 = replace_wrap(bb['field_889457']['label']) if 'field_889457' in bb and bb[
            'field_889457'] is not None and 'label' in bb['field_889457'] else None  # 首发车型
        field_2e2be1 = replace_wrap(bb['field_2e2be1']['label']) if 'field_2e2be1' in bb and bb[
            'field_2e2be1'] is not None and 'label' in bb['field_2e2be1'] else None  # Gemini G1.3 选装策略
        field_295df1 = replace_wrap(bb['field_295df1']['label']) if 'field_295df1' in bb and bb[
            'field_295df1'] is not None and 'label' in bb['field_295df1'] else None  # Orion G1.2 选装策略
        field_6647e5 = replace_wrap(bb['field_6647e5']['label']) if 'field_6647e5' in bb and bb[
            'field_6647e5'] is not None and 'label' in bb['field_6647e5'] else None  # Pegasus G1.2 选装策略
        field_728f95 = replace_wrap(bb['field_728f95']['label']) if 'field_728f95' in bb and bb[
            'field_728f95'] is not None and 'label' in bb['field_728f95'] else None  # Force G1.F 选装策略
        field_f75f76 = replace_wrap(bb['field_f75f76']['label']) if 'field_f75f76' in bb and bb[
            'field_f75f76'] is not None and 'label' in bb['field_f75f76'] else None  # Force G1.3 选装策略
        field_e70224 = replace_wrap(bb['field_e70224']['label']) if 'field_e70224' in bb and bb[
            'field_e70224'] is not None and 'label' in bb['field_e70224'] else None  # Libra G1.1 选装策略
        field_29fb34 = replace_wrap(bb['field_29fb34']['label']) if 'field_29fb34' in bb and bb[
            'field_29fb34'] is not None and 'label' in bb['field_29fb34'] else None  # Lyra G1.1 选装策略
        field_0c5a16 = replace_wrap(bb['field_0c5a16']['label']) if 'field_0c5a16' in bb and bb[
            'field_0c5a16'] is not None and 'label' in bb['field_0c5a16'] else None  # Sirius G1.1 选装策略
        field_97e739 = replace_wrap(bb['field_97e739']['label']) if 'field_97e739' in bb and bb[
            'field_97e739'] is not None and 'label' in bb['field_97e739'] else None  # Gemini G1.1 选装策略
        field_ad5928 = replace_wrap(bb['field_ad5928']['label']) if 'field_ad5928' in bb and bb[
            'field_ad5928'] is not None and 'label' in bb['field_ad5928'] else None  # Pegasus G1.1 选装策略
        field_b482f9 = replace_wrap(bb['field_b482f9']['label']) if 'field_b482f9' in bb and bb[
            'field_b482f9'] is not None and 'label' in bb['field_b482f9'] else None  # Force G1.1 选装策略
        field_030e59 = replace_wrap(bb['field_030e59']['label']) if 'field_030e59' in bb and bb[
            'field_030e59'] is not None and 'label' in bb['field_030e59'] else None  # Aries G1.1 选装策略
        field_29f769 = replace_wrap(bb['field_29f769']['label']) if 'field_29f769' in bb and bb[
            'field_29f769'] is not None and 'label' in bb['field_29f769'] else None  # 选装包
        field_f7a203 = replace_wrap(bb['field_f7a203']) if 'field_f7a203' in bb and bb[
            'field_f7a203'] is not None else None  # R1评审意见
        field_d1563b = replace_wrap(bb['field_d1563b']) if 'field_d1563b' in bb and bb[
            'field_d1563b'] is not None else None  # R2评审意见
        field_e941bf = replace_wrap(bb['field_e941bf']['label']) if 'field_e941bf' in bb and bb[
            'field_e941bf'] is not None and 'label' in bb['field_e941bf'] else None  # R2 评审会议
        field_b2cc34 = replace_wrap(bb['field_b2cc34']['label']) if 'field_b2cc34' in bb and bb[
            'field_b2cc34'] is not None and 'label' in bb['field_b2cc34'] else None  # R1 评审会议
        tags = replace_wrap(bb['tags']['label']) if 'tags' in bb and bb['tags'] is not None and 'label' in bb[
            'tags'] else None  # 标签
        field_023d10 = replace_wrap(bb['field_023d10']['label']) if 'field_023d10' in bb and bb[
            'field_023d10'] is not None and 'label' in bb['field_023d10'] else None  # 长周期件
        field_bb2170 = replace_wrap(bb['field_bb2170']) if 'field_bb2170' in bb and bb[
            'field_bb2170'] is not None else None  # 所属核心体验
        field_bd0076 = replace_wrap(bb['field_bd0076']) if 'field_bd0076' in bb and bb[
            'field_bd0076'] is not None else None  # 所属体验目标
        field_920e01 = replace_wrap(bb['field_920e01']['label']) if 'field_920e01' in bb and bb[
            'field_920e01'] is not None and 'label' in bb['field_920e01'] else None  # 预算审批会议
        field_afd864 = replace_wrap(bb['field_afd864']) if 'field_afd864' in bb and bb[
            'field_afd864'] is not None else None  # R2.5评审意见
        field_2d9270 = replace_wrap(bb['field_2d9270']) if 'field_2d9270' in bb and bb[
            'field_2d9270'] is not None else None  # 车型需求描述
        field_89c432 = replace_wrap(bb['field_89c432']['label']) if 'field_89c432' in bb and bb[
            'field_89c432'] is not None and 'label' in bb['field_89c432'] else None  # 平台标签
        field_22c608 = replace_wrap(bb['field_22c608']) if 'field_22c608' in bb and bb[
            'field_22c608'] is not None else None  # 竞品车型
        field_b21efa = replace_wrap(bb['field_b21efa']['label']) if 'field_b21efa' in bb and bb[
            'field_b21efa'] is not None and 'label' in bb['field_b21efa'] else None  # 批量触发
        field_4f29f4 = replace_wrap(bb['field_4f29f4']) if 'field_4f29f4' in bb and bb[
            'field_4f29f4'] is not None else None  # 车型需求文档
        current_nodes = replace_wrap(bb['current_nodes']) if 'current_nodes' in bb and bb[
            'current_nodes'] is not None else None  # 进行中节点
        role_owners =bb['role_owners']

        vem =""
        avem=""
        Studio_EM=""
        EM=""
        EMT_Leader=""
        L2_Leader=""
        SDT_Leader=""
        SDT_PM=""
        VPM=""
        DRE=""
        VPEM评审=""
        PRM评审=""
        PCM评审=""
        PD_L1评审=""
        for item in role_owners:
            role = item["role"]
            owners = item["owners"]
            owners=str(owners).replace('\'','').replace('[','').replace(']','').replace(' ','').split(',')
            if role == user_config["VEM"]:
                vem = get_user_config_value_all(user_config_value,owners)
            elif role == user_config["AVEM"]:
                avem = get_user_config_value_all(user_config_value,owners)
            elif role == user_config["Studio EM"]:
                Studio_EM = get_user_config_value_all(user_config_value,owners)
            elif role == user_config["EM"]:
                EM = get_user_config_value_all(user_config_value,owners)
            elif role == user_config["EMT Leader"]:
                EMT_Leader = get_user_config_value_all(user_config_value,owners)
            elif role == user_config["L2 Leader"]:
                L2_Leader = get_user_config_value_all(user_config_value,owners)
            elif role == user_config["SDT Leader"]:
                SDT_Leader = get_user_config_value_all(user_config_value,owners)
            elif role == user_config["SDT PM"]:
                SDT_PM = get_user_config_value_all(user_config_value,owners)
            elif role == user_config["VPM"]:
                VPM = get_user_config_value_all(user_config_value,owners)
            elif role == user_config["DRE"]:
                DRE = get_user_config_value_all(user_config_value,owners)
            elif role == user_config["VPEM评审"]:

                VPEM评审 = str(get_user_config_value_all(user_config_value,owners))
            elif role == user_config["PRM评审"]:
                PRM评审 = get_user_config_value_all(user_config_value,owners)
            elif role == user_config["PCM评审"]:
                PCM评审 = get_user_config_value_all(user_config_value,owners)
            elif role == user_config["PD L1评审"]:
                PD_L1评审 = get_user_config_value_all(user_config_value,owners)
            else:
                print()
        print("这是所有角色")
        print([vem,avem,Studio_EM,EM,EMT_Leader,L2_Leader,SDT_Leader,SDT_PM,VPM,DRE,VPEM评审,PRM评审,PCM评审,PD_L1评审])
        wsd.append([id, name, template, priority, start_time, owner, watchers, description, business, owned_project,
                    work_item_id, current_status_operator, work_item_type_key, finish_time, work_item_status,
                    field_693940, field_f29b07, field_0b7e67, field_950dc4, field_20e79e, field_5f5851, field_9b95ea,
                    field_384544, field_7e5bf5, field_a86fff, field_7b36c2, field_54f49c, field_3650f3, field_4383a0,
                    field_028025, field_84c89b, field_dfeb1a, field_aa38f7, field_16da83, field_92ef9d, field_71b04d,
                    field_609710, field_98b3eb, field_919365, field_e80907, field_c3ba8b, field_e29d7a, field_478e51,
                    field_fae060, field_f65322, field_889457, field_2e2be1, field_295df1, field_6647e5, field_728f95,
                    field_f75f76, field_e70224, field_29fb34, field_0c5a16, field_97e739, field_ad5928, field_b482f9,
                    field_030e59, field_29f769, field_f7a203, field_d1563b, field_e941bf, field_b2cc34, tags,
                    field_023d10, field_bb2170, field_bd0076, field_920e01, field_afd864, field_2d9270, field_89c432,
                    field_22c608, field_b21efa, field_4f29f4, current_nodes])
        current_time = datetime.now()
        # print([id, name, template, priority, start_time, owner, watchers, description, business, owned_project,
        #        work_item_id, current_status_operator, work_item_type_key, finish_time, work_item_status, field_693940,
        #        field_f29b07, field_0b7e67, field_950dc4, field_20e79e, field_5f5851, field_9b95ea, field_384544,
        #        field_7e5bf5, field_a86fff, field_7b36c2, field_54f49c, field_3650f3, field_4383a0, field_028025,
        #        field_84c89b, field_dfeb1a, field_aa38f7, field_16da83, field_92ef9d, field_71b04d, field_609710,
        #        field_98b3eb, field_919365, field_e80907, field_c3ba8b, field_e29d7a, field_478e51, field_fae060,
        #        field_f65322, field_889457, field_2e2be1, field_295df1, field_6647e5, field_728f95, field_f75f76,
        #        field_e70224, field_29fb34, field_0c5a16, field_97e739, field_ad5928, field_b482f9, field_030e59,
        #        field_29f769, field_f7a203, field_d1563b, field_e941bf, field_b2cc34, tags, field_023d10, field_bb2170,
        #        field_bd0076, field_920e01, field_afd864, field_2d9270, field_89c432, field_22c608, field_b21efa,
        #        field_4f29f4, current_nodes])

        # writer.writerow(
        #     [id, name, template, priority, start_time, owner, watchers, description, business, owned_project,
        #      work_item_id, current_status_operator, work_item_type_key, finish_time, work_item_status, field_693940,
        #      field_f29b07, field_0b7e67, field_950dc4, field_20e79e, field_5f5851, field_9b95ea, field_384544,
        #      field_7e5bf5, field_a86fff, field_7b36c2, field_54f49c, field_3650f3, field_4383a0, field_028025,
        #      field_84c89b, field_dfeb1a, field_aa38f7, field_16da83, field_92ef9d, field_71b04d, field_609710,
        #      field_98b3eb, field_919365, field_e80907, field_c3ba8b, field_e29d7a, field_478e51, field_fae060,
        #      field_f65322, field_889457, field_2e2be1, field_295df1, field_6647e5, field_728f95, field_f75f76,
        #      field_e70224, field_29fb34, field_0c5a16, field_97e739, field_ad5928, field_b482f9, field_030e59,
        #      field_29f769, field_f7a203, field_d1563b, field_e941bf, field_b2cc34, tags, field_023d10, field_bb2170,
        #      field_bd0076, field_920e01, field_afd864, field_2d9270, field_89c432, field_22c608, field_b21efa,
        #      field_4f29f4, current_nodes]
        # )
    return wsd


if __name__ == '__main__':
    # print(get_work_item_query())
    # print(get_user_perpores())
    # a = [get_work_item_query(), get_project_name()]
    # # print(a)
    # # 需要设置csv格式编码,不然后面写入有可能报错
    # csv_name = 'feishu_hive_hf.csv'
    # csvfile = open(csv_name, 'w', newline='', encoding='utf-8-sig')  # python3下
    # writer = csv.writer(csvfile, delimiter='^')
    # # 后面需要新建一个表
    # table_name = 'dop_plm_myplm_prod.ods_ipd_vehicle_demand_feishu_to_hive_hf'
    # # a=get_item_value()
    # # print(a)
    result = get_work_item_query()
    print(result)
    get_item_value(result=result)
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