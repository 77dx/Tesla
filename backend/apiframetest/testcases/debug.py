"""
@ Title:
@ Author: Cathy
@ Time: 2025/9/18 15:02
"""
import os
from pathlib import Path

# testcases = Path(__file__).parent
# yaml_list = testcases.glob("**/*.yaml")
# for yaml_file in yaml_list:
#     method_name = f'test_{yaml_file.stem}_{hash(yaml_file)}'
#     print(method_name)


# def setup(file_path):
#     if os.path.exists(file_path):
#         os.remove(file_path)
#         print(f"文件 {file_path} 已删除")
#     else:
#         print(f"文件 {file_path} 不存在")
# setup('../extract.yaml')

testcases = Path(__file__).parent
yaml_list = testcases.glob("**/*.yaml")
print(f"收集到的测试用例列表：{list(yaml_list)}")





















