"""
@ Title:
@ Author: Cathy
@ Time: 2025/5/13 17:04
"""
import os
import sys
import pytest
import django
import logging
import warnings
from pathlib import Path
import shutil


logger = logging.getLogger(__name__)

result_id = sys.argv[-1]
sys.argv = sys.argv[:-2]

# 启动Django
sys.path.append('/Users/cathy/python_project/Tesla')  # 此处是否可以参数化？
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Tesla.settings") 
django.setup()  

# 获取RunResult对象并更新状态
from suite.models import RunResult
result: RunResult = RunResult.objects.get(id=result_id)
result.status = result.RunStatus.Running
result.save()

# 获取 apiframetest 目录路径
api_test_dir = Path('/Users/cathy/python_project/Tesla/apiframetest')
test_cases_dir = api_test_dir / 'testcases'
temp_results_dir = api_test_dir / 'results'  # 临时结果目录

logger.info(f"API测试目录: {api_test_dir}")
logger.info(f"测试用例目录: {test_cases_dir}")
logger.info(f"临时结果目录: {temp_results_dir}")

# 检查目录是否存在
if not test_cases_dir.exists():
    logger.error(f"测试用例目录不存在: {test_cases_dir}")
    result.status = result.RunStatus.Error
    result.save()
    sys.exit(1)

# 清理之前的临时结果目录
if temp_results_dir.exists():
    shutil.rmtree(temp_results_dir)
temp_results_dir.mkdir(exist_ok=True)

# 执行测试并获取返回码
# 明确指定测试目录和参数
test_args = [
    str(test_cases_dir),  # 使用绝对路径
    f"--alluredir={temp_results_dir}",  # 指定临时结果目录
    "-v",  # 详细输出
    "--tb=short"  # 简洁的 traceback
]

logger.info(f"执行 pytest 命令参数: {test_args}")

ret_code = pytest.main(test_args)

logger.info(f"pytest 返回码: {ret_code}")

if ret_code == 0:  # pytest.ExitCode.OK
    logger.info("测试通过")
    result.is_pass = True
else:
    logger.info("测试不通过")
    result.is_pass = False

result.status = result.RunStatus.Reporting
result.save()

# 将结果文件复制到正确的目录
suite_results_dir = Path(result.path) / "results"
suite_results_dir.mkdir(exist_ok=True)

# 复制所有结果文件
if temp_results_dir.exists():
    for file in temp_results_dir.iterdir():
        if file.is_file():
            shutil.copy2(file, suite_results_dir / file.name)
            logger.info(f"复制结果文件: {file.name}")

# 生成 Allure 报告
allure_cmd = f"allure generate {suite_results_dir} -o {Path(result.path) / 'report'} --clean"
logger.info(f"执行 Allure 命令: {allure_cmd}")

ret_code = os.system(allure_cmd)

if ret_code == 0:
    logger.info("报告生成成功")
    result.status = result.RunStatus.Done
else:
    logger.error("报告生成失败")
    result.status = result.RunStatus.Error

result.save()

# 输出最终结果
final_result = RunResult.objects.get(id=result_id)
logger.info(f"最终结果 - ID: {result_id}, 通过: {final_result.is_pass}, 状态: {final_result.status}")

# 清理临时目录
if temp_results_dir.exists():
    shutil.rmtree(temp_results_dir)
