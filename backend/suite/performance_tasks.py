"""
性能测试 Celery 任务
"""
import logging
from celery import shared_task

logger = logging.getLogger(__name__)


def start_performance_test_task(perf_test_id: int) -> str:
    """异步启动性能测试任务，返回 task id。"""
    async_result = run_performance_test_task.delay(perf_test_id)
    logger.info(f'[PerfTask] 已提交异步任务 task_id={async_result.id} perf_test_id={perf_test_id}')
    return async_result.id


@shared_task(bind=True)
def run_performance_test_task(self, perf_test_id: int) -> None:
    """实际执行函数。"""
    from suite.locust_engine import run_performance_test
    run_performance_test(perf_test_id)

