"""
@ Title:
@ Author: Cathy
@ Time: 2025/2/27 15:15
"""
import allure
import pytest
import yaml
from pytest_xlsx.file import XlsxItem

# from Tesla import settings
# from commons import yaml_util
from configs import setting

# 在执行用例前清除extract.yaml中的中间变量的值
# 目前文件地址是写死的，先手动处理
@pytest.fixture(scope="session", autouse=True)
def clear_extract():
    ...
    # yaml_util.clean(settings.EXTRACT_PATH)

@pytest.fixture(scope="function")
def execute():
    print("测试前生成数据")
    yield
    print("测试后清楚数据")

@pytest.fixture(scope="function", params=[{"username":"xiaoqi", "password":"123456"},{"username":"naicha", "password":"123456"}],
                ids=["success", "fail"])
def create_user(request):
    print(f"创建待删除的用户名和密码：{request.param['username']}，{request.param['password']}")

# 支持 YAML 测试用例文件的收集
def pytest_collect_file(parent, file_path):
    """自定义文件收集钩子，支持 YAML 测试文件"""
    if file_path.suffix in [".yaml", ".yml"] and file_path.name.startswith("test_"):
        return YamlFile.from_parent(parent, path=file_path)

class YamlFile(pytest.File):
    """YAML 测试文件处理器"""
    def collect(self):
        """读取 yaml 文件并生成测试项"""
        with open(self.path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        
        if isinstance(data, list):
            for index, case in enumerate(data):
                yield YamlTest.from_parent(
                    self,
                    name=f"{self.path.name}::case_{index}",
                    case_data=case
                )
        else:
            yield YamlTest.from_parent(
                self,
                name=f"{self.path.name}::case",
                case_data=data
            )

class YamlTest(pytest.Item):
    """YAML 测试用例项"""
    def __init__(self, name, parent, case_data):
        super().__init__(name, parent)
        self.case_data = case_data

    def runtest(self):
        """执行 YAML 测试逻辑"""
        # 这里添加实际的测试执行逻辑
        # 目前只是简单示例
        print(f"执行测试用例: {self.name}")
        print(f"测试数据: {self.case_data}")
        
        # 模拟测试执行
        if self.case_data.get("title"):
            print(f"测试标题: {self.case_data['title']}")















