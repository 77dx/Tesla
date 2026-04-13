"""
压测执行引擎（基于 PerformanceResult）
"""
import csv
import json
import logging
import os
import signal
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

import requests

logger = logging.getLogger(__name__)

LOCUST_WEB_PORT = 8089


def run_perf_result(result_id: int) -> None:
    """
    完整执行流程：
    1. 生成 locustfile
    2. 启动 Locust 进程
    3. 等待完成
    4. 从 CSV 解析历史数据
    5. 汇总并写入 PerformanceResult
    """
    from suite.perf_models import PerformanceResult
    from suite.locust_generator import LocustScriptGenerator
    from django.conf import settings as django_settings

    try:
        result = PerformanceResult.objects.select_related('config', 'config__suite').get(id=result_id)
    except PerformanceResult.DoesNotExist:
        logger.error(f'[PerfEngine] PerformanceResult {result_id} 不存在')
        return

    cfg = result.config

    try:
        # 1. 创建工作目录
        base = Path(getattr(django_settings, 'SUITE_EXECUTION_BASE_DIR',
                            Path(os.path.dirname(os.path.abspath(__file__))).parent / 'upload_yaml'))
        work_dir = base / f'perf_{result_id}_{int(time.time())}'
        work_dir.mkdir(parents=True, exist_ok=True)

        # 2. 生成 locustfile
        gen = LocustScriptGenerator(
            suite_id=cfg.suite_id,
            case_ids=cfg.case_ids or None,
            host=result.host or '',
        )
        locust_file = gen.write_to_file(str(work_dir))

        # 3. 构建命令
        cmd = [
            'locust',
            '-f', locust_file,
            '--headless',
            '--users', str(result.users),
            '--spawn-rate', str(result.spawn_rate),
            '--run-time', f'{result.run_time}s',
            '--web-port', str(LOCUST_WEB_PORT),
            '--csv', str(work_dir / 'stats'),
            '--html', str(work_dir / 'report.html'),
            '--logfile', str(work_dir / 'locust.log'),
            '--loglevel', 'INFO',
        ]
        if result.host:
            cmd.extend(['--host', result.host])

        log_file = open(work_dir / 'locust.log', 'w')
        logger.info(f'[PerfEngine] 启动命令: {" ".join(cmd)}')

        # 4. 启动进程
        proc = subprocess.Popen(cmd, stdout=log_file, stderr=subprocess.STDOUT, cwd=str(work_dir))

        PerformanceResult.objects.filter(id=result_id).update(
            status=PerformanceResult.Status.RUNNING,
            pid=proc.pid,
            work_dir=str(work_dir),
            started_at=datetime.now(),
        )
        logger.info(f'[PerfEngine] 进程已启动 pid={proc.pid} work_dir={work_dir}')

        # 5. 等待并轮询
        time.sleep(3)
        poll_interval = 5
        elapsed = 0
        stats_data = []

        while elapsed < result.run_time:
            result.refresh_from_db()
            if result.status == PerformanceResult.Status.STOPPED:
                logger.info(f'[PerfEngine] 被手动停止 id={result_id}')
                return

            stats = _poll_stats()
            if stats:
                point = {
                    'ts':       int(time.time()),
                    'elapsed':  elapsed,
                    'rps':      stats.get('total', {}).get('current_rps', 0),
                    'avg_rt':   stats.get('total', {}).get('avg_response_time', 0),
                    'failures': stats.get('total', {}).get('num_failures', 0),
                    'requests': stats.get('total', {}).get('num_requests', 0),
                    'users':    stats.get('user_count', 0),
                }
                stats_data.append(point)
                PerformanceResult.objects.filter(id=result_id).update(stats_data=stats_data)

            time.sleep(poll_interval)
            elapsed += poll_interval

        # 6. 从 CSV 解析历史数据
        history = _read_history(str(work_dir))
        if history:
            stats_data = history

        summary = _read_summary(str(work_dir))

        PerformanceResult.objects.filter(id=result_id).update(
            status=PerformanceResult.Status.DONE,
            finished_at=datetime.now(),
            summary=summary,
            stats_data=stats_data,
        )
        logger.info(f'[PerfEngine] 完成 id={result_id}')

    except Exception as e:
        logger.exception(f'[PerfEngine] 执行异常: {e}')
        PerformanceResult.objects.filter(id=result_id).update(
            status=PerformanceResult.Status.ERROR,
            error_msg=str(e),
            finished_at=datetime.now(),
        )


def stop_perf_result(result_id: int) -> None:
    from suite.perf_models import PerformanceResult
    result = PerformanceResult.objects.get(id=result_id)
    if result.pid:
        try:
            os.kill(result.pid, signal.SIGTERM)
            logger.info(f'[PerfEngine] 已发送 SIGTERM 给 pid={result.pid}')
        except ProcessLookupError:
            pass
    PerformanceResult.objects.filter(id=result_id).update(
        status=PerformanceResult.Status.STOPPED,
        finished_at=datetime.now(),
    )


def _poll_stats() -> Optional[dict]:
    try:
        resp = requests.get(f'http://127.0.0.1:{LOCUST_WEB_PORT}/stats/requests', timeout=3)
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        pass
    return None


def _read_history(work_dir: str) -> list:
    try:
        history_file = Path(work_dir) / 'stats_stats_history.csv'
        if not history_file.exists():
            return []
        with open(history_file, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = [r for r in reader if r.get('Name') == 'Aggregated']
        if not rows:
            return []
        start_ts = int(rows[0]['Timestamp'])
        result = []
        for row in rows:
            try:
                result.append({
                    'ts':       int(row['Timestamp']),
                    'elapsed':  int(row['Timestamp']) - start_ts,
                    'rps':      round(float(row.get('Requests/s', 0) or 0), 2),
                    'avg_rt':   round(float(row.get('Total Average Response Time', 0) or 0), 1),
                    'failures': int(row.get('Total Failure Count', 0) or 0),
                    'requests': int(row.get('Total Request Count', 0) or 0),
                    'users':    int(row.get('User Count', 0) or 0),
                })
            except (ValueError, TypeError):
                continue
        return result
    except Exception as e:
        logger.warning(f'[PerfEngine] 读取 history CSV 失败: {e}')
    return []


def _read_summary(work_dir: str) -> dict:
    try:
        stats_file = Path(work_dir) / 'stats_stats.csv'
        if not stats_file.exists():
            return {}
        with open(stats_file, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        for row in rows:
            if row.get('Name') == 'Aggregated':
                return {
                    'total_requests':  int(row.get('Request Count', 0)),
                    'failure_count':   int(row.get('Failure Count', 0)),
                    'failure_rate':    round(int(row.get('Failure Count', 0)) /
                                            max(int(row.get('Request Count', 1)), 1), 4),
                    'avg_response_ms': float(row.get('Average Response Time', 0)),
                    'min_response_ms': float(row.get('Min Response Time', 0)),
                    'max_response_ms': float(row.get('Max Response Time', 0)),
                    'p50_response_ms': float(row.get('50%', 0)),
                    'p95_response_ms': float(row.get('95%', 0)),
                    'p99_response_ms': float(row.get('99%', 0)),
                    'rps':             float(row.get('Requests/s', 0)),
                }
    except Exception as e:
        logger.warning(f'[PerfEngine] 读取 summary CSV 失败: {e}')
    return {}
