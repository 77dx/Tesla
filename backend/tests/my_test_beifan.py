"""
@ Title:
@ Author: Cathy
@ Time: 2024/11/4 15:24
"""
from django.test.client import Client
from django.contrib.auth.models import User
import pytest
import json

@pytest.fixture
def client():
    return Client()

@pytest.fixture()
def user(_django_db_helper):
    new_user = User.objects.create_user()

@pytest.mark.parametrize(
    "case_data, code, msg",
    [
        ({
            "username": "marks",
            "password": "",
            "password_confirm": "123456",
            "email": "marks@qq.com"
        }, 0, "['password'] 不能为空！"),
        ({
            "username": "marks",
            "password": "12345",
            "password_confirm": "12345",
            "email": "marks@qq.com"
        }, 0, "用户名不能重复！"),
        ({
            "username": "marks",
            "password": "123456",
            "password_confirm": "123456",
            "email": "marks@qq.com"
        }, 0, "密码长度不能小于6位！"),
        ({
            "username": "marks",
            "password": "1234567",
            "password_confirm": "123456",
            "email": "marks@qq.com"
        }, 0, "两次密码输入不一致！"),
        ({
            "username": "marks",
            "password": "1234567",
            "password_confirm": "123456",
            "email": "marks11111qq.com"
        }, 0, "邮箱格式不正确！"),
    ]
)
def test_reister_post(client, data, code, msg):
    resp = client.post('/beifan/register', data=data, content_type="application/json")
    html = resp.content.decode()
    print(html)
    resp_json = json.loads(html)
    assert resp_json["code"] == code
    assert resp_json["msg"] == msg