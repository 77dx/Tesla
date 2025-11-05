"""
@ Title:
@ Author: Cathy
@ Time: 2025/2/27 14:50
"""
import pytest
import allure

from commons.requests_util import RequestsUtil
from commons.yaml_util import YamlUtil


@allure.epic("万师傅售后系统")
@allure.feature("用户模块")
class TestUser:
    api = YamlUtil('yamldata/api.yaml').read()

    def test_wsf_userinfo(self):
        data = TestUser.api["userinfo"]['request']
        res = RequestsUtil().send_all_requests(method=data['method'], url=data['url'])
        assert res.json()["code"] == "success"


    @allure.story("接口：增加用户")
    @allure.title("用例：增加用户成功")
    @allure.description('给万师傅后台系统添加一名用户')
    @allure.severity("致命")
    @allure.link('https://www.baidu.com', name="接口链接")
    def test_add_user(self):
        allure.attach("get", "请求方法", attachment_type = allure.attachment_type.TEXT)
        allure.attach("https://www.baidu.com", "请求路径", attachment_type = allure.attachment_type.TEXT)
        with allure.step("第一步：输入用户信息"):
            with open("/Users/cathy/Desktop/aa.png", 'rb') as f:
                allure.attach(body=f.read(), name="输入用户截图", attachment_type=allure.attachment_type.PNG)
        with allure.step("第二步：增加用户成功"):
            print("提交增加的用户")
        assert 1

    @pytest.mark.parametrize("userinfo", [{"username": "baili", "pwd": 123, "validate": True},
                                          {"username": "beifan", "pwd": 321, "validate": False}])
    def test_user_login(self, userinfo):
        print(f"输入用户名: {userinfo['username']}")
        print(f"输入密码: {userinfo['pwd']}")
        print("登录")
        assert userinfo["validate"]

    @pytest.mark.parametrize("userinfo", YamlUtil('yamldata/api.yaml').read())
    def test_user_login_2(self, userinfo):
        print("登录用例")
        print(userinfo["request"]["data"])
        assert 1

    @pytest.mark.usefixtures("create_user")
    def test_del_user(self):
        print("删除用户")
        assert 1

class TestOrder:
    def test_add_order(self):
        print("创建订单")
        assert 1

    def test_del_order(self):
        print("删除订单")
        assert 2

