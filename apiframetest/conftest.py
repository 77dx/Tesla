"""
@ Title:
@ Author: Cathy
@ Time: 2025/2/27 15:15
"""
import allure
import pytest
from pytest_xlsx.file import XlsxItem

from commons import yaml_util
from configs import setting

# 在执行用例前清除extract.yaml中的中间变量的值
@pytest.fixture(scope="session", autouse=True)
def clear_extract():
    yaml_util.clean(setting.extract_path)

@pytest.fixture(scope="function")
def execute():
    print("测试前生成数据")
    yield
    print("测试后清楚数据")

@pytest.fixture(scope="function", params=[{"username":"xiaoqi", "password":"123456"},{"username":"naicha", "password":"123456"}],
                ids=["success", "fail"])
def create_user(request):
    print(f"创建待删除的用户名和密码：{request.param['username']}，{request.param['password']}")


# 从kdt ui自动化迁移过来的
def pytest_xlsx_run_step(item: XlsxItem):
    if not hasattr(item, "kw"):
        item.kw = KeyWord(item.usefixtures)
    data = item.current_step

    key = data["关键字"]
    args = [data['参数']]
    args.extend(data['_BlankField'])
    remark = data["步骤名"]

    f = getattr(item.kw, key)
    f(*args)

    if item.kw.driver:
        png = item.kw.driver.get_screenshot_as_png()
        allure.attach(png, remark, allure.attachment_type)
    return 1















