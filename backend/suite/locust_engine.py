"""
Locust 性能测试执行引擎

负责：
1. 启动 Locust 无头进程（headless 模式）
2. 通过 Locust REST API 轮询实时统计数据
3. 定期把统计数据写入 PerformanceTest.stats_data
4. 测试结束后汇总结果
"""
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

# Locust Web UI 默认端口（headless 模式也会启动 REST API）
LOCUST_WEB_PORT = 8089


class LocustEngine:
    """
    Locust 进程管理器。

    使用方式：
        engine = LocustEngine(perf_test_id=42)
        engine.start()
        # ... 等待 / 轮询 ...
        engine.stop()
    """

    def __init__(self, perf_test_id: int):
        self.perf_test_id = perf_test_id
        self._proc: Optional[subprocess.Popen] = None

    def _get_test(self):
        from suite.performance_models import PerformanceTest
        return PerformanceTest.objects.get(id=self.perf_test_id)

    def _web_base(self) -> str:
        return f'http://127.0.0.1:{LOCUST_WEB_PORT}'

    def start(self) -> None:
        """生成脚本 & 启动 Locust 进程"""
        from suite.performance_models import PerformanceTest
        from suite.locust_generator import LocustScriptGenerator

        pt = self._get_test()

        # 1. 创建工作目录
        from django.conf import settings as django_settings
        base = Path(getattr(django_settings, 'SUITE_EXECUTION_BASE_DIR',
                            Path(os.path.dirname(os.path.abspath(__file__))).parent / 'upload_yaml'))
        work_dir = base / f'perf_{pt.id}_{int(time.time())}'
        work_dir.mkdir(parents=True, exist_ok=True)

        # 2. 生成 locustfile.py
        gen = LocustScriptGenerator(
            suite_id=pt.suite_id,
            case_ids=pt.case_ids or None,
            host=pt.host or '',
        )
        locust_file = gen.write_to_file(str(work_dir))

        # 3. 构建 Locust 命令
        cmd = [
            'locust',
            '-f', locust_file,
            '--headless',
            '--users', str(pt.users),
            '--spawn-rate', str(pt.spawn_rate),
            '--run-time', f'{pt.run_time}s',
            '--web-port', str(LOCUST_WEB_PORT),
            '--csv', str(work_dir / 'stats'),
            '--html', str(work_dir / 'report.html'),
            '--logfile', str(work_dir / 'locust.log'),
            '--loglevel', 'INFO',
        ]
        if pt.host:
            cmd.extend(['--host', pt.host])

        log_file = open(work_dir / 'locust.log', 'w')
        logger.info(f'[LocustEngine] 启动命令: {" ".join(cmd)}')

        # 4. 启动进程
        self._proc = subprocess.Popen(
            cmd,
            stdout=log_file,
            stderr=subprocess.STDOUT,
            cwd=str(work_dir),
        )

        # 5. 更新数据库状态
        PerformanceTest.objects.filter(id=pt.id).update(
            status=PerformanceTest.Status.RUNNING,
            pid=self._proc.pid,
            work_dir=str(work_dir),
            started_at=datetime.now(),
        )
        logger.info(f'[LocustEngine] 进程已启动 pid={self._proc.pid} work_dir={work_dir}')

    def poll_stats(self) -> Optional[dict]:
        """从 Locust REST API 获取实时统计（Locust headless 模式也有 REST API）"""
        try:
            resp = requests.get(f'{self._web_base()}/stats/requests', timeout=3)
            if resp.status_code == 200:
                return resp.json()
        except Exception as e:
            logger.debug(f'[LocustEngine] poll_stats 失败（可能还未就绪）: {e}')
        return None

    def stop(self) -> None:
        """停止 Locust 进程"""
        from suite.performance_models import PerformanceTest
        pt = self._get_test()
        pid = pt.pid

        if pid:
            try:
                os.kill(pid, signal.SIGTERM)
                logger.info(f'[LocustEngine] 已发送 SIGTERM 给 pid={pid}')
            except ProcessLookupError:
                pass

        PerformanceTest.objects.filter(id=pt.id).update(
            status=PerformanceTest.Status.STOPPED,
            finished_at=datetime.now(),
        )

    def finalize(self) -> None:
        """等待进程结束，汇总最终统计"""
        from suite.performance_models import PerformanceTest
        pt = self._get_test()

        # 尝试读取 CSV 汇总（Locust 生成的 stats_stats.csv）
        summary = self._read_summary(pt.work_dir)
        stats_data = self._read_history(pt.work_dir)
        update_fields = dict(
            status=PerformanceTest.Status.DONE,
            finished_at=datetime.now(),
            summary=summary,
        )
        if stats_data:
            update_fields['stats_data'] = stats_data
        PerformanceTest.objects.filter(id=pt.id).update(**update_fields)
        logger.info(f'[LocustEngine] 测试完成 id={pt.id} summary={summary}')

    def _read_history(self, work_dir: str) -> list:
        """从 stats_history.csv 解析时序数据，用于前端图表"""
        try:
            import csv
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
                ts = int(row['Timestamp'])
                try:
                    rps = float(row.get('Requests/s', 0) or 0)
                    failures = int(row.get('Total Failure Count', 0) or 0)
                    requests = int(row.get('Total Request Count', 0) or 0)
                    avg_rt = float(row.get('Total Average Response Time', 0) or 0)
                    users = int(row.get('User Count', 0) or 0)
                    result.append({
                        'ts':       ts,
                        'elapsed':  ts - start_ts,
                        'rps':      round(rps, 2),
                        'avg_rt':   round(avg_rt, 1),
                        'failures': failures,
                        'requests': requests,
                        'users':    users,
                    })
                except (ValueError, TypeError):
                    continue
            return result
        except Exception as e:
            logger.warning(f'[LocustEngine] 读取 history CSV 失败: {e}')
        return []

    def _read_summary(self, work_dir: str) -> dict:
        """读取 Locust 生成的 CSV 文件，提取汇总数据"""
        try:
            import csv
            stats_file = Path(work_dir) / 'stats_stats.csv'
            if not stats_file.exists():
                return {}
            with open(stats_file, newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
            # 找 Aggregated 行
            for row in rows:
                if row.get('Name') == 'Aggregated':
                    return {
                        'total_requests':   int(row.get('Request Count', 0)),
                        'failure_count':    int(row.get('Failure Count', 0)),
                        'failure_rate':     round(int(row.get('Failure Count', 0)) /
                                                  max(int(row.get('Request Count', 1)), 1), 4),
                        'avg_response_ms':  float(row.get('Average Response Time', 0)),
                        'min_response_ms':  float(row.get('Min Response Time', 0)),
                        'max_response_ms':  float(row.get('Max Response Time', 0)),
                        'p50_response_ms':  float(row.get('50%', 0)),
                        'p95_response_ms':  float(row.get('95%', 0)),
                        'p99_response_ms':  float(row.get('99%', 0)),
                        'rps':              float(row.get('Requests/s', 0)),
                    }
        except Exception as e:
            logger.warning(f'[LocustEngine] 读取 CSV 失败: {e}')
        return {}


def run_performance_test(perf_test_id: int) -> None:
    """
    Celery 任务入口：执行完整的性能测试流程。

    流程：
    1. 启动 Locust 进程
    2. 等待 run_time 秒
    3. 每 5 秒轮询一次统计数据，追加到 stats_data
    4. 进程结束后汇总结果
    """
    from suite.performance_models import PerformanceTest

    engine = LocustEngine(perf_test_id)
    try:
        engine.start()
        pt = engine._get_test()
        run_time = pt.run_time
        stats_data = []
        poll_interval = 5  # 每 5 秒轮询一次
        elapsed = 0

        # 等待 Locust 启动（最多 10 秒）
        time.sleep(3)

        while elapsed < run_time:
            # 检查是否被手动停止
            pt.refresh_from_db()
            if pt.status == PerformanceTest.Status.STOPPED:
                logger.info(f'[LocustEngine] 测试被手动停止 id={perf_test_id}')
                return

            stats = engine.poll_stats()
            if stats:
                point = {
                    'ts': int(time.time()),
                    'elapsed': elapsed,
                    'rps': stats.get('total', {}).get('current_rps', 0),
                    'avg_rt': stats.get('total', {}).get('avg_response_time', 0),
                    'failures': stats.get('total', {}).get('num_failures', 0),
                    'requests': stats.get('total', {}).get('num_requests', 0),
                    'users': stats.get('user_count', 0),
                }
                stats_data.append(point)
                # 每次轮询都保存，方便前端实时读取
                PerformanceTest.objects.filter(id=perf_test_id).update(
                    stats_data=stats_data
                )

            time.sleep(poll_interval)
            elapsed += poll_interval

        engine.finalize()

    except Exception as e:
        logger.exception(f'[LocustEngine] 执行异常: {e}')
        from suite.performance_models import PerformanceTest
        PerformanceTest.objects.filter(id=perf_test_id).update(
            status=PerformanceTest.Status.ERROR,
            error_msg=str(e),
            finished_at=datetime.now(),
        )
