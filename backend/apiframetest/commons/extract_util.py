"""
[DEPRECATED] apiframetest.commons.extract_util
此模块已废弃，请使用 case_api.engine.Extractor 和 case_api.engine.VarResolver 替代。
保留仅供参考，请勿在新功能中使用。
"""
# [DEPRECATED] 2026-03-12: 新版执行引擎已移至 case_api/engine.py
#   - VarResolver  替代本模块的变量替换功能
#   - Extractor    替代本模块的变量提取功能

import copy
import re
import yaml
import os
from jsonpath import jsonpath

from apiframetest.commons import yaml_util
from string import Template

from apiframetest.commons.log_util import logger
from apiframetest.hotload.debug_talk import DebugTalk
import redis

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

        extract_data = {var_name: extract_value_list[index]}
        backend = os.getenv("APIFRAME_CONTEXT_BACKEND", "file").lower()
        if backend == "redis":
            redis_url = os.getenv("APIFRAME_REDIS_URL") or os.getenv("CELERY_BROKER_URL") or "redis://127.0.0.1:6379/0"
            prefix = os.getenv("APIFRAME_CONTEXT_PREFIX", "")
            redis_key = f"{prefix}:context" if prefix else "apiframe:context"

            r = redis.Redis.from_url(redis_url, decode_responses=True)
            r.hset(redis_key, mapping={var_name: str(extract_value_list[index])})
            logger.info(f"数据提取成功{extract_data},保存至redis:{redis_key}")
            return

        # file backend (默认)
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

    def _replace_vars(self, data_str: str) -> str:
        """
        从 Redis 或 extract.yaml 中读取上下文变量，替换 ${varName} 占位符。
        注意：只替换简单变量格式，函数调用格式 ${func()} 由 hot_replace 处理。
        """
        backend = os.getenv("APIFRAME_CONTEXT_BACKEND", "file").lower()

        if backend == "redis":
            redis_url = (
                os.getenv("APIFRAME_REDIS_URL")
                or os.getenv("CELERY_BROKER_URL")
                or "redis://127.0.0.1:6379/0"
            )
            prefix = os.getenv("APIFRAME_CONTEXT_PREFIX", "")
            redis_key = f"{prefix}:context" if prefix else "apiframe:context"
            try:
                r = redis.Redis.from_url(redis_url, decode_responses=True)
                var_store = r.hgetall(redis_key)
                logger.info(f"[变量替换] 从 Redis ({redis_key}) 读取到变量: {list(var_store.keys())}")
            except Exception as e:
                logger.error(f"[变量替换] Redis 读取失败: {e}")
                var_store = {}
        else:
            try:
                var_store = yaml_util.read(os.getenv("APIFRAME_EXTRACT_PATH", "../extract.yaml")) or {}
                logger.info(f"[变量替换] 从文件读取到变量: {list(var_store.keys())}")
            except Exception as e:
                logger.warning(f"[变量替换] 读取 extract.yaml 失败: {e}")
                var_store = {}

        if not var_store:
            return data_str

        # 只替换简单变量 ${varName}，排除函数调用 ${func(...)}
        def _replacer(m):
            name = m.group(1)
            if name in var_store:
                logger.info(f"[变量替换] ${{{name}}} -> {var_store[name]!r}")
                return str(var_store[name])
            logger.warning(f"[变量替换] ${{{name}}} 未找到对应变量，保留原文")
            return m.group(0)

        # 使用负向前瞻排除函数调用格式 ${func(...)}
        return re.sub(r'\$\{(\w+)(?!\s*\()\}', _replacer, data_str)

    def change(self, request_data):
        # 将request转换成str
        new_request_data = yaml.safe_dump(request_data)
        # 1. 替换函数调用 ${func()}
        changed_request_data = self.hot_replace(new_request_data)
        # 2. 替换上下文变量 ${varName}
        changed_request_data = self._replace_vars(changed_request_data)
        # 将字符串还原成字典
        request_data_dict = yaml.safe_load(changed_request_data)
        return request_data_dict


#
# if __name__ == '__main__':
#     data_str = '{"username": "cathy", "token": "${yaml_read(extract.yaml,token)}"}'
#     # new_data = ExtractUtil().hot_replace(data_str)
#     # print(new_data)



