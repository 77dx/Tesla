"""
自测脚本：验证新版执行引擎 (case_api.engine + suite.runner)

使用方式（在项目根目录执行）：
    python tests/test_new_engine.py

测试内容：
    1. ContextStore 读写
    2. VarResolver 占位符替换
    3. CaseRunner 单条用例执行
    4. SuiteRunner 套件顺序执行
"""
import os
import sys
import django

# 设置 Django 环境
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Tesla.settings')
django.setup()

import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger('test_engine')


def test_context_store():
    """测试 ContextStore 内存后端"""
    from case_api.engine import ContextStore
    logger.info('=== 测试 ContextStore ===')
    ctx = ContextStore(backend='memory')
    ctx.set('token', 'abc123')
    ctx.set('userId', '42')
    assert ctx.get('token') == 'abc123', 'get token 失败'
    assert ctx.get('userId') == '42', 'get userId 失败'
    all_vars = ctx.get_all()
    assert 'token' in all_vars, 'get_all 缺少 token'
    ctx.clear()
    assert ctx.get('token') is None, 'clear 未生效'
    logger.info('ContextStore ✓')


def test_var_resolver():
    """测试 VarResolver 占位符替换"""
    from case_api.engine import ContextStore, VarResolver
    logger.info('=== 测试 VarResolver ===')
    ctx = ContextStore(backend='memory')
    ctx.set('token', 'mytoken123')
    ctx.set('userId', '99')
    resolver = VarResolver(ctx)

    # 简单变量替换
    result = resolver.resolve('Bearer ${token}')
    assert result == 'Bearer mytoken123', f'变量替换失败: {result}'

    # dict 替换
    result = resolver.resolve({'Authorization': 'Bearer ${token}', 'X-User': '${userId}'})
    assert result['Authorization'] == 'Bearer mytoken123', f'dict 替换失败: {result}'
    assert result['X-User'] == '99', f'dict userId 替换失败: {result}'

    # 内置函数
    result = resolver.resolve('ts=${timestamp()}')
    assert 'ts=' in result and '${timestamp()}' not in result, f'timestamp 替换失败: {result}'

    # 未找到变量，保留原文
    result = resolver.resolve('${notExist}')
    assert result == '${notExist}', f'未知变量应保留原文: {result}'

    logger.info('VarResolver ✓')


def test_case_runner():
    """测试 CaseRunner 执行真实用例（需要数据库有用例数据）"""
    from case_api.engine import ContextStore, CaseRunner
    from case_api.models import Case

    logger.info('=== 测试 CaseRunner ===')

    cases = Case.objects.select_related('endpoint').order_by('id')[:5]
    if not cases:
        logger.warning('数据库中没有用例，跳过 CaseRunner 测试')
        return

    ctx = ContextStore(backend='memory')
    runner = CaseRunner(ctx=ctx)

    for case in cases:
        logger.info(f'执行用例 #{case.id} [{case.name}] 接口: {case.endpoint.name}')
        result = runner.run_case(case.id)
        logger.info(f'  状态码: {result.status_code}  成功: {result.success}  耗时: {result.duration:.2f}s')
        if result.extracted:
            logger.info(f'  提取变量: {result.extracted}')
        if result.error:
            logger.warning(f'  错误: {result.error}')

    logger.info('CaseRunner ✓')


def test_suite_runner():
    """测试 SuiteRunner 执行套件（需要数据库有套件数据）"""
    from suite.models import Suite, RunResult
    from suite.runner import SuiteRunner
    from pathlib import Path
    import time

    logger.info('=== 测试 SuiteRunner ===')

    suite = Suite.objects.first()
    if not suite:
        logger.warning('数据库中没有套件，跳过 SuiteRunner 测试')
        return

    logger.info(f'测试套件: {suite.name} (id={suite.id})')

    # 创建 RunResult 记录
    result = RunResult.objects.create(
        suite=suite,
        project=suite.project,
        path='todo'
    )
    base_dir = Path('upload_yaml') / f'test_engine_{result.id}_{int(time.time())}'
    base_dir.mkdir(parents=True, exist_ok=True)
    result.path = str(base_dir)
    result.save()

    log_file = base_dir / 'log' / 'pytest.log'

    # 获取套件内用例
    case_ids = list(
        suite.get_case_api_items().values_list('case_api_id', flat=True)
    )
    logger.info(f'套件用例: {case_ids}')

    if not case_ids:
        logger.warning('套件内没有启用的 API 用例，跳过')
        result.delete()
        return

    runner = SuiteRunner(result_id=result.id, log_file=log_file)
    suite_result = runner.run(case_api_ids=case_ids)

    logger.info(f'套件结果: 总计={suite_result.total} 通过={suite_result.passed} 失败={suite_result.failed}')
    logger.info(f'is_pass={suite_result.is_pass}  耗时={suite_result.duration:.2f}s')

    if log_file.exists():
        logger.info(f'日志文件: {log_file} ({log_file.stat().st_size} bytes)')

    # 验证数据库状态已更新
    result.refresh_from_db()
    assert result.status == RunResult.RunStatus.Done, f'状态应为 Done，实际: {result.status}'
    logger.info('SuiteRunner ✓')


if __name__ == '__main__':
    print('\n' + '='*60)
    print('新版执行引擎自测')
    print('='*60 + '\n')

    tests = [
        ('ContextStore', test_context_store),
        ('VarResolver',  test_var_resolver),
        ('CaseRunner',   test_case_runner),
        ('SuiteRunner',  test_suite_runner),
    ]

    passed = 0
    failed = 0
    for name, fn in tests:
        try:
            fn()
            passed += 1
            print(f'  ✓ {name}')
        except Exception as e:
            failed += 1
            print(f'  ✗ {name}: {e}')
            import traceback
            traceback.print_exc()

    print(f'\n结果: {passed} 通过 / {failed} 失败')
    sys.exit(0 if failed == 0 else 1)
