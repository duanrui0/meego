# -*- coding: utf-8 -*-
# ********************************************************************
# Author: chensong.csongbj
# CreateTime: 2023-03-22 17:39:24
# Description:
# Update: Task Update Description
# 5/16 优化user字典的获取逻辑
# ********************************************************************

from meego.conn.hive import *
from meego.core.model import *
from meego.core.process import *
import pandas as pd
import bytedtqs as tqs
import subprocess
import sys

if __name__ == "__main__":
    print("----------任务开始----------")

    # 初始化TQS 客户端
    client = tqs.TQSClient(app_id=config.app_id, app_key=config.app_key)

    # 初始化 user_dict
    user_dict.update({'system_validity': '', 'automation': ''})
    try:
        # 初始化数据从成员id及成员的映射表取
        user_query = "select user_id, user_name from eps_dsc_data.ods_people_sys_member_prefix_mapping;"
        query_job = client.execute_query(user_name='chensong.csongbj', query=user_query)
        if query_job.is_success():
            rows = query_job.get_result().fetch_all_data()
            df = pd.DataFrame(rows[1:], columns=rows[0])
            user_dict.update(dict(user_dict, **dict(zip(df['user_id'], df['user_name']))))
    except Exception as e:
        print(e)

    # 在数据更新前，备份初始化的用户字典
    user_dict_init = user_dict.copy()

    # 配置需要装配的飞书空间及工作项类型
    config.root_project = "io_pmo,datai,v-voc"
    proj_type_config = {
        "io_pmo": ["缺陷", "版本", "分产品部署任务", "私有化线上变更任务"],
        "datai": ["需求", "项目评估", "项目交付管理", "数据开发统计", "数据校验", "工作项预估", "风险记录"],
        "v-voc": ["需求"]
    }

    # 初始化meta数据列表及数据表列表；考虑到hive需要表头【字段信息】，补充表头信息。
    meta_list_all, result_list_all = [], []
    meta_list_all.append(['project_name', 'type_name', 'field_key', 'field_name', 'field_type_key', 'label', 'value'])
    result_list_all.append(['id', 'name', 'pattern', 'project_key', 'simple_name', 'state_times', 'template_id',
                            'sub_stage', 'template_type', 'updated_at', 'updated_by', 'work_item_status',
                            'work_item_type_key', 'created_at', 'created_by', 'current_nodes', 'deleted_by',
                            'deleted_at', 'workflow_node_info', 'field_key', 'field_type_key', 'label', 'value',
                            'type_name'])

    ref_projects = config.ref_project.split(",")
    ref_version_dict = get_version_name(ref_projects)
    # 数据处理
    for proj in config.root_project.split(","):
        proj = proj.strip()

        type_dict = get_type_list(proj)
        business_dict = get_business_list(proj)

        # bar = tqdm(type_dict.keys())

        info = {}
        for type_name in type_dict.keys():
            if type_name not in proj_type_config[proj]:
                continue
            # bar.set_description("{0}空间下类型为【{1}】的工作项列表正在处理中".format(proj, type_name))
            info['project_name'] = proj
            info['type_name'] = type_name
            info['business'] = business_dict
            info['version'] = ref_version_dict

            print("start calc proj %s, work_item type %s".format(proj, type_name))
            # 获取空间下每个类型工作项元数据
            result_meta = get_type_item_meta(proj, type_dict[type_name])
            meta_list_all += meta_data_processing(result_meta, info)

            # 获取指定空间的工作项列表
            result_meego = get_type_item_list(proj, type_dict[type_name])
            result_list_all += meego_data_processing(result_meego, info)

    # 更新meego hive表（包含meta 表和数据表）
    execute(meta_list_all, "eps_dsc_data.ods_feishu_meego_projects_meta_df", "${date}", client)
    execute(result_list_all, "eps_dsc_data.ods_feishu_meego_projects_df", "${date}", client)

    dict_size = sys.getsizeof(user_dict)

    print("字典的大小（字节数）：", dict_size)
    ##################################################################################################
    # # 更新用户字典user_dict 的 hive 底表

    # # 获取需要更新的用户字典key 列表
    # ext_user_keys = user_dict.keys() - user_dict_init.keys()

    # # 用户字典key 列表每次最多更新50条 , 考虑到拼接的SQL可能会过长，超过限制
    # pick_keys_ind = max(100, len(ext_user_keys))

    # # 拼接需要插入的用户字典数据SQL
    # insert_query = "insert into eps_dsc_data.ods_people_sys_member_prefix_mapping(user_id, user_name) "
    # for ext_user in list(ext_user_keys)[:pick_keys_ind]:
    #     insert_query += " select '{}','{}' union ".format(ext_user, user_dict[ext_user])

    # insert_query = insert_query.rstrip('union ')
    # print(insert_query)

    # # 执行插入用户字典数据SQL语句
    # try:
    #     insert_job = client.execute_query(user_name='chensong.csongbj', query=insert_query)
    #     if insert_job.is_success():
    #         print('--------- [user_dict refresh ok] -----------')
    # except Exception as e:
    #     print(e)

    # 结束
    print("----------任务结束----------")
