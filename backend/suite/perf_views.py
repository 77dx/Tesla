"""
压测配置与结果 API 视图

Endpoints:
  # 压测配置
  GET    /api/suite/perf-config/              配置列表
  POST   /api/suite/perf-config/              创建配置
  GET    /api/suite/perf-config/{id}/         配置详情
  PUT    /api/suite/perf-config/{id}/         编辑配置
  DELETE /api/suite/perf-config/{id}/         删除配置
  POST   /api/suite/perf-config/{id}/run/     创建新执行记录并启动压测

  # 执行结果
  GET    /api/suite/perf-result/              结果列表（可按 config 过滤）
  GET    /api/suite/perf-result/{id}/         结果详情
  DELETE /api/suite/perf-result/{id}/         删除结果
  POST   /api/suite/perf-result/{id}/stop/    停止执行
  GET    /api/suite/perf-result/{id}/stats/   实时统计（轮询）
  GET    /api/suite/perf-result/{id}/log/     运行日志
  GET    /api/suite/perf-result/{id}/report/  HTML 报告路径
"""
import logging
from pathlib import Path
from datetime import datetime

from drf_spectacular.utils import extend_schema
from rest_framework import status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from snippet.base_viewset import BaseViewSet
from .perf_models import PerformanceConfig, PerformanceResult
from .perf_serializers import (
    PerformanceConfigSerializer, PerformanceConfigCreateSerializer,
    PerformanceResultSerializer,
)

logger = logging.getLogger(__name__)


@extend_schema(tags=['PerfConfig'])
class PerformanceConfigViewSet(BaseViewSet):
    """压测配置管理"""
    queryset = PerformanceConfig.objects.select_related('suite', 'project', 'created_by').order_by('-created_at')
    serializer_class = PerformanceConfigSerializer
    permission_classes = [permissions.IsAuthenticated]
    product_line_field = None
    search_fields = ['name', 'suite__name']

    def get_queryset(self):
        qs = super().get_queryset()
        suite_id = self.request.query_params.get('suite')
        if suite_id:
            qs = qs.filter(suite_id=suite_id)
        project_id = self.request.query_params.get('project')
        if project_id:
            qs = qs.filter(project_id=project_id)
        return qs

    def create(self, request, *args, **kwargs):
        """创建配置（不自动启动）"""
        serializer = PerformanceConfigCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        suite = serializer.validated_data['suite']
        cfg = serializer.save(
            project=suite.project,
            created_by=request.user if request.user.is_authenticated else None,
        )
        return Response(PerformanceConfigSerializer(cfg).data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        """编辑配置"""
        partial = kwargs.pop('partial', False)
        cfg = self.get_object()
        serializer = PerformanceConfigCreateSerializer(cfg, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        # 如果套件改了，同步更新 project
        if 'suite' in serializer.validated_data:
            serializer.validated_data['project'] = serializer.validated_data['suite'].project
        cfg = serializer.save()
        return Response(PerformanceConfigSerializer(cfg).data)

    @action(detail=True, methods=['post'], url_path='run')
    def run(self, request, pk=None):
        """基于此配置创建一条新执行记录并启动压测"""
        cfg = self.get_object()

        # 检查是否有正在执行的结果
        running = cfg.results.filter(status__in=['pending', 'running']).first()
        if running:
            return Response(
                {'msg': f'已有执行中的任务 result_id={running.id}，请等待完成后再启动'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 创建新执行记录（快照当前配置参数）
        result = PerformanceResult.objects.create(
            config=cfg,
            users=cfg.users,
            spawn_rate=cfg.spawn_rate,
            run_time=cfg.run_time,
            host=cfg.host,
            status=PerformanceResult.Status.PENDING,
            created_by=request.user if request.user.is_authenticated else None,
        )

        # 异步启动
        try:
            from suite.perf_tasks import start_perf_result_task
            start_perf_result_task(result.id)
        except Exception as e:
            logger.error(f'[PerfConfig] run 启动失败: {e}')
            PerformanceResult.objects.filter(id=result.id).update(
                status=PerformanceResult.Status.ERROR,
                error_msg=str(e),
            )

        result.refresh_from_db()
        return Response(PerformanceResultSerializer(result).data, status=status.HTTP_201_CREATED)


@extend_schema(tags=['PerfResult'])
class PerformanceResultViewSet(BaseViewSet):
    """压测执行结果管理"""
    queryset = PerformanceResult.objects.select_related('config', 'config__suite', 'config__project', 'created_by').order_by('-created_at')
    serializer_class = PerformanceResultSerializer
    permission_classes = [permissions.IsAuthenticated]
    product_line_field = None
    search_fields = ['config__name', 'config__suite__name']

    def get_queryset(self):
        qs = super().get_queryset()
        config_id = self.request.query_params.get('config')
        if config_id:
            qs = qs.filter(config_id=config_id)
        suite_id = self.request.query_params.get('suite')
        if suite_id:
            qs = qs.filter(config__suite_id=suite_id)
        project_id = self.request.query_params.get('project')
        if project_id:
            qs = qs.filter(config__project_id=project_id)
        status_filter = self.request.query_params.get('status')
        if status_filter:
            qs = qs.filter(status=status_filter)
        return qs

    @action(detail=True, methods=['post'], url_path='stop')
    def stop(self, request, pk=None):
        result = self.get_object()
        if result.status not in ('running', 'pending'):
            return Response({'msg': f'当前状态 {result.status} 无法停止'}, status=status.HTTP_400_BAD_REQUEST)
        from suite.perf_engine import stop_perf_result
        stop_perf_result(result.id)
        result.refresh_from_db()
        return Response(PerformanceResultSerializer(result).data)

    @action(detail=True, methods=['get'], url_path='stats')
    def stats(self, request, pk=None):
        result = self.get_object()
        return Response({
            'id':         result.id,
            'status':     result.status,
            'stats_data': result.stats_data or [],
            'summary':    result.summary or {},
            'started_at': result.started_at,
            'finished_at': result.finished_at,
        })

    @action(detail=True, methods=['get'], url_path='log')
    def log(self, request, pk=None):
        result = self.get_object()
        if not result.work_dir:
            return Response({'lines': [], 'msg': '工作目录尚未创建'})
        log_path = Path(result.work_dir) / 'locust.log'
        if not log_path.exists():
            return Response({'lines': [], 'msg': '日志文件尚未生成'})
        try:
            n = int(request.query_params.get('n', 200))
            with open(log_path, 'r', encoding='utf-8', errors='replace') as f:
                lines = f.readlines()
            return Response({
                'lines': [l.rstrip('\n') for l in lines[-n:]],
                'total': len(lines),
                'status': result.status,
            })
        except Exception as e:
            return Response({'lines': [], 'msg': str(e)})

    @action(detail=True, methods=['get'], url_path='report')
    def report(self, request, pk=None):
        result = self.get_object()
        if not result.work_dir:
            return Response({'msg': '报告尚未生成'}, status=status.HTTP_404_NOT_FOUND)
        report_path = Path(result.work_dir) / 'report.html'
        if not report_path.exists():
            return Response({'msg': '报告文件不存在'}, status=status.HTTP_404_NOT_FOUND)
        try:
            from django.conf import settings
            base = getattr(settings, 'SUITE_EXECUTION_BASE_DIR', None)
            if base:
                rel = report_path.relative_to(base)
                report_url = f'/api/suite/static/{rel}'
            else:
                report_url = None
        except ValueError:
            report_url = None
        return Response({'report_url': report_url, 'work_dir': result.work_dir})
