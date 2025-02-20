"""
@ Title:
@ Author: Cathy
@ Time: 2024/12/9 17:52
"""
"""
将json数据转换为yaml数据，然后保存进yaml文件中。
    1。读取json文件数据   
    2。解析json, 构造yaml格式
    3。写入yaml
    
    # json.loads(str), 将字符串转成字典
    # json.dumps(dict), 将字典转为字符串
"""
import json
from pathlib import Path
from ruamel.yaml import YAML


json_path = "beifan/api_json/beifan.json"

def to_yaml(json_path):
    # 处理path
    p = Path(__file__).resolve().parent.parent   # 根目录
    jp = p / json_path   # 拼接json文件地址
    yp = jp.parent / f"{jp.stem}.yaml"   # 在json同级生成相同名称的yaml文件

    # 创建一个YAML处理器
    yaml = YAML()
    yaml.preserve_quotes = True  # 保持字符串的引号
    yaml.default_flow_style = False  # 使用块状风格

    with open(jp, 'r', encoding="utf-8") as f:
        data = f.read()
    data = json.loads(data)

    # 写入文件
    with open(yp, 'w', encoding='utf-8') as fp:
        yaml.dump(data, fp)



if __name__ == '__main__':
    to_yaml(json_path)



