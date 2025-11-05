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

logger = logging.getLogger(__name__)

result_id = sys.argv[-1]
sys.argv = sys.argv[:-2]

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Tesla.settings")
django.setup()

from django.conf import settings
sys.path.append(settings.BASE_DIR)

from suite.models import RunResult
result: RunResult = RunResult.objects.get(id=result_id)
result.status = result.RunStatus.Running
result.save()
ret_code = pytest.main()

if ret_code == pytest.ExitCode.OK:
    print("测试通过")
    result.is_pass = True
    result.save()
else:
    print("测试不通过")

result.status = result.RunStatus.Reporting
result.save()
ret_code = os.system("allure generate -o report temps --clean")

if ret_code == pytest.ExitCode.OK:
    print("报告生成成功")
    result.status = result.RunStatus.Done
    result.save()
else:
    print("报告生成失败")
    result.status = result.RunStatus.Error
    result.save()

result: RunResult = RunResult.objects.get(id=result_id)
print(result_id, result.is_pass, result.status)