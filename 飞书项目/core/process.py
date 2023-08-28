import re

from meego.core.model import get_user_list
from meego.util.utils import trans_unix_time, time_cost


# 工作项数据处理
@time_cost
def meego_data_processing(result, info):
    version_dict = info['version']
    business_dict = info['business']
    result_list_all = []  # 所有数据放入列表中，便于批量插入mysql
    for r in result:  # 每一行记录

        def business_invalid_check():
            business_value = [field['field_value'] for field in r['fields'] if field['field_type_key'] == 'business']
            if len(business_value) > 0:
                business_key = business_value[0]
                if business_key in business_dict:
                    if re.search(
                            r"经营平台|云基础|研发中台|计算|安全|视频与边缘|云通信",
                            business_dict[business_key],
                            re.I
                    ):
                        return True
            return False
        # 跳过无关的业务线
        if business_invalid_check():
            continue

        id = r['id']  # 工作项id
        name = r['name']  # 工作项名称
        pattern = r['pattern']  # 工作项模式,分为节点模式(Node)/状态模式(State)
        project_key = r['project_key']  # 空间id（project_key）
        simple_name = r['simple_name']  # 空间域名（simple_name）
        state_times = r['state_times'] if 'state_times' in r.keys() else ''  # 节点时间
        sub_stage = r['sub_stage']  # 需求状态(仅需求有值)
        template_id = r['template_id']  # 使用的模板id
        template_type = r['template_type']  # 模板类型
        created_at = trans_unix_time(r['created_at'])  # 创建时间 毫秒时间戳
        created_by = get_user_list([r['created_by']])  # 创建者userKey
        deleted_at = trans_unix_time(r['deleted_at'])  # 删除时间戳，毫秒精度
        deleted_by = get_user_list([r['deleted_by']])  # 删除人user_key
        updated_at = trans_unix_time(r['updated_at'])  # 更新时间 毫秒时间戳
        updated_by = get_user_list([(r['updated_by'])])  # 更新者userKey
        work_item_status = r['work_item_status']  # ## 工作项状态(除需求外有值)
        work_item_type_key = r['work_item_type_key']  # 工作项类
        current_nodes = r['current_nodes']  # ##当前进行中节点(仅节点流有值)

        # 处理公共字段
        result_list = [str(id), name, str(pattern), str(project_key), str(simple_name), str(state_times),
                       str(template_id), str(sub_stage), str(template_type), str(updated_at), str(updated_by),
                       str(work_item_status), str(work_item_type_key), str(created_at), str(created_by),
                       str(current_nodes), str(deleted_by), str(deleted_at)]

        # 处理工作流：QA验收/实施操作与自测等节点信息
        qa_workflow_list = []
        # 节点模式下，额外读取config.workflow_nodes 配置中节点信息做补充.
        # work_item_type_key暂时写死，为63355a0629ec60526839d1d0即"私有化线上变更任务"
        # 单次请求 平均时长在0.5s, 耗时不可接受, 任务需要独立出去
        # if pattern == 'Node':
        #     # 63355a0629ec60526839d1d0
        #     if work_item_type_key == '63355a0629ec60526839d1d0':
        #         qa_workflow_list = get_work_flow_dtl(
        #             project_key,
        #             work_item_type_key,
        #             id,
        #             config.workflow_nodes.split(",")
        #         )

        result_list.extend([str(qa_workflow_list)])

        fields = r['fields']  # ##工作项字段
        f_list = []
        # 处理工作项字段
        # 根据field_type_key 类别的不同，分别处理
        for i in fields:
            if i['field_type_key'] == 'multi_select':
                m_list = []
                if type(i['field_value']) == list:
                    try:
                        for m in i['field_value']:
                            m_list.append(str(m['label']))
                    except TypeError:
                        m_list = []
                f_list = [str(i['field_key']),
                          str(i['field_type_key']),
                          str(m_list),
                          '',
                          info['type_name']]
            elif i['field_type_key'] == 'work_item_related_multi_select':
                m_list = []
                if type(i['field_value']) == list:
                    for m in i['field_value']:
                        if m in version_dict.keys():
                            m_list.append(version_dict[m])
                        else:
                            m_list.append(m)
                f_list = [str(i['field_key']),
                          str(i['field_type_key']),
                          str(m_list),
                          '',
                          info['type_name']]
            elif i['field_type_key'] == 'select' and isinstance(i['field_value'], dict):
                f_list = [str(i['field_key']),
                          str(i['field_type_key']),
                          str(i['field_value']['label']),
                          str(i['field_value']['value']),
                          info['type_name']]
            elif i['field_type_key'] == 'date':
                f_list = [str(i['field_key']),
                          str(i['field_type_key']),
                          str(trans_unix_time(i['field_value'])),
                          '',
                          info['type_name']]
            elif i['field_type_key'] == 'user':
                f_list = [str(i['field_key']),
                          str(i['field_type_key']),
                          str(get_user_list([i['field_value']])),
                          '',
                          info['type_name']]
            elif i['field_type_key'] == 'multi_user':
                f_list = [str(i['field_key']),
                          str(i['field_type_key']),
                          str(get_user_list(i['field_value'])),
                          '',
                          info['type_name']]
            elif i['field_type_key'] == 'business':
                f_list = [str(i['field_key']),
                          str(i['field_type_key']),
                          str(business_dict[i['field_value']]) if i['field_value'] in business_dict.keys()
                          else str(i['field_value']),
                          '',
                          info['type_name']]

            elif i['field_type_key'] == 'work_item_related_select':
                if i['field_value'] in version_dict.keys():
                    version_name = version_dict[i['field_value']]
                else:
                    version_name = i['field_value']
                f_list = [str(i['field_key']),
                          str(i['field_type_key']),
                          str(version_name),
                          '',
                          info['type_name']]
            # role_owners 需要多行处理
            elif i['field_type_key'] == 'role_owners' and isinstance(i['field_value'], list):
                for v in i['field_value']:
                    result_list_all.append(
                        result_list + [
                            str(v['role']),
                            str(i['field_type_key']),
                            str(get_user_list(v['owners'])),
                            '',
                            info['type_name']
                        ])
            else:
                f_list = [str(i['field_key']),
                          str(i['field_type_key']),
                          str(i['field_value']),
                          '',
                          info['type_name']]
            result_list_all.append(result_list + f_list.copy())
    return result_list_all


# 元数据解析处理
@time_cost
def meta_data_processing(result, info):
    meta_list_all = []
    for r in result:
        r['field_type_key'] = r['field_type_key'] if 'field_type_key' in r else ''
        r['label'] = r['label'] if 'label' in r else ''
        if r['field_type_key'] == 'select':
            for o in r['options']:
                meta_list_all.append([
                                         info['project_name'],
                                         info['type_name'],
                                         r['field_key'],
                                         r['field_name'],
                                         r['field_type_key'],
                                         o['label'],
                                         o['value']
                                     ])
        elif r['field_type_key'] == 'role_owners':
            for ro in r['role_assign']:
                meta_list_all.append([
                                         info['project_name'],
                                         info['type_name'],
                                         ro['role'],
                                         ro['name'],
                                         r['field_type_key'],
                                         '',
                                         ''
                                     ])
        else:
            meta_list_all.append([
                                     info['project_name'],
                                     info['type_name'],
                                     r['field_key'],
                                     r['field_name'],
                                     r['field_type_key'],
                                     r['label'],
                                     ''
                                 ])
    return meta_list_all
