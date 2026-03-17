"""
测试套件执行功能的测试脚本

用于验证:
1. 多套件并发执行
2. 数据隔离
3. 报告生成
"""
import os
import sys
import django
import time
from pathlib import Path

# 设置 Django 环境
sys.path.append('/')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Tesla.settings")
django.setup()

from suite.models import Suite, RunResult


def test_single_suite():
    """测试单个套件执行"""
    print("\n" + "="*50)
    print("测试 1: 单个套件执行")
    print("="*50)
    
    suites = Suite.objects.all()[:1]
    if not suites:
        print("❌ 没有找到测试套件")
        return
    
    suite = suites[0]
    print(f"✓ 执行套件: {suite.name} (ID: {suite.id})")
    
    result = suite.run()
    print(f"✓ 创建执行结果: ID={result.id}, 路径={result.path}")
    
    # 等待一段时间让测试执行
    print("⏳ 等待测试执行...")
    time.sleep(5)
    
    # 检查结果
    result.refresh_from_db()
    print(f"✓ 执行状态: {result.get_status_display()}")
    print(f"✓ 测试通过: {result.is_pass}")
    
    # 检查目录结构
    path = Path(result.path)
    print(f"\n目录结构:")
    print(f"  - 基础路径: {path} (存在: {path.exists()})")
    print(f"  - 结果目录: {path / 'results'} (存在: {(path / 'results').exists()})")
    print(f"  - 报告目录: {path / 'report'} (存在: {(path / 'report').exists()})")


def test_multiple_suites():
    """测试多个套件并发执行"""
    print("\n" + "="*50)
    print("测试 2: 多个套件并发执行")
    print("="*50)
    
    suites = Suite.objects.all()[:3]
    if len(suites) < 2:
        print("⚠️  套件数量不足,跳过并发测试")
        return
    
    results = []
    for suite in suites:
        print(f"✓ 提交套件: {suite.name} (ID: {suite.id})")
        result = suite.run()
        results.append(result)
        print(f"  - 执行结果 ID: {result.id}, 路径: {result.path}")
    
    print(f"\n✓ 已提交 {len(results)} 个套件到线程池")
    
    # 等待执行
    print("⏳ 等待所有测试执行...")
    time.sleep(10)
    
    # 检查所有结果
    print("\n执行结果汇总:")
    for result in results:
        result.refresh_from_db()
        path = Path(result.path)
        print(f"\n套件 {result.suite.name}:")
        print(f"  - 状态: {result.get_status_display()}")
        print(f"  - 通过: {result.is_pass}")
        print(f"  - 路径: {result.path}")
        print(f"  - 目录存在: {path.exists()}")
        print(f"  - 结果文件: {len(list((path / 'results').glob('*'))) if (path / 'results').exists() else 0}")


def test_data_isolation():
    """测试数据隔离"""
    print("\n" + "="*50)
    print("测试 3: 数据隔离验证")
    print("="*50)
    
    # 获取最近的几个执行结果
    recent_results = RunResult.objects.all().order_by('-id')[:5]
    
    if len(recent_results) < 2:
        print("⚠️  执行结果不足,跳过数据隔离测试")
        return
    
    paths = [Path(r.path) for r in recent_results]
    
    print(f"检查最近 {len(paths)} 个执行结果的路径:")
    for i, path in enumerate(paths, 1):
        print(f"\n路径 {i}: {path}")
        print(f"  - 存在: {path.exists()}")
        if path.exists():
            yaml_files = list(path.glob("*.yaml"))
            result_files = list((path / "results").glob("*")) if (path / "results").exists() else []
            print(f"  - YAML 文件: {len(yaml_files)}")
            print(f"  - 结果文件: {len(result_files)}")
    
    # 检查路径是否唯一
    path_strs = [str(p) for p in paths]
    unique_paths = set(path_strs)
    
    if len(unique_paths) == len(path_strs):
        print(f"\n✅ 数据隔离验证通过: 所有路径都是唯一的")
    else:
        print(f"\n❌ 数据隔离验证失败: 存在重复路径")


if __name__ == "__main__":
    print("\n" + "="*50)
    print("开始测试套件执行功能")
    print("="*50)
    
    try:
        test_single_suite()
        test_multiple_suites()
        test_data_isolation()
        
        print("\n" + "="*50)
        print("✅ 所有测试完成")
        print("="*50)
        
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
