from django.test import TestCase

# Create your tests here.
"""
需求1：实现一个注册功能
    1. 字段
        1. username
        2. password
        3. email
        4. create_time
        5. update_time
    2. 功能
        1. 注册页面有username, password, password_comfirm, email, submit, reset --- 前端未实现
        2. password和password_comfirm校验一致 ---ok
        3. 所有字段不能为空 --- ok
        4. submit发送请求 ---使用了接口请求
        5. reset清空输入框内容
        6. 验证邮箱格式 ---ok
        7. 判断用户名是否重复
        8. 保存用户信息至数据库
"""
import sys
import subprocess
python_path = sys.executable
# print(python_path)
# process = subprocess.run(['pwd'], cwd='/Users/cathy', stdout=subprocess.PIPE, stderr=subprocess.PIPE)
# print(process.stdout.decode())

result = subprocess.run(['ls', '-l'], capture_output=True, text=True)
# print(result.stdout)
# print(result.returncode)

str1 = "hello"
print(str1.encode())

# class Person:
#     def __init__(self, name):
#         self.name = name
#
#
#     def __str__(self):
#         return "%sObject(%s)" % (self.__class__.__name__, self.name)
#
#
#     def __repr__(self):
#         return (
#             f"<{self.__class__.__qualname__}: model={self.model.__qualname__} "
#             f"site={self.admin_site!r}>"
#         )
# p = Person("zhangsan")
# print(p)

# import requests
#
# url = 'http://127.0.0.1:8000/beifan/register'
# case_data = {
#     "username": "marks",
#     "password": "123456",
#     "password_confirm": "123456",
#     "email": "marks@qq.com"
# }
# headers = {"content_type": "application/json"}
# response = requests.post(url=url, case_data=case_data, headers=headers)
# print(response.status_code)

# from django.test.client import Client
# import pytest
#
# @pytest.fixture
# def client():
#     return Client()
#
# def test_reister_get(client):
#     resp = client.get('/beifan/register')
#     html = resp.content.decode()
#     print(html)
