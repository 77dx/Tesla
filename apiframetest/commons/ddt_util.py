"""
@ Title:
@ Author: Cathy
@ Time: 2025/3/10 10:45
"""
import yaml
from os.path import exists
import logging

logger =logging.getLogger(__name__)

def read(file_path):
    logger.info(f"用例文件名:{file_path}")
    if exists(file_path):
        with open(file_path, encoding='utf-8', mode='r') as f:
            case_list = yaml.safe_load(f)
            logger.info(f"用例列表为：{case_list}")
            if case_list:
                # 此处给数据做处理，判断是单用例，流程用例和数据驱动用例
                if len(case_list) > 1:
                    # 流程用例
                    return [case_list]
                else:  # 数据驱动
                    if "parametrize" in dict(*case_list).keys():
                        new_case_list = ddts(*case_list)
                        logger.info(f"数据驱动用例列表为：{new_case_list}")
                        logger.info(f"数据驱动用例类型为：{type(new_case_list)}")
                        return new_case_list
                    else: # 单用例
                        return case_list
            else:
                raise Exception(f"{case_list}是空")
    else:
        raise Exception(f"{file_path} 不存在")

def ddts(caseinfo:dict):
    params = caseinfo.get("parametrize")
    str_caseinfo = yaml.dump(caseinfo)   # 将dict转成str处理
    new_caseinfo_list = []  # 最终要的格式是：[{}, {}, {}]
    for x in range(1, len(params)):   # 第一行是字段名
        raw_caseinfo = str_caseinfo   # 需要根据$ddt{param}匹配替换值，所以在每次循环替换后，字符串重置为原来带有$ddt{}
        for y in range(0, len(params[0])):  # 根据列数，循环替换各个字段的值
            raw_caseinfo = raw_caseinfo.replace("$ddt{"+params[0][y]+"}", str(params[x][y]))
        caseinfo_dict = yaml.safe_load(raw_caseinfo)   # str转dict
        caseinfo_dict.pop("parametrize")     # 实际测试执行时无需paramstrize字段
        new_caseinfo_list.append(caseinfo_dict)  # 处理成pytest ddt接受的格式：[{}, {}, {}]
    return new_caseinfo_list



if __name__ == '__main__':
    print(read("/apiframetest/testcases/django_login.yaml"))
    print("*"* 30)
    print(read("/Users/cathy/python_project/Tesla/apiframetest/testcases/flow_cases/flow_cases.yaml"))

