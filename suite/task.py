"""
@ Title: 测试套件执行任务
@ Author: Cathy
@ Time: 2025/5/13 16:56
@ Updated: 2026/3/2 - 重构为直接调用 case_api 服务

本模块提供测试套件执行的任务函数,用于在后台线程/进程中执行测试。

主要功能:
- 接收测试路径和执行参数
- 调用 case_api.services 中的核心服务
- 记录执行日志
- 处理异常情况

设计特点:
- 线程安全: 可以在多线程环境中并发调用
- 错误隔离: 异常不会影响其他并发任务
- 日志完善: 详细记录执行过程,便于问题排查

使用场景:
1. ThreadPoolExecutor 中提交任务
2. Django-Q 异步任务队列
3. Celery 分布式任务
4. 定时任务调度

改造历史:
- v1.0 (2025-05-13): 初始版本,使用 subprocess 调用独立脚本
- v2.0 (2026-03-02): 重构为直接调用服务函数,简化架构
"""
import logging
import time
from pathlib import Path
import warnings

# 忽略特定的警告信息,避免日志污染
# django_q.conf 模块会产生一些无关紧要的 UserWarning
warnings.filterwarnings("ignore", category=UserWarning, module="django_q.conf")

# 获取日志记录器
logger = logging.getLogger(__name__)


def run_pytest(path, result_id=0, case_api_count=0):
    """
    执行测试套件的任务函数
    
    这是一个包装函数,用于在后台线程/进程中执行测试套件。
    它会调用 case_api.services.run_suite_tests() 完成实际的测试执行。
    
    工作流程:
    1. 验证并创建测试路径
    2. 调用 case_api 服务执行测试
    3. 记录执行结果
    4. 处理异常情况
    
    Args:
        path (str|Path): 测试用例和报告的基础路径
            - 测试用例文件(.yaml)应该已经生成在这个目录中
            - 测试结果会输出到 {path}/results/
            - 测试报告会生成到 {path}/report/
            
        result_id (int): RunResult 模型的主键 ID
            - 用于关联数据库中的执行记录
            - 服务函数会根据此 ID 更新执行状态
            - 默认值 0 仅用于兼容性,实际使用时必须传入有效 ID
            
        case_api_count (int): API 用例数量(已废弃)
            - 保留此参数仅为了向后兼容
            - 新架构中不再使用此参数
            - 可以传入任意值,不影响执行
    
    Returns:
        None - 此函数没有返回值
        执行结果会通过 RunResult 模型记录到数据库中
    
    异常处理:
        所有异常都会被捕获并记录到日志,不会向外抛出
        这确保了一个任务的失败不会影响其他并发任务
    
    日志记录:
        - INFO: 正常的执行流程信息
        - ERROR: 执行失败或异常信息
        - 所有日志都包含 result_id,便于追踪特定执行
    
    示例:
        # 在线程池中使用
        from concurrent.futures import ThreadPoolExecutor
        
        pool = ThreadPoolExecutor(max_workers=6)
        pool.submit(
            run_pytest,
            path='/path/to/test',
            result_id=123,
            case_api_count=0  # 不再使用,可以传0
        )
        
        # 在 Django-Q 中使用
        from django_q.tasks import async_task
        
        async_task(
            'suite.task.run_pytest',
            path='/path/to/test',
            result_id=123
        )
    
    注意:
    - 此函数设计为在后台线程/进程中调用
    - 不要在主线程中直接调用并等待结果,这会阻塞主线程
    - 如果需要同步执行,请直接使用 case_api.services.run_suite_tests()
    """
    # ========== 记录开始执行 ==========
    logger.info(f"=" * 60)
    logger.info(f"开始执行测试套件任务")
    logger.info(f"  - Result ID: {result_id}")
    logger.info(f"  - 测试路径: {path}")
    logger.info(f"  - 时间戳: {time.time()}")
    logger.info(f"=" * 60)
    
    # ========== 验证并创建路径 ==========
    path_obj = Path(path)
    
    # 确保目录存在
    # parents=True: 创建所有必要的父目录
    # exist_ok=True: 如果目录已存在,不抛出异常
    path_obj.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"测试路径验证通过: {path_obj.absolute()}")
    
    # 检查目录中是否有测试文件
    yaml_files = list(path_obj.glob("*.yaml")) + list(path_obj.glob("*.yml"))
    if yaml_files:
        logger.info(f"找到 {len(yaml_files)} 个测试文件")
    else:
        logger.warning(f"警告: 目录中没有找到测试文件")
    
    try:
        # ========== 调用核心服务执行测试 ==========
        # 延迟导入,避免循环依赖
        from case_api.services import run_suite_tests
        
        logger.info(f"调用测试执行服务...")
        
        # 调用服务函数
        # 这是一个同步调用,会阻塞直到测试完成
        result = run_suite_tests(
            result_id=result_id,
            yaml_files_dir=str(path_obj),  # YAML 文件所在目录
            report_base_dir=str(path_obj)  # 报告输出目录
        )
        
        # ========== 检查执行结果 ==========
        if result.get("success"):
            # 执行成功
            is_pass = result.get('is_pass', False)
            logger.info(f"=" * 60)
            logger.info(f"测试执行成功")
            logger.info(f"  - Result ID: {result_id}")
            logger.info(f"  - 测试通过: {is_pass}")
            logger.info(f"  - 返回码: {result.get('returncode', 'N/A')}")
            logger.info(f"  - 报告路径: {result.get('report_path', 'N/A')}")
            logger.info(f"=" * 60)
        else:
            # 执行失败
            error = result.get('error', '未知错误')
            logger.error(f"=" * 60)
            logger.error(f"测试执行失败")
            logger.error(f"  - Result ID: {result_id}")
            logger.error(f"  - 错误信息: {error}")
            logger.error(f"=" * 60)
            
    except ImportError as e:
        # 导入错误,通常是模块不存在或路径问题
        logger.error(f"=" * 60)
        logger.error(f"导入测试服务失败")
        logger.error(f"  - Result ID: {result_id}")
        logger.error(f"  - 错误: {str(e)}")
        logger.error(f"  - 提示: 检查 case_api.services 模块是否存在")
        logger.error(f"=" * 60, exc_info=True)
        
    except Exception as e:
        # 其他异常
        logger.error(f"=" * 60)
        logger.error(f"执行测试时发生异常")
        logger.error(f"  - Result ID: {result_id}")
        logger.error(f"  - 异常类型: {type(e).__name__}")
        logger.error(f"  - 异常信息: {str(e)}")
        logger.error(f"=" * 60, exc_info=True)

def run_by_cron(suite_id):
    """
    定时任务执行函数
    
    这个函数专门用于定时任务调度系统(如 Django-Q, Celery)调用。
    当测试套件配置为 CRON 模式时,调度系统会定期调用此函数。
    
    工作流程:
    1. 根据 suite_id 获取测试套件对象
    2. 调用套件的 run() 方法执行测试
    3. 返回执行结果对象
    
    Args:
        suite_id (int): Suite 模型的主键 ID
            用于查找需要执行的测试套件
    
    Returns:
        RunResult: 执行结果对象
            包含执行状态、测试结果、报告路径等信息
    
    异常:
        Suite.DoesNotExist: 如果指定的套件不存在
        其他异常会向上传播,由调度系统处理
    
    使用示例:
        # 在 Django-Q 中配置定时任务
        from django_q.models import Schedule
        from django_q.tasks import schedule
        
        # 创建定时任务,每天凌晨2点执行
        schedule(
            'suite.task.run_by_cron',
            1,  # suite_id
            cron='0 2 * * *',
            schedule_type='C'
        )
        
        # 在 Celery 中配置定时任务
        from celery import shared_task
        from celery.schedules import crontab
        
        @shared_task
        def scheduled_test():
            return run_by_cron(suite_id=1)
        
        # 在 celerybeat 配置中
        CELERY_BEAT_SCHEDULE = {
            'run-test-suite': {
                'task': 'suite.task.scheduled_test',
                'schedule': crontab(hour=2, minute=0),
            },
        }
    
    注意:
    - 此函数会被调度系统在后台进程中调用
    - 确保 suite_id 对应的套件存在且配置正确
    - 执行结果会记录到数据库,可以通过 RunResult 查询
    - 如果套件执行失败,不会抛出异常,而是在 RunResult 中标记状态
    """
    from .models import Suite
    
    # 获取测试套件
    suite = Suite.objects.get(id=suite_id)
    
    # 执行测试套件
    # run() 方法会异步执行测试,立即返回 RunResult 对象
    return suite.run()


def _test_task():
    """
    测试任务函数(仅用于开发和调试)
    
    这是一个简单的测试函数,用于验证任务队列系统是否正常工作。
    不应该在生产环境中使用。
    
    功能:
    - 查询数据库中测试套件的数量
    - 打印到控制台
    - 返回数量值
    
    Returns:
        int: 数据库中测试套件的总数
    
    使用示例:
        # 在 Django shell 中测试
        from suite.task import _test_task
        count = _test_task()
        print(f"找到 {count} 个测试套件")
        
        # 在 Django-Q 中测试任务队列
        from django_q.tasks import async_task
        result_id = async_task('suite.task._test_task')
        
        # 查看任务结果
        from django_q.models import Task
        task = Task.objects.get(id=result_id)
        print(f"任务状态: {task.success}")
        print(f"任务结果: {task.result}")
    
    注意:
    - 函数名以下划线开头,表示这是内部/私有函数
    - 仅用于开发和测试,不要在生产代码中调用
    - 使用 print() 而不是 logger,因为这是测试函数
    """
    from .models import Suite
    
    # 查询测试套件数量
    c = Suite.objects.all().count()
    
    # 打印结果(测试用)
    print("测试套件的数量=", c)
    
    # 返回数量
    return c