from meego.conn.load2mysql import load2mysql
from meego.core.model import *
from meego.core.process import *


if __name__ == "__main__":
    print("----------任务开始----------")


    config.root_project = "io_pmo"

    load_type = "mysql"
    is_mysql_init = True
    # --, "分产品部署任务", "私有化线上变更任务"
    proj_type_config = {"io_pmo": ["版本", "私有化线上变更任务"],
                        "datai": ["版本", "项目交付管理"],
                        "v-voc": ["需求"]
                        }

    ref_projects = config.ref_project.split(",")
    ref_version_dict = get_version_name(ref_projects)

    for proj in config.root_project.split(","):
        proj = proj.strip()

        type_dict = get_type_list(proj)
        business_dict = get_business_list(proj)

        info = {}
        for type_name in type_dict.keys():
            if type_name not in proj_type_config[proj]:
                continue
            info['project_name'] = proj
            info['type_name'] = type_name
            info['business'] = business_dict
            info['version'] = ref_version_dict

            # 获取空间下每个类型工作项元数据
            result_meta = get_type_item_meta(proj, type_dict[type_name])
            meta_list = meta_data_processing(result_meta, info)

            # 获取空间下的工作项列表
            result_meego = get_type_item_list(proj, type_dict[type_name])
            result_list = meego_data_processing(result_meego, info)

            print("开始写入 空间名称:{} 工作项:{} 的数据".format(proj, type_name))
            print("写入ing meta条数:{} 记录条数:{} ".format(len(meta_list), len(result_list)))
            load2mysql(meta_list, result_list, is_init=is_mysql_init)
            is_mysql_init = False
            print("完成写入 空间名称:{} 工作项:{} 的数据".format(proj, type_name))

    print("----------任务结束----------")
