import json

import requests


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
    payload = json.dumps({
        "plugin_id": "MII_64BF73E313814002",
        "plugin_secret": "CC490B6545429495228191E74962621A"
    })
    response = requests.request("POST", url, headers=header, data=payload)

    data = json.loads(response.text)
    if 'data' in data and data['data'] != '':

        return data['data']['token']
    else:
        raise Exception('获取data异常!')


# 2.获取空间列表
def get_projects():
    url = 'https://project.feishu.cn/open_api/projects'
    header = get_header()
    body = json.dumps({
        "user_key": "7137587176702885916"
    })
    response = requests.request('POST', url, headers=header, data=body)
    # print(response.text)
    data = json.loads(response.text)
    return data['data']


# 3.获取空间下工作项类型
def get_project_type():
    url = 'https://project.feishu.cn/open_api/64b9ea9a523ec554280f4247/work_item/all-types'
    header = get_header()
    body = json.dumps({
        "project_key": "64b9ea9a523ec554280f4247"
    })
    response = requests.request('GET', url, headers=header, data=body)
    data = json.loads(response.text)

    return data


# 4.获取视图列表
def get_version_list():
    url='https://project.feishu.cn/open_api/64b9ea9a523ec554280f4247/view_conf/list'
    header=get_header()
    body=json.dumps({
        "project_key": "64b9ea9a523ec554280f4247",
        "work_item_type_key": "story"
    })
    result=requests.request('POST',url,headers=header,data=body)
    data = json.loads(result.text)
    data=data['data']
    list = []
    for re in data :
        list.append(re['view_id'])

    return  list

#5.获取视图下工作项列表
def get_version_work_list():
    data=[]
    for id in get_version_list():
        url='https://project.feishu.cn/open_api/64b9ea9a523ec554280f4247/fix_view/'+id+'?page_size=22&page_num=1'
        header=get_header()
        result=requests.request('GET',url,headers=header)
        result=json.loads(result.text)
        aa=result['data']['work_item_id_list']
        data.append(aa)
    data = [item for sublist in data for item in sublist]

    return data

if __name__ == '__main__':
    print(get_project_type())
