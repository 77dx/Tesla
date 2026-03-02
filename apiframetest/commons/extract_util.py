"""
@ Title:
@ Author: Cathy
@ Time: 2025/3/4 14:28
"""
import copy
import re
import yaml
from jsonpath import jsonpath

from apiframetest.commons import yaml_util
from string import Template

from apiframetest.commons.log_util import logger
from apiframetest.hotload.debug_talk import DebugTalk

class ExtractUtil:
    # 从响应数据中提取字段
    def extract_key(self, yaml_file, res, var_name, attr_name, expr, index):
        new_res = copy.deepcopy(res)
        new_res.json = res.json()
        data = getattr(new_res, attr_name)  # 获取res.json()的值
        # 在data中根据提取表达式提取数据
        if expr.startswith("$"):
            extract_value_list = jsonpath(data, expr)
        else:  # 正则的处理
            extract_value_list = re.findall(expr, data)
        # 将这些提取的值保存到extract.yaml
        extract_data = {var_name: extract_value_list[index]}
        yaml_util.write(yaml_file, datas=extract_data, mode='a+')
        logger.info(f"数据提取成功{extract_data},保存至extract.yaml中")

    # 替换request中${}的数据---已废弃
    def use_extract_value(self, request_data):
        # 将request转换成str
        request_data_str = yaml.safe_dump(request_data)
        # 进行字符串替换
        new_request_data = Template(request_data_str).safe_substitute(yaml_util.read('../extract.yaml'))
        # 将字符串还原成字典
        request_data_dict = yaml.safe_load(new_request_data)
        return request_data_dict

    def hot_replace(self, data_str):
        regexp = "\\$\\{(.*?)\\((.*?)\\)\\}"  # 捕获“token”: {函数名(参数1，参数2)}，参数部分注意空格
        func_list = re.findall(regexp, data_str)
        if func_list:
            for func in func_list:
                # 判断函数是否有参数
                if func[1] == '': # 无参数
                    new_values = getattr(DebugTalk(), func[0])()
                else:
                    params = func[1].split(',') # 有参数
                    new_values = getattr(DebugTalk(), func[0])(*params)
                # 处理"1"的问题
                if isinstance(new_values, str) and new_values.isdigit():
                    new_values = int(new_values)
                # 把调用函数返回的值拼接进原有的数据中
                old_value = '${'+ func[0] + '('+func[1]+')}'
                data_str = data_str.replace(old_value, str(new_values))
        return data_str

    def change(self, request_data):
        # 将request转换成str
        new_request_data = yaml.safe_dump(request_data)
        # 读取数据并替换
        changed_request_data = self.hot_replace(new_request_data)
        # 将字符串还原成字典
        request_data_dict = yaml.safe_load(changed_request_data)

        return request_data_dict


#
# if __name__ == '__main__':
#     data_str = '{"username": "cathy", "token": "${yaml_read(extract.yaml,token)}"}'
#     # new_data = ExtractUtil().hot_replace(data_str)
#     # print(new_data)



