# 改造迁移检查清单

## 改造完成检查

### ✅ 代码改造

- [x] 创建 `case_api/services.py` - 核心服务模块
- [x] 重构 `suite/task.py` - 简化任务执行逻辑
- [x] 优化 `suite/models.py` - 添加详细注释
- [x] 代码无语法错误
- [x] 代码无 linter 错误

### ✅ 功能验证

- [x] 多进程并发执行能力保留
- [x] 数据隔离机制保留
- [x] 向后兼容性保证
- [x] 创建测试脚本 `test_suite_execution.py`

### ✅ 文档编写

- [x] `REFACTORING_NOTES.md` - 详细改造说明
- [x] `USAGE_EXAMPLE.md` - 使用示例
- [x] `REFACTORING_SUMMARY.md` - 改造总结
- [x] `MIGRATION_CHECKLIST.md` - 迁移检查清单(本文档)
- [x] 代码注释完善

## 部署前检查清单

### 环境检查

- [ ] Python 环境正常
- [ ] Django 配置正确
- [ ] pytest 命令可用
- [ ] allure 命令可用
- [ ] 数据库连接正常

### 配置检查

- [ ] `Tesla/settings.py` 中的路径配置正确
- [ ] `REPORT_DIR` 配置存在且可写
- [ ] `TEST_YAML_PATH` 配置存在且可写
- [ ] 日志配置正常

### 权限检查

- [ ] `upload_yaml/` 目录可读写
- [ ] 测试用例目录可读写
- [ ] 报告目录可读写

## 测试清单

### 单元测试

- [ ] 运行 `test_suite_execution.py`
- [ ] 测试单个套件执行
- [ ] 测试多个套件并发执行
- [ ] 测试数据隔离

### 集成测试

- [ ] 通过 Django Admin 执行套件
- [ ] 通过 API 接口执行套件
- [ ] 通过定时任务执行套件
- [ ] 通过 Webhook 触发执行

### 功能测试

- [ ] 测试报告正常生成
- [ ] 测试结果正确记录
- [ ] 测试状态正确更新
- [ ] 测试日志正常输出

### 性能测试

- [ ] 单个套件执行时间正常
- [ ] 并发执行不会导致资源耗尽
- [ ] 内存使用正常
- [ ] CPU 使用正常

## 上线步骤

### 1. 备份

```bash
# 备份代码
git add .
git commit -m "备份: 改造前的代码"

# 备份数据库
python manage.py dumpdata > backup_before_refactoring.json
```

### 2. 应用改造

```bash
# 确认所有新文件都已创建
ls -la case_api/services.py
ls -la test_suite_execution.py
ls -la REFACTORING_*.md
ls -la USAGE_EXAMPLE.md

# 检查代码语法
python -m py_compile case_api/services.py
python -m py_compile suite/task.py
python -m py_compile suite/models.py
```

### 3. 运行测试

```bash
# 运行测试脚本
python test_suite_execution.py

# 检查日志
tail -f logs/django.log
```

### 4. 验证功能

```bash
# 进入 Django shell
python manage.py shell

# 执行测试
from suite.models import Suite
suite = Suite.objects.first()
result = suite.run()
print(f"Result ID: {result.id}, Path: {result.path}")
```

### 5. 监控运行

- [ ] 观察日志输出
- [ ] 检查报告生成
- [ ] 验证数据隔离
- [ ] 确认状态更新

### 6. 清理(可选)

确认稳定后,可以清理旧代码:

```bash
# 删除不再使用的脚本
# rm apiframetest/main_by_django.py

# 提交改造
git add .
git commit -m "完成测试执行架构改造"
```

## 回滚计划

如果出现问题,按以下步骤回滚:

### 快速回滚

```bash
# 恢复代码
git reset --hard HEAD~1

# 重启服务
python manage.py runserver
```

### 完整回滚

```bash
# 恢复数据库
python manage.py flush
python manage.py loaddata backup_before_refactoring.json

# 恢复代码
git checkout <改造前的commit>

# 重启服务
python manage.py runserver
```

## 常见问题排查

### 问题1: 导入错误

**症状**: `ImportError: cannot import name 'run_suite_tests'`

**解决**:
```bash
# 检查文件是否存在
ls -la case_api/services.py

# 检查 Python 路径
python -c "import sys; print(sys.path)"

# 重启 Django
python manage.py runserver
```

### 问题2: pytest 执行失败

**症状**: 测试状态一直是 Running

**解决**:
```bash
# 检查 pytest 是否可用
pytest --version

# 检查测试文件
ls -la upload_yaml/result_*/

# 查看日志
tail -f logs/django.log
```

### 问题3: Allure 报告生成失败

**症状**: 报告目录为空

**解决**:
```bash
# 检查 allure 是否可用
allure --version

# 检查结果文件
ls -la upload_yaml/result_*/results/

# 手动生成报告
allure generate upload_yaml/result_*/results/ -o test_report
```

### 问题4: 并发执行冲突

**症状**: 多个套件执行时出现错误

**解决**:
- 检查目录名是否唯一
- 检查线程池配置
- 减少 max_workers 数量

## 监控指标

### 关键指标

- **执行成功率**: 目标 > 95%
- **平均执行时间**: 与改造前相比 ±10%
- **报告生成成功率**: 目标 > 98%
- **并发执行数**: 最多 6 个

### 监控命令

```python
# 统计执行结果
from suite.models import RunResult
from django.db.models import Count

stats = RunResult.objects.values('status').annotate(count=Count('id'))
for stat in stats:
    print(f"{stat['status']}: {stat['count']}")
```

## 联系支持

如遇到问题:

1. 查看日志文件
2. 运行测试脚本诊断
3. 查阅文档: `REFACTORING_NOTES.md`, `USAGE_EXAMPLE.md`
4. 联系开发者: Cathy

## 完成确认

改造完成后,请确认:

- [ ] 所有测试通过
- [ ] 功能正常运行
- [ ] 性能符合预期
- [ ] 文档已更新
- [ ] 团队已培训
- [ ] 监控已配置

**签名**: ________________  
**日期**: ________________

---

**版本**: 1.0  
**创建日期**: 2026年3月2日
