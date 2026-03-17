"""
@ Title:
@ Author: Cathy
@ Time: 2025/2/28 11:15
"""
import logging
import os
import yaml

logger = logging.getLogger(__name__)

def read(file_path):
    with open(file_path, encoding='utf-8', mode='r') as f:
        value = yaml.safe_load(f)
    return value

def write(file_path, datas, mode):
    if mode == 'w':
        with open(file_path, encoding='utf-8', mode='w') as f:
            yaml.safe_dump(datas, f, allow_unicode=True)
    if mode == 'a+':
        with open(file_path, encoding='utf-8', mode='a+') as f:
            yaml.safe_dump(datas, f, allow_unicode=True)

def clean(file_path):
    with open(file_path, encoding='utf-8', mode='w') as f:
        pass

def clear_folder(folder_path):
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.remove(file_path)
        except Exception as e:
            print(f"Failed to delete {file_path}, Reason: {e}")


if __name__ == '__main__':
    print(read('/Users/cathy/python_project/Tesla/apiframetest/testcases/django_login.yaml'))
