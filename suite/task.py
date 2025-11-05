"""
@ Title:
@ Author: Cathy
@ Time: 2025/5/13 16:56
"""
import shutil
import subprocess
import sys
from pathlib import Path

test_path = []

python_path = sys.executable
run_path = "/Users/cathy/python_project/Tesla/apiframetest/main_by_django.py"
ini_path = "/Users/cathy/python_project/Tesla/apiframetest/pytest.ini"
case_path = "/Users/cathy/python_project/Tesla/tests"

def run_pytest(path, result_id=0, case_api_count=0):
    if case_api_count > 0:
        cmd = f"{python_path} {run_path} -c {ini_path} {case_path} ./ result_id {result_id}"
    else:
        cmd = f"{python_path} {run_path} -c {ini_path} ./ result_id {result_id}"

    process = subprocess.run(
        cmd,
        cwd=path,
        sdtout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    try:
        print(process.stdout.decode("utf-8"))
        print(process.stderrt.decode("utf-8"))
    except UnicodeDecodeError:
        print(process.stdout.decode("gbk"))
        print(process.stderrt.decode("gbk"))

    # 打包
    shutil.make_archive(f'artifacts_{result_id}.zip', 'zip', path)
    shutil.move(f'artifacts_{result_id}.zip', Path(path) / 'artifacts.zip')

def run_by_cron(suite_id):
    from .models import Suite
    suite = Suite.objects.get(id=suite_id)
    return suite.run()

def _test_task():
    from .models import Suite
    c = Suite.objects.all().count()
    print("测试套件的数量=", c)
    return c