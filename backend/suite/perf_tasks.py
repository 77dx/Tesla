"""
压测执行任务（基于 PerformanceResult）
"""
import logging
from celery import shared_task

logger = logging.getLogger(__name__)


def start_perf_result_task(result_id: int) -> str:
    async_result = run_perf_result_task.delay(result_id)
    logger.info(f'[PerfTask] 已提交任务 task_id={async_result.id} result_id={result_id}')
    return async_result.id


@shared_task(bind=True)
def run_perf_result_task(self, result_id: int) -> None:
    from suite.perf_engine import run_perf_result
    run_perf_result(result_id)

