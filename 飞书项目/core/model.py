import re
from typing import Optional

from 飞书项目.core.cache import user_dict

from 飞书项目.util import request
from 飞书项目.util.utils import trans_unix_time, time_cost
import math
import os

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

def get_comm_header():

    header = {
        'X-User-Key': "7137587176702885916",
        'Content-Type': 'application/json'
    }
    if get_fsu_token():
        plugin_token = {"X-Plugin-Token": get_fsu_token()}
        headers = dict(plugin_token, **header)
        return headers
    else:
        return None

header = get_comm_header()
base_url ="https://project.feishu.cn/open_api"


# 获取创建工作项元数据 /open_api/:project_key/work_item/:work_item_type_key/meta
def get_type_item_meta(project_name, item_type_key):
    url = '{}/{}/work_item/{}/meta'.format(base_url, project_name, item_type_key)

    response = request.get(url, header=header)
    data = None
    if response:
        data = response['data']

    # 补充 meta 数据
    proj_path = os.path.dirname(os.path.dirname(__file__))
    with open(proj_path + "/resources/default_meta_refeed.conf", 'r') as f:
        lines = f.readlines()
        for line in lines:
            if len(line.split(":")) >= 4:
                elements = line.split(":")
                if elements[0] == project_name and item_type_key == get_type_list(project_name)[elements[1]]:
                    # 忽略重复的key-value
                    if elements[2] not in [i['field_key'] for i in data]:
                        data.append({"field_key": elements[2], "field_name": elements[3].strip()})

    return data


# 获取空间下工作项类型 /open_api/:project_key/work_item/all-types
def get_type_list(project_key):
    url = '{}/{}/work_item/all-types'.format(base_url, project_key)
    response = request.get(url, header=header)
    type_dict = {}
    if response:
        try:
            data = response['data']
            for res in data:
                if res['is_disable'] != 1:
                    type_dict.update({res['name']: res['type_key']})
        except AttributeError:
            print("project_key: " + project_key)
            print("response: " + response)
    return type_dict


# 获取空间下业务线详情
def get_business_list(project_name):
    url = '{}/{}/business/all'.format(base_url, project_name)
    response = request.get(url, header=header)
    bus_dict = {}
    if response:
        data = response['data']
        for r in data:
            bus_dict[r['id']] = r['name']
            # 目前只取3层关系
            for child in r['children'] \
                    if 'children' in r.keys() else []:
                bus_dict[child['id']] = bus_dict[child['parent']] + "/" + child['name']
                for sub_child in child['children'] \
                        if 'children' in child.keys() else []:
                    bus_dict[sub_child['id']] = bus_dict[sub_child['parent']] + "/" + sub_child['name']
    return bus_dict


# 获取指定的工作项列表（非跨空间）的分页数
def get_type_item_page_num(project_name, item_type_keys):
    url = '{}/{}/work_item/filter'.format(base_url, project_name)
    payload = {
        "work_item_type_keys": item_type_keys,  # list
        "page_size": 200,
    }
    response = request.post(url, header=header, payload=payload)

    page_num = 1
    if response:
        if 'pagination' in response:
            total = response['pagination']['total']
            if total > 200:
                page_num = math.ceil(total / 200)
    return page_num


# 获取指定分页的工作项列表（非跨空间）/open_api/:project_key/work_item/filter
def get_type_item_list(project_name, item_type_keys, page_num: Optional[int] = None):

    if isinstance(item_type_keys, str):
        item_type_keys = [item_type_keys]
    else:
        if not isinstance(item_type_keys, list):
            print("get_type_item_list Func Input item_type_keys type error!")
            raise TypeError
    url = '{}/{}/work_item/filter'.format(base_url, project_name)

    payload = {
        "work_item_type_keys": item_type_keys,  # list
        "page_size": 200,
    }
    result = []

    # 获取制定page的数据
    if page_num and page_num > 0:
        payload.update({"page_num": page_num})
        response = request.post(url, header=header, payload=payload)
        if response:
            result = response['data']
    else:
        # page_num 为空，则获取所有page的数据
        page_num = get_type_item_page_num(project_name, item_type_keys)
        for pn in range(1, page_num + 1):
            payload.update({"page_num": pn})
            response = request.post(url, header=header, payload=payload)
            if response:
                result += response['data']
    return result


# 获取指定的工作项详情 /open_api/:project_key/work_item/:work_item_type_key/query
# 该方法用于调试，工作项详情获取主要使用get_type_item_list方法分页批量获取
def get_work_item_dtl(project_name, item_type_key, work_item_ids):
    url = '{}/{}/work_item/{}/query'.format(base_url, project_name, item_type_key)
    if type(work_item_ids) == int:
        work_item_ids = [work_item_ids]
    else:
        if type(work_item_ids) == str:
            work_item_ids = [int(work_item_ids)]
    payload = {
        "work_item_ids": work_item_ids,  # list
        # "expand": {
        #     "need_workflow": True,
        #     "need_multi_text": True,
        #     "relation_fields_detail": True,
        # }
    }
    response = request.post(url, header=header, payload=payload)
    if response:
        return response['data']
    return []


# 获取指定的工作流详情 /open_api/:project_key/work_item/:work_item_type_key/:work_item_id/workflow/query
@time_cost
def get_work_flow_dtl(project_name, item_type_key, work_item_id, node_list):
    url = '{}/{}/work_item/{}/{}/workflow/query'.format(base_url, project_name, item_type_key, work_item_id)
    response = request.post(url, header=header, payload={})
    node_dtl_result = []
    node_list = [node_list] if isinstance(node_list, str) else node_list
    if response:
        try:
            workflow_nodes = response['data']['workflow_nodes'] \
                if 'workflow_nodes' in response['data'] else []
            workflow_nodes_valid = [node for node in workflow_nodes if node["name"] in node_list]
            for row in workflow_nodes_valid:
                node_dtl_result.append({
                    "name": row['name'],
                    'fields': [
                        {
                            i["field_key"]: i['field_value']['label']
                            if isinstance(i['field_value'], dict) and 'label' in i['field_value']
                            else i['field_value']
                        }
                        for i in row['fields']
                        if 'fields' in row.keys() and 'field_value' in i.keys()
                    ],
                    "sub_tasks": [
                        {
                            "name": i["name"],
                            "actual_begin_time": re.sub('T|Z', ' ', i["actual_begin_time"]).strip(),
                            "actual_finish_time": re.sub('T|Z', ' ', i["actual_finish_time"]).strip(),
                            "schedules": [
                                {
                                    "estimate_start_date": trans_unix_time(sch['estimate_start_date'])[:10]
                                    if 'estimate_start_date' in sch else 0,
                                    "estimate_end_date": trans_unix_time(sch['estimate_end_date'])[:10]
                                    if 'estimate_end_date' in sch else 0,
                                }
                                for sch in i["schedules"]
                            ]
                        }
                        for i in row['sub_tasks']
                    ]
                })
        except AttributeError:
            print("get_work_flow_dtl error: " + response)
            print("work_time_id: " + work_item_id)
    return node_dtl_result


# 获取用户名称
# parma:
#   user_keys: 需要查询的用户id
#   user_dict: 用户id名称缓存字典
# out:
#   user_list: 输出的用户列表
def get_user_list(user_ids):
    if user_ids == [] or \
            user_ids == [None] or user_ids == [''] or user_ids == [-1]:
        return ['']
    if user_ids == -1 or user_ids is None:
        return ['']

    # 从cache 中查找所有符合条件的用户名称
    user_list = [user_dict[u] for u in user_dict.keys() if u in user_ids]

    # 查找cache中未查询成功的用户id
    user_ids_keep = [u for u in user_ids if u not in user_dict.keys()]

    # 对user_ids_keep 通过api进行搜索
    if len(user_ids_keep) > 0 and isinstance(user_ids_keep[0], str):
        url = '{}/user/query'.format(base_url)
        payload = {
            "user_keys": user_ids_keep
        }
        response = request.post(url, header=header, payload=payload)

        try:
            if response:
                data = response['data']
                if isinstance(data, list):
                    for i in data:
                        if 'name_cn' in i.keys() and 'user_key' in i.keys():
                            user_list.append(i['name_cn'])
                            user_dict[i['user_key']] = i['name_cn']
        except TypeError or AttributeError:
            print("user_ids_keep: " + str(user_ids_keep))
            print("user_ids: " + str(user_ids))
            print("response: " + str(response))
    return user_list


# 解析获取版本号
def get_version_name(projects):
    version_dict = {}
    for proj in projects:
        result_meego = get_type_item_list(proj, 'version', 1)
        for r in result_meego:
            version_dict[r['id']] = r['name']
    return version_dict


if __name__ == "__main__":
    user_keys = [
        "7111622427955740676",
        "7029501294477869058",
        "7164797674179346460",
        "7128286145477099524",
        "7029497691709259778",
        "7103352855548919810"
    ]
    user_dict = {'7086350658462384131': 'x1', '7111622427955740676': 'x2'}
    # result = get_type_item_list_page_num('620e02272a92bcd1dbfa9f78', ['63355a0629ec60526839d1d0'])
    # result = get_work_flow_dtl('620e02272a92bcd1dbfa9f78', '63355a0629ec60526839d1d0', '13128444', "实施操作与自测")
    # result = get_type_item_meta('640eeb8dc852dd28018e7105', '648956232b2eea3d9013f958')

    result = get_business_list('v-voc')
    print(result)
