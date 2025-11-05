"""
@ Title:
@ Author: Cathy
@ Time: 2025/2/27 14:53
"""
import os
import shutil
import time
import pytest
import yaml
from commons import yaml_util
from configs import setting

def get_token():
    import requests
    url = 'https://user-site-api.wanshifu.com/user/security/login'
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "principal": "18791716437",
        "password": "Cathy8877"
    }
    res = requests.post(url, headers=headers, data=data)
    return res


def use_extract_value(request_data):
    # 将request转换成str
    request_data_str = yaml.safe_dump(request_data)
    # 进行字符串替换
    from string import Template
    new_request_data = Template(request_data_str).safe_substitute(yaml_util.read(setting.extract_path))
    # 将字符串还原成字典
    request_data_dict = yaml.safe_load(new_request_data)

    return request_data_dict

if __name__ == '__main__':
    # print(get_token().json())
    pytest.main()
    os.system("allure generate ./temps -o ./reports --clean")
    os.system("allure open ./reports")
    # shutil.move("logs/frame.log", "logs/frame_"+str(int(time.time())) + ".log")