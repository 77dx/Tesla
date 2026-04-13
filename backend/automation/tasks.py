from pathlib import Path
import os
import shutil
import subprocess
from django.conf import settings
from celery import shared_task

from .models import AutomationRun


def _append_log(log_file: Path, message: str):
    log_file.parent.mkdir(parents=True, exist_ok=True)
    with log_file.open('a', encoding='utf-8') as f:
        f.write(message.rstrip() + '\n')


def _run_command(command: str, cwd: str, env: dict, log_file: Path):
    process = subprocess.run(command, shell=True, cwd=cwd, env=env, capture_output=True, text=True)
    if process.stdout:
        _append_log(log_file, process.stdout)
    if process.stderr:
        _append_log(log_file, process.stderr)
    return process.returncode


@shared_task
def run_automation_task(run_id: int):
    run = AutomationRun.objects.select_related('suite__automation_project', 'environment').get(id=run_id)
    project = run.suite.automation_project

    reports_base = Path(getattr(settings, 'REPORT_DIR', Path(settings.BASE_DIR) / 'reports')) / 'automation'
    run_dir = reports_base / f'run_{run.id}'
    run_dir.mkdir(parents=True, exist_ok=True)
    log_file = run_dir / 'run.log'
    run.log_path = str(log_file)
    run.report_path = str(run_dir / project.report_dir)
    run.workdir = project.local_repo_path or ''
    run.save(update_fields=['log_path', 'report_path', 'workdir'])
    run.mark_running()

    repo_path = Path(project.local_repo_path or '')
    if not project.local_repo_path:
        run.mark_finished(AutomationRun.Status.ERROR, {'error': 'MVP 仅支持本地仓库路径 local_repo_path'})
        _append_log(log_file, 'ERROR: 未配置 local_repo_path，当前 MVP 不拉取远程仓库。')
        return
    if not repo_path.exists():
        run.mark_finished(AutomationRun.Status.ERROR, {'error': f'本地仓库不存在: {repo_path}'})
        _append_log(log_file, f'ERROR: 本地仓库不存在: {repo_path}')
        return

    env = os.environ.copy()
    env['PLAYWRIGHT_HTML_REPORT'] = str(run_dir / project.report_dir)
    env['PLAYWRIGHT_JUNIT_OUTPUT_NAME'] = 'results.xml'
    env['TESLA_AUTOMATION_RUN_ID'] = str(run.id)
    env['TESLA_AUTOMATION_RUN_DIR'] = str(run_dir)
    if run.base_url:
        env['BASE_URL'] = run.base_url
    for key, value in (run.variables or {}).items():
        env[str(key)] = '' if value is None else str(value)

    payload = {'steps': []}
    try:
        if project.install_command:
            _append_log(log_file, f'$ {project.install_command}')
            code = _run_command(project.install_command, str(repo_path), env, log_file)
            payload['steps'].append({'name': 'install', 'code': code})
            if code != 0:
                run.mark_finished(AutomationRun.Status.ERROR, payload)
                return

        command = run.command or project.test_command
        _append_log(log_file, f'$ {command}')
        code = _run_command(command, str(repo_path), env, log_file)
        payload['steps'].append({'name': 'test', 'code': code})

        report_dir = repo_path / project.report_dir
        if report_dir.exists() and report_dir.is_dir():
            target = run_dir / project.report_dir
            if target.exists():
                shutil.rmtree(target)
            shutil.copytree(report_dir, target)
            run.report_path = str(target)
            run.save(update_fields=['report_path'])

        run.mark_finished(AutomationRun.Status.PASSED if code == 0 else AutomationRun.Status.FAILED, payload)
    except Exception as exc:
        _append_log(log_file, f'ERROR: {exc}')
        run.mark_finished(AutomationRun.Status.ERROR, {'error': str(exc), **payload})
