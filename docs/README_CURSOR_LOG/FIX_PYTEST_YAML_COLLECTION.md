# Pytest YAML 测试文件收集问题修复

## 问题描述

在执行测试套件时,pytest 无法识别动态生成的 YAML 测试文件,导致:
- pytest 返回码为 5 (没有收集到测试)
- results 目录为空(没有生成测试结果)
- Allure 报告生成失败

错误日志:
```
collected 0 items
no tests ran in 0.01s
pytest 返回码: 5
✗ 未找到测试结果文件: /Users/cathy/python_project/Tesla/upload_yaml/result_25_1772437178/results
```

## 根本原因

1. **缺少 conftest.py**: 动态生成的测试目录中没有 `conftest.py` 文件,pytest 无法识别 YAML 文件为测试用例
2. **缺少 pytest.ini**: 没有配置文件告诉 pytest 如何收集 YAML 测试文件
3. **模块导入问题**: conftest.py 依赖 `apiframetest` 模块,但项目根目录不在 sys.path 中

## 修复方案

### 1. 在 `suite/models.py` 中添加配置文件复制逻辑

在生成测试用例后,自动复制必要的配置文件到测试目录:

```python
# ========== 步骤3.5: 复制测试配置文件到测试目录 ==========
if test_cases_generated:
    import shutil
    
    # 复制 conftest.py
    source_conftest = Path(settings.BASE_DIR) / "tests" / "conftest.py"
    target_conftest = path / "conftest.py"
    shutil.copy2(source_conftest, target_conftest)
    
    # 复制 pytest.ini
    source_pytest_ini = Path(settings.BASE_DIR) / "tests" / "pytest.ini"
    target_pytest_ini = path / "pytest.ini"
    shutil.copy2(source_pytest_ini, target_pytest_ini)
```

### 2. 在 `case_api/services.py` 中添加 sys.path 配置

在执行 pytest 前,确保项目根目录在 sys.path 中:

```python
# 确保项目根目录在 sys.path 中,以便 conftest.py 能导入项目模块
import sys
project_root = str(settings.BASE_DIR)
if project_root not in sys.path:
    sys.path.insert(0, project_root)
```

## 修复效果

修复后,pytest 能够正确识别和执行 YAML 测试文件:

```
collected 4 items

test_万师傅web端首页订单列表_1772437179.yaml::case PASSED [ 25%]
test_用户web端登录_1772437179.yaml::case_0_ddt_0 PASSED [ 50%]
test_用户web端登录_1772437179.yaml::case_0_ddt_1 PASSED [ 75%]
test_用户web端登录_1772437179.yaml::case_0_ddt_2 PASSED [100%]

4 passed in 0.85s

✓ pytest 执行完成
✓ 测试通过
✓ Allure 报告生成成功
```

## 测试验证

可以使用以下命令验证修复:

```bash
# 1. 运行测试套件
curl -X POST http://127.0.0.1:8000/api/suite/suite/1/run/

# 2. 检查执行结果
# 查看日志,确认:
# - pytest 返回码为 0 (测试通过) 或 1 (有测试失败)
# - 不再是 5 (没有收集到测试)
# - Allure 报告成功生成
```

## 相关文件

- `suite/models.py`: 添加配置文件复制逻辑
- `case_api/services.py`: 添加 sys.path 配置
- `tests/conftest.py`: YAML 测试文件收集器
- `tests/pytest.ini`: pytest 配置文件

## 注意事项

1. 确保 `tests/conftest.py` 和 `tests/pytest.ini` 文件存在
2. 如果修改了 `tests/conftest.py`,需要确保它能在动态生成的测试目录中正常工作
3. 项目根目录必须在 sys.path 中,否则 conftest.py 无法导入项目模块

## 日期

2026-03-02
