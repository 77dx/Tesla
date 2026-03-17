# 测试套件执行架构改造说明

## 改造日期
2026年3月2日

## 改造目标
将测试执行逻辑从独立的 `apiframetest/main_by_django.py` 脚本迁移到 `case_api` 模块中,实现更清晰的架构和更好的代码复用。

## 改造前架构

```
Suite.run() 
  ↓
suite/task.py (run_pytest)
  ↓
subprocess 调用 apiframetest/main_by_django.py
  ↓
独立进程中启动 Django, 执行 pytest
```

### 问题
1. 需要通过 subprocess 调用独立脚本,增加了复杂度
2. 硬编码了路径 (`/Users/cathy/python_project/Tesla/...`)
3. 代码重复: `apiframetest/main_by_django.py` 和 `case_api/views.py` 有相似逻辑
4. 难以维护和测试

## 改造后架构

```
Suite.run()
  ↓
suite/task.py (run_pytest)
  ↓
case_api/services.py (TestExecutionService)
  ↓
直接调用 pytest.main() 和 allure 命令
```

### 优势
1. ✅ 代码复用: 统一使用 `case_api/services.py` 中的服务
2. ✅ 简化流程: 不再需要 subprocess 调用独立脚本
3. ✅ 更好的错误处理和日志记录
4. ✅ 易于测试和维护
5. ✅ 保持多进程并发能力
6. ✅ 保证数据隔离

## 主要变更

### 1. 新增文件: `case_api/services.py`

核心服务类 `TestExecutionService`:
- 负责执行测试用例
- 生成 Allure 报告
- 更新 RunResult 状态

便捷函数 `run_suite_tests()`:
- 用于在多进程/线程中调用
- 自动处理 Django 初始化

### 2. 重构文件: `suite/task.py`

简化 `run_pytest()` 函数:
- 移除 subprocess 调用
- 直接调用 `case_api.services.run_suite_tests()`
- 保持相同的函数签名,确保兼容性

### 3. 更新文件: `suite/models.py`

优化 `Suite.run()` 方法:
- 添加详细的文档字符串
- 优化注释,说明数据隔离机制
- 保持原有的 ThreadPoolExecutor 多线程执行

### 4. 保留文件: `apiframetest/main_by_django.py`

暂时保留,但不再使用。可以在确认新架构稳定后删除。

## 数据隔离机制

每次执行套件时:
1. 创建唯一的执行目录: `upload_yaml/result_{result_id}_{timestamp}/`
2. YAML 测试文件生成到该目录
3. pytest 结果输出到 `{目录}/results/`
4. Allure 报告生成到 `{目录}/report/`

多个套件并发执行时,各自在独立目录中运行,互不干扰。

## 多进程执行

使用 `ThreadPoolExecutor` (max_workers=6) 实现并发:
- 每个套件的 `run()` 方法立即返回 RunResult 对象
- 实际的测试执行在线程池中异步进行
- 支持同时执行多个套件

## 测试验证

运行测试脚本验证功能:

```bash
python test_suite_execution.py
```

测试内容:
1. 单个套件执行
2. 多个套件并发执行
3. 数据隔离验证

## 向后兼容性

✅ 保持了原有的 API 接口:
- `Suite.run()` 返回值不变
- `run_pytest()` 函数签名不变
- 数据库模型不变

## 迁移建议

1. ✅ 新架构已经实现并可以直接使用
2. ⚠️  建议先在测试环境验证
3. ✅ 确认稳定后,可以删除 `apiframetest/main_by_django.py`
4. ✅ 可以考虑将 `case_api/views.py` 中的 `run_pytest` 视图函数也重构为使用 `services.py`

## 后续优化建议

1. **统一 case_api/views.py**: 将视图函数中的测试执行逻辑也改为调用 `services.py`
2. **配置化路径**: 将硬编码的路径改为配置项
3. **增强监控**: 添加测试执行的实时监控和进度反馈
4. **结果通知**: 测试完成后发送邮件或消息通知
5. **历史报告管理**: 自动清理过期的测试报告

## 注意事项

1. 确保 Django 环境已正确配置
2. 确保 pytest 和 allure 命令可用
3. 确保有足够的磁盘空间存储测试结果和报告
4. 注意线程池的 max_workers 设置,避免资源耗尽

## 联系人

如有问题,请联系: Cathy
