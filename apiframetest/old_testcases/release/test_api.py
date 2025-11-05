"""
@ Title:
@ Author: Cathy
@ Time: 2025/2/28 15:45
"""
from commons.yaml_util import YamlUtil
from commons.requests_util import RequestsUtil

class TestApi:
    api = YamlUtil('yamldata/api.yaml').read()

    def test_wsf_login(self):
        data = TestApi.api["login"]['request']
        res = RequestsUtil().send_all_requests(method=data['method'], url=data['url'], data=data['data'], headers=data['headers'])
        res_data = res.json()
        wsf_user_token = res_data["data"]["appToken"]
        YamlUtil('extract.yaml').write({"wsf_user_token": wsf_user_token}, 'a+')
        res_code = res.status_code
        assert res_code == 200

    def test_wsf_order_list(self):
        data = TestApi.api["order_list"]['request']
        res = RequestsUtil().send_all_requests(method=data['method'],url=data['url'], data=data['data'], headers=data['headers'])
        code = res.json()["code"]
        assert code == "success"
