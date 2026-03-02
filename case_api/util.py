import logging
import time
import yaml
from pathlib import Path
from os.path import exists
from ruamel.yaml import safe_dump
from Tesla import settings
from case_api.models import Case, Endpoint
from project.models import Project

# 需要和apiframetest对接，把接口和用例的数据读取出来，按照框架约定的格式写入yaml文件，
# 然后再调用apiframetest方法运行用例。

logger = logging.getLogger(__name__)

class GenerateCase:
    def __init__(self, endpoint_id):
        self.endpoint_id = endpoint_id

        # 查询cased对应的endpoint
        self.endpoint = Endpoint.objects.get(pk=endpoint_id)
        logger.info(f"接口信息{self.endpoint}")

        # 查询接口的用例
        self.case_data_list = Case.objects.filter(endpoint_id=endpoint_id)
        logger.info(f"查询接口的用例{self.case_data_list}")

        # 项目名称
        self.feature = Project.objects.get(id=self.endpoint.project_id).name
        logger.info(f"项目名称{self.feature}")

        # 写入cookies
        if self.endpoint.cookies:
            cookies_str = ""
            for k, v in self.endpoint.cookies.items():
                cookies_str += f"{k}={v};"
            self.endpoint.headers["cookie"] = cookies_str

        # api框架的数据格式
        self.YAML_TEMPLATE = {
            "feature": self.feature,
            "story": self.endpoint.name,
            "title": self.endpoint.name,
            "request": {
                "url": self.endpoint.url,
                "method": self.endpoint.method,
                "headers": self.endpoint.headers
            },
            "parametrize": [],
            "extract": {},
            "validate": {}
        }
    # 将数据库的接口数据转换成yaml文件
    def to_yaml(self, path=None):
        yaml_data = self.YAML_TEMPLATE.copy()
        # 处理request中data部分
        keys_list = []
        values_list = []
        data_type = ""
        for case in self.case_data_list:
            # extract
            if case.extract:
                yaml_data["extract"] = case.extract
            # validate
            yaml_data["validate"] = case.validate

            for key in ['params', 'data', 'json', 'files']:
                value = case.api_args.get(key)
                if value not in [None, '', {}, []]:
                    yaml_data["request"][key] = value
                    data_type = key
            keys_list = [key for key in yaml_data["request"][data_type].keys()]
            logger.info(f"接口入参的key：:{keys_list}")
            value_list = []
            for value in yaml_data["request"][data_type].values():
                l = []
                if len(l) < 2:
                    l.append(value)
                value_list.extend(l)
            values_list.append(value_list)
        logger.info(f"入参的values列表:：{values_list}")

        # 如果values_list长度大于1，则需要处理成ddt
        if len(values_list) > 1:
            parametrize = []
            parametrize.append(keys_list)
            parametrize.extend(values_list)
            for key in keys_list:
                yaml_data["request"][data_type][key] = '$ddt{' + key + '}'
            yaml_data["parametrize"] = parametrize
            logger.info(f"要写入的ddt_yaml数据为：{yaml_data}")
        else:
            yaml_data["request"][data_type] = dict(zip(keys_list, values_list[0]))
            logger.info(f"要写入的single_yaml数据为：{yaml_data}")

        # 写入yaml文件
        try:
            if path is None:
                file_path = f"{settings.TEST_YAML_PATH}/test_{self.endpoint.name}_{round(time.time())}.yaml"
            else:
                # 检查path是否为目录，如果是则生成文件名
                path_obj = Path(path)
                if path_obj.is_dir():
                    file_path = path_obj / f"test_{self.endpoint.name}_{round(time.time())}.yaml"
                else:
                    file_path = path_obj
                file_path = str(file_path)
                
            with open(file_path, 'w', encoding="utf-8") as f:
                data_to_dump = [yaml_data] if len(values_list)>1 else yaml_data
                yaml.dump(data_to_dump, f,
                               allow_unicode= True,
                               default_flow_style= False,
                               indent=4,
                               sort_keys= False)
            logger.info(f"YAML文件生成成功: {file_path}")
            return file_path
        except Exception as e:
            logger.error(f"写入yaml文件失败：{e}")
            return None


