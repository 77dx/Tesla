import json
import logging
import os
import re
import shutil
import subprocess
from pathlib import Path

import redis
from celery import chord, group, shared_task

logger = logging.getLogger(__name__)


# ===========================================================
# [NEW] 新版 Celery 任务入口（v2.0，2026-03-12）
# 直接调用 SuiteRunner，不再生成 YAML / 调用 pytest
# ===========================================================

@shared_task(bind=True)
def run_suite_task(self, result_id: int, case_api_ids: list, initial_context: dict = None,
                   max_retries: int = 0, retry_delay: float = 1.0,
                   timeout_seconds: int = 0, fail_strategy: str = 'continue'):
    """
    [NEW] 套件执行 Celery 任务（v2.0）

    不再生成 YAML 文件，不再调用 pytest 子进程。
    直接通过 SuiteRunner 顺序执行用例，上下文通过 ContextStore(Redis) 共享。

    Args:
        result_id:        RunResult.id
        case_api_ids:     按执行顺序的 CaseAPI id 列表
        initial_context:  初始上下文变量
        max_retries:      单条用例失败后最多重跑次数（0=不重跑）
        retry_delay:      每次重跑前等待秒数
        timeout_seconds:  单条用例超时秒数（0=不限制）
        fail_strategy:    失败策略：'continue'=继续 / 'stop'=立即停止
    """
    from suite.models import RunResult
    from suite.runner import SuiteRunner

    try:
        db_result = RunResult.objects.get(id=result_id)
        base_dir  = Path(db_result.path)
        base_dir.mkdir(parents=True, exist_ok=True)
        log_file  = base_dir / 'log' / 'pytest.log'
    except Exception as e:
        logger.error(f'[run_suite_task] 初始化失败: {e}')
        return {'success': False, 'error': str(e)}

    runner = SuiteRunner(result_id=result_id, log_file=log_file)
    suite_result = runner.run(
        case_api_ids=case_api_ids,
        initial_context=initial_context or {},
        max_retries=max_retries,
        retry_delay=retry_delay,
        timeout_seconds=timeout_seconds,
        fail_strategy=fail_strategy,
    )
    return suite_result.to_dict()


# ===========================================================
# [DEPRECATED] 以下为旧版 DAG 调度代码（v1.x，基于 pytest + YAML）
# 保留仅供参考，请勿在新功能中使用
# ===========================================================


# [DEPRECATED] DAG 工具函数 - 旧版 pytest+YAML 执行链路

def _extract_placeholder_vars(obj) -> set:
    """
    递归扫描对象（dict/list/str）中所有 ${varName} 和 ${func(args)} 占位符，
    返回其中的简单变量名集合（排除函数调用格式）。
    用于自动推断 Endpoint/Case 的隐式 requires。
    """
    found = set()
    if isinstance(obj, str):
        # 匹配 ${varName}（不含括号，排除函数调用）
        for m in re.finditer(r'\$\{(\w+)\}', obj):
            found.add(m.group(1))
    elif isinstance(obj, dict):
        for v in obj.values():
            found |= _extract_placeholder_vars(v)
    elif isinstance(obj, list):
        for item in obj:
            found |= _extract_placeholder_vars(item)
    return found


def _extract_provides_vars(extract_rules) -> set:
    """
    从 Case.extract 规则中提取所有变量名，作为隐式 provides。
    """
    if not extract_rules or not isinstance(extract_rules, dict):
        return set()
    return set(extract_rules.keys())

def _dag_state_path(result_path: Path) -> Path:
    return result_path / "inputs" / "dag_state.json"


def _load_dag_state(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_dag_state(path: Path, state: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def _normalize_list(value):
    if value is None:
        return []
    if isinstance(value, str):
        return [x.strip() for x in value.split(",") if x.strip()]
    if isinstance(value, int):
        return [value]
    return list(value)


def _build_dependency_graph(case_meta: dict) -> dict:
    """
    case_meta: {case_id: {"requires": [...], "provides": [...]}}
    基于用例关联接口的 requires/provides 构建 DAG。
    """
    nodes = sorted(int(x) for x in case_meta.keys())
    provides_map = {}
    for cid in nodes:
        for var in _normalize_list(case_meta[str(cid)].get("provides")):
            provides_map.setdefault(var, []).append(cid)

    deps = {cid: set() for cid in nodes}
    reverse = {cid: set() for cid in nodes}

    for cid in nodes:
        requires = _normalize_list(case_meta[str(cid)].get("requires"))
        for var in requires:
            providers = provides_map.get(var, [])
            if not providers:
                continue
            provider = sorted(providers)[0]
            if provider == cid:
                continue
            deps[cid].add(provider)
            reverse[provider].add(cid)

    return {
        "nodes": nodes,
        "deps": {k: sorted(list(v)) for k, v in deps.items()},
        "reverse": {k: sorted(list(v)) for k, v in reverse.items()},
    }


def _has_cycle(graph: dict) -> bool:
    nodes = list(graph["nodes"])
    indeg = {n: len(graph["deps"].get(n, [])) for n in nodes}
    q = [n for n in nodes if indeg[n] == 0]
    popped = 0
    while q:
        n = q.pop()
        popped += 1
        for nxt in graph["reverse"].get(n, []):
            indeg[nxt] -= 1
            if indeg[nxt] == 0:
                q.append(nxt)
    return popped != len(nodes)


def _redis_context_key(result_id: int) -> str:
    return f"suite:{result_id}:context"


def _append_log(log_file: Path, msg: str):
    """追加一行日志到 pytest.log，同时输出到 logger"""
    log_file.parent.mkdir(parents=True, exist_ok=True)
    import datetime
    ts = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    line = f"[{ts}] {msg}\n"
    logger.info(msg)
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(line)


# ==================== Celery 任务 ====================

@shared_task(bind=True)
def start_suite_dag(self, result_id: int, case_api_ids: list, initial_context: dict = None):
    """
    开始一次 DAG 调度的套件执行（用例粒度）。

    case_api_ids: CaseAPI.id 列表（已启用、已排序）
    initial_context: 初始上下文
    """
    from Tesla import settings
    from case_api.models import Case as CaseAPI
    from suite.models import RunResult

    result = RunResult.objects.get(id=result_id)
    base_dir = Path(result.path)
    base_dir.mkdir(parents=True, exist_ok=True)

    result.status = result.RunStatus.Running
    result.save()

    log_file = base_dir / "log" / "pytest.log"
    _append_log(log_file, f"{'='*60}")
    _append_log(log_file, f"开始执行测试套件 (result_id={result_id})")
    _append_log(log_file, f"执行路径: {base_dir}")
    _append_log(log_file, f"用例数量: {len(case_api_ids)} 条")
    _append_log(log_file, f"{'='*60}")

    # 初始化 Redis 上下文
    redis_url = (
        os.getenv("APIFRAME_REDIS_URL")
        or os.getenv("CELERY_BROKER_URL")
        or getattr(settings, "CELERY_BROKER_URL", "redis://127.0.0.1:6379/0")
    )
    r = redis.Redis.from_url(redis_url, decode_responses=True)
    ctx_key = _redis_context_key(result_id)
    r.delete(ctx_key)
    if initial_context:
        r.hset(ctx_key, mapping={k: str(v) for k, v in initial_context.items()})

    case_api_ids = [int(x) for x in _normalize_list(case_api_ids)]
    # 保留传入的顺序（models.run() 已按 order 排序）
    cases_by_id = {
        c.id: c
        for c in CaseAPI.objects.filter(id__in=case_api_ids).select_related('endpoint')
    }
    ordered_cases = [cases_by_id[cid] for cid in case_api_ids if cid in cases_by_id]

    # 用用例关联接口的 requires/provides 构建 DAG
    # 同时自动扫描 Endpoint 字段和 Case.extract/api_args 中的占位符，
    # 无需手动配置 requires/provides 也能自动感知依赖关系
    meta = {}
    for case in ordered_cases:
        ep = case.endpoint

        # 自动扫描 Endpoint 所有参数字段中的 ${varName} 占位符 → 隐式 requires
        auto_requires = _extract_placeholder_vars({
            'headers': ep.headers,
            'params':  ep.params,
            'data':    ep.data,
            'json':    ep.json,
            'cookies': ep.cookies,
        })
        # 同时扫描 Case.api_args（用例级参数覆盖）
        if case.api_args:
            auto_requires |= _extract_placeholder_vars(case.api_args)

        # 自动从 Case.extract 推断 provides
        auto_provides = _extract_provides_vars(case.extract)

        # 显式配置优先，自动扫描兜底
        explicit_requires = set(ep.requires or [])
        explicit_provides = set(ep.provides or [])

        meta[str(case.id)] = {
            "requires": sorted(explicit_requires | auto_requires),
            "provides": sorted(explicit_provides | auto_provides),
        }

    graph = _build_dependency_graph(meta)

    # 对没有配置 requires/provides 的用例，按传入的 order 顺序建立链式依赖
    # 这样套件中设置的执行顺序能真正生效
    no_dep_cases = [
        c.id for c in ordered_cases
        if not (c.endpoint.requires or c.endpoint.provides)
    ]
    for i in range(1, len(no_dep_cases)):
        prev, curr = no_dep_cases[i - 1], no_dep_cases[i]
        if prev not in graph["deps"][curr]:
            graph["deps"][curr].append(prev)
        if curr not in graph["reverse"][prev]:
            graph["reverse"][prev].append(curr)
    # 同时保证 pending 列表也按 order 顺序排列
    ordered_ids = [c.id for c in ordered_cases]
    graph["nodes"] = [n for n in ordered_ids if n in graph["nodes"]] + \
                     [n for n in graph["nodes"] if n not in ordered_ids]
    if _has_cycle(graph):
        result.status = result.RunStatus.Error
        result.is_pass = False
        result.save()
        raise RuntimeError("DAG 依赖存在环，无法执行")

    state = {
        "result_id": result_id,
        "case_ids": graph["nodes"],
        "deps": graph["deps"],
        "reverse": graph["reverse"],
        "pending": graph["nodes"][:],
        "running": [],
        "succeeded": [],
        "failed": [],
        "skipped": [],
        "wave": 0,
    }
    _save_dag_state(_dag_state_path(base_dir), state)

    return schedule_next_wave.delay(result_id)


@shared_task(bind=True)
def schedule_next_wave(self, result_id: int):
    from suite.models import RunResult

    result = RunResult.objects.get(id=result_id)
    base_dir = Path(result.path)
    state_path = _dag_state_path(base_dir)
    state = _load_dag_state(state_path)

    pending = set(state["pending"])
    succeeded = set(state["succeeded"])
    failed = set(state["failed"])
    skipped = set(state["skipped"])

    ready = []
    blocked = []
    for cid in list(pending):
        preds = state["deps"].get(str(cid), state["deps"].get(cid, []))
        if any(p in failed or p in skipped for p in preds):
            blocked.append(cid)
            continue
        if all(p in succeeded for p in preds):
            ready.append(cid)

    for cid in blocked:
        pending.discard(cid)
        skipped.add(cid)

    if not ready:
        if not pending:
            return finalize_suite_run.delay(result_id)
        result.is_pass = False
        result.status = result.RunStatus.Reporting
        result.save()
        return finalize_suite_run.delay(result_id)

    state["wave"] += 1
    state["pending"] = sorted(list(pending - set(ready)))
    state["running"] = sorted(list(set(state.get("running", [])) | set(ready)))
    _save_dag_state(state_path, state)

    header = group(execute_case_node.s(result_id, cid) for cid in ready)
    return chord(header)(dag_wave_complete.s(result_id=result_id, executed=ready))


@shared_task(bind=True)
def execute_case_node(self, result_id: int, case_id: int):
    """
    执行单条 CaseAPI 用例：
    1. 用 GenerateCase.from_case(case_id) 生成 YAML（仅含该条用例的参数/断言）
    2. 跑 pytest
    3. Allure results 写入独立子目录，由 finalize 合并
    """
    from Tesla import settings
    from suite.models import RunResult
    from case_api.util import GenerateCase
    from case_api.models import Case as CaseAPI

    result = RunResult.objects.get(id=result_id)
    base_dir = Path(result.path)

    log_file = base_dir / "log" / "pytest.log"
    _append_log(log_file, f"\n{'─'*50}")
    _append_log(log_file, f"开始执行用例 #{case_id}")

    # 设置上下文后端
    os.environ["APIFRAME_CONTEXT_BACKEND"] = "redis"
    os.environ["APIFRAME_CONTEXT_PREFIX"] = f"suite:{result_id}"
    os.environ["APIFRAME_EXTRACT_PATH"] = str(base_dir / "extract.yaml")

    # 用例名称（用于文件命名）
    try:
        case = CaseAPI.objects.select_related('endpoint').get(id=case_id)
        case_name = case.name.replace('/', '_').replace(' ', '_')
        _append_log(log_file, f"用例名称: {case.name}")
        _append_log(log_file, f"接口: {case.endpoint.name} [{case.endpoint.method}] {case.endpoint.url}")
    except CaseAPI.DoesNotExist:
        _append_log(log_file, f"ERROR: 用例 #{case_id} 不存在")
        return {"case_id": case_id, "success": False, "returncode": 4, "error": "用例不存在"}

    yaml_path = base_dir / f"test_case_{case_id}_{case_name}.yaml"
    yaml_file = GenerateCase.from_case(case_id).to_yaml(yaml_path)
    if not yaml_file:
        _append_log(log_file, f"ERROR: 用例 #{case_id} 生成 YAML 失败")
        return {"case_id": case_id, "success": False, "returncode": 4, "error": "生成 YAML 失败"}
    _append_log(log_file, f"YAML 文件已生成: {yaml_path.name}")

    # 每个用例独立的 allure-results 目录，避免并发写冲突
    results_raw_dir = base_dir / "results_raw" / str(case_id)
    results_raw_dir.mkdir(parents=True, exist_ok=True)

    log_dir = base_dir / "log"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "pytest.log"

    pytest_args = getattr(settings, "PYTEST_ARGS", ["-v", "--tb=short"])
    test_args = [
        "pytest",
        str(yaml_path),
        f"--alluredir={results_raw_dir}",
    ] + list(pytest_args)

    _append_log(log_file, f"执行命令: {' '.join(test_args)}")
    _append_log(log_file, f"工作目录: {settings.BASE_DIR}")

    log_dir = base_dir / "log"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "pytest.log"

    try:
        proc = subprocess.run(
            test_args,
            capture_output=True,
            text=True,
            timeout=300,
            cwd=str(settings.BASE_DIR)
        )
        ret_code = proc.returncode

        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"\n=== 用例 #{case_id} {case_name} ===\n")
            f.write(proc.stdout)
            if proc.stderr:
                f.write("--- stderr ---\n")
                f.write(proc.stderr)
            f.write(f"\n=== 结果: {'通过' if ret_code == 0 else '失败'} (code={ret_code}) ===\n")
        _append_log(log_file, f"用例 #{case_id} 执行{'通过' if ret_code == 0 else '失败'} (returncode={ret_code})")

    except subprocess.TimeoutExpired:
        _append_log(log_file, f"ERROR: 用例 #{case_id} 执行超时")
        return {"case_id": case_id, "success": False, "returncode": 3, "error": "执行超时"}
    except Exception as e:
        _append_log(log_file, f"ERROR: 用例 #{case_id} 执行异常: {e}")
        return {"case_id": case_id, "success": False, "returncode": 3, "error": str(e)}

    return {"case_id": case_id, "success": ret_code == 0, "returncode": int(ret_code)}


@shared_task(bind=True)
def dag_wave_complete(self, results: list, result_id: int, executed: list):
    """chord callback：收集本波用例执行结果，更新 state，触发下一波。"""
    from suite.models import RunResult

    result = RunResult.objects.get(id=result_id)
    base_dir = Path(result.path)
    state_path = _dag_state_path(base_dir)
    state = _load_dag_state(state_path)
    log_file = base_dir / "log" / "pytest.log"

    running = set(state.get("running", []))
    succeeded = set(state.get("succeeded", []))
    failed = set(state.get("failed", []))

    for item in results or []:
        cid = int(item.get("case_id"))
        ok = bool(item.get("success"))
        running.discard(cid)
        if ok:
            succeeded.add(cid)
        else:
            failed.add(cid)

    state["running"] = sorted(list(running))
    state["succeeded"] = sorted(list(succeeded))
    state["failed"] = sorted(list(failed))
    _save_dag_state(state_path, state)

    _append_log(log_file, f"本波执行完成 - 成功: {sorted(list(succeeded))} 失败: {sorted(list(failed))}")

    if failed:
        result.is_pass = False
        result.save()

    return schedule_next_wave.delay(result_id)


@shared_task(bind=True)
def finalize_suite_run(self, result_id: int):
    """合并 Allure results 并生成报告，更新 RunResult 最终状态。"""
    from Tesla import settings
    from suite.models import RunResult

    result = RunResult.objects.get(id=result_id)
    base_dir = Path(result.path)
    state = _load_dag_state(_dag_state_path(base_dir))
    log_file = base_dir / "log" / "pytest.log"

    succeeded = set(state.get("succeeded", []))
    failed = set(state.get("failed", []))
    skipped = set(state.get("skipped", []))

    _append_log(log_file, f"\n{'='*60}")
    _append_log(log_file, f"所有用例执行完毕，开始生成 Allure 报告")
    _append_log(log_file, f"成功用例: {sorted(list(succeeded))}")
    _append_log(log_file, f"失败用例: {sorted(list(failed))}")
    _append_log(log_file, f"跳过用例: {sorted(list(skipped))}")
    _append_log(log_file, f"{'='*60}")

    # 合并各用例的 allure results
    results_dir = base_dir / "results"
    report_dir = base_dir / "report"
    results_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)

    raw_dir = base_dir / "results_raw"
    if raw_dir.exists():
        for sub in raw_dir.iterdir():
            if sub.is_dir():
                for f in sub.iterdir():
                    if f.is_file():
                        shutil.copy2(f, results_dir / f.name)

    result.is_pass = len(failed) == 0
    result.status = result.RunStatus.Reporting
    result.save()

    allure_args = getattr(settings, "ALLURE_ARGS", ["--clean"])
    timeout = getattr(settings, "ALLURE_GENERATION_TIMEOUT", 120)
    cmd = ["allure", "generate", str(results_dir), "-o", str(report_dir)] + list(allure_args)
    _append_log(log_file, f"执行 Allure 命令: {' '.join(cmd)}")
    try:
        subprocess.run(cmd, capture_output=True, text=True, timeout=timeout,
                       cwd=str(settings.BASE_DIR))
        if (report_dir / "index.html").exists():
            result.status = result.RunStatus.Done
            _append_log(log_file, f"Allure 报告生成成功: {report_dir}")
        else:
            result.status = result.RunStatus.Error
            _append_log(log_file, "ERROR: Allure 报告生成失败，index.html 不存在")
    except Exception as e:
        result.status = result.RunStatus.Error
        _append_log(log_file, f"ERROR: Allure 生成异常: {e}")

    _append_log(log_file, f"套件执行完成 - 结果: {'通过' if result.is_pass else '失败'} 状态: {result.status}")
    result.save()
    return {
        "result_id": result_id,
        "is_pass": result.is_pass,
        "succeeded": sorted(list(succeeded)),
        "failed": sorted(list(failed)),
        "skipped": state.get("skipped", []),
        "status": int(result.status),
    }


# ==================== 定时任务 ====================

def run_by_cron(suite_id):
    """定时执行测试套件"""
    from suite.models import Suite
    try:
        suite = Suite.objects.get(id=suite_id)
        logger.info(f"定时执行套件: {suite.name} (ID={suite.id})")
        result = suite.run()
        logger.info(f"定时执行完成，结果 ID: {result.id}")
    except Exception as e:
        logger.error(f"定时执行套件失败: {e}")


def run_by_cron_task(suite_id):
    """django-q 定时任务入口"""
    run_by_cron(suite_id)
