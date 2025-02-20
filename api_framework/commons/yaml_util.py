"""
@ Title:
@ Author: Cathy
@ Time: 2024/11/20 15:36
"""
import yaml

extract_yaml = "../extract.yaml"
# 读取yaml数据
def read_yaml(file_path=extract_yaml):
    with open(file_path, encoding="utf-8") as f:
        value = yaml.safe_load(f)
    return value

# 给yaml中写入数据
def write_yaml(file_path=extract_yaml, data=None):
    with open(file_path, encoding="utf-8", mode="a+") as f:
        yaml.safe_dump(data, f, allow_unicode=True)

# 清空yaml文件
def clean_yaml(file_path=extract_yaml):
    with open(file_path, encoding="utf-8", mode="w") as f:
        ...


if __name__ == '__main__':
    write_yaml(data={"token": "hdkj68e932y4uhjdsk"})
    print(read_yaml())
    clean_yaml()


