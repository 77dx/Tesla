"""
@ Title:
@ Author: Cathy
@ Time: 2025/3/5 15:25
"""
import copy
import logging

from jsonpath import jsonpath
from apiframetest.commons.log_util import logger


class AssertUtil:

    def assert_all_case(self, res, assert_type, assert_data):
        new_res = copy.deepcopy(res)
        try:
         new_res.json = res.json()
        except Exception:
            new_res.json = {"msg": "response not json data"}

        for msg, assert_value in assert_data.items():
            expect, actual = assert_value[0], assert_value[1]
            # 获取实际结果
            # 1. 利用反射得到res中的属性值,先用不太高级的类型判断吧
            if not isinstance(actual, list):
                try:
                    actual_value = getattr(new_res, actual)
                except Exception:
                    actual_value = actual
            # 2. 根据设置的jsonpath提取res中的值
            else:
                attr_name = actual[0] # res中的属性名称
                expr = actual[1]      # jsonpath表达式
                index = actual[2]     # 取第几个值
                res_attr_data = getattr(new_res, attr_name)
                res_assert_data_list = jsonpath(res_attr_data, expr)
                actual_value = res_assert_data_list[index]
            match assert_type:
                case "equals":
                    assert expect == actual_value, msg
                case "contains":
                    assert actual_value in expect, msg
                case "db_equals":
                    pass
                case "db_contains":
                    pass


if __name__ == '__main__':
    s1 = "success_ok"
    s2 = "success"
    print(s1.__contains__(s2))







