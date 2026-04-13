"""
性能测试 API 视图

Endpoints:
  POST   /api/suite/performance/              创建并启动性能测试
  GET    /api/suite/performance/              历史列表
  GET    /api/suite/performance/{id}/         测试详情（含实时 stats_data）
  POST   /api/suite/performance/{id}/stop/    停止测试
  DELETE /api/suite/performance/{id}/         删除记录
  GET    /api/suite/performance/{id}/report/  获取 HTML 报告路径
"""
import logging
from datetime import datetime
from pathlib import Path

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import permissions

from snippet.base_viewset import BaseViewSet
from .performance_models import PerformanceTest
from .performance_serializers import PerformanceTestSerializer, PerformanceTestCreateSerializer

logger = logging.getLogger(__name__)


@extend_schema(tags=['Performance'])
class PerformanceTestViewSet(BaseViewSet):
    """
    性能测试管理接口。
    """
    queryset = PerformanceTest.objects.select_related('suite', 'project', 'created_by').order_by('-created_at')
    serializer_class = PerformanceTestSerializer
    permission_classes = [permissions.IsAuthenticated]
    product_line_field = None
    search_fields = ['suite__name']

    def get_queryset(self):
        qs = super().get_queryset()
        suite_id = self.request.query_params.get('suite')
        if suite_id:
            qs = qs.filter(suite_id=suite_id)
        project_id = self.request.query_params.get('project')
        if project_id:
            qs = qs.filter(project_id=project_id)
        status_filter = self.request.query_params.get('status')
        if status_filter:
            qs = qs.filter(status=status_filter)
        return qs

    def create(self, request, *args, **kwargs):
        """创建并立即启动性能测试"""
        serializer = PerformanceTestCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # 补充 project、created_by
        suite = serializer.validated_data['suite']
        pt = serializer.save(
            project=suite.project,
            created_by=request.user if request.user.is_authenticated else None,
            status=PerformanceTest.Status.PENDING,
        )

        # 异步启动
        try:
            from suite.performance_tasks import start_performance_test_task
            start_performance_test_task(pt.id)
        except Exception as e:
            logger.error(f'[PerfAPI] 启动任务失败: {e}')
            pt.status = PerformanceTest.Status.ERROR
            pt.error_msg = str(e)
            pt.save(update_fields=['status', 'error_msg'])

        return Response(
            PerformanceTestSerializer(pt).data,
            status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=['post'], url_path='run')
    def run(self, request, pk=None):
        """对已保存的配置重新发起一次压测（重置状态后异步启动）"""
        pt = self.get_object()
        if pt.status in (PerformanceTest.Status.RUNNING, PerformanceTest.Status.PENDING):
            return Response(
                {'msg': f'当前状态 {pt.status}，请等待本次压测结束后再启动'},
                status=status.HTTP_400_BAD_REQUEST
            )
        # 重置状态
        import datetime
        PerformanceTest.objects.filter(id=pt.id).update(
            status=PerformanceTest.Status.PENDING,
            pid=None,
            error_msg='',
            summary=None,
            stats_data=None,
            started_at=None,
            finished_at=None,
        )
        try:
            from suite.performance_tasks import start_performance_test_task
            start_performance_test_task(pt.id)
        except Exception as e:
            logger.error(f'[PerfAPI] run 启动失败: {e}')
            PerformanceTest.objects.filter(id=pt.id).update(
                status=PerformanceTest.Status.ERROR,
                error_msg=str(e),
            )
        pt.refresh_from_db()
        return Response(PerformanceTestSerializer(pt).data)

    @action(detail=True, methods=['post'], url_path='stop')
    def stop(self, request, pk=None):
        """停止正在运行的性能测试"""
        pt = self.get_object()
        if pt.status not in (PerformanceTest.Status.RUNNING, PerformanceTest.Status.PENDING):
            return Response(
                {'msg': f'当前状态 {pt.status} 无法停止'},
                status=status.HTTP_400_BAD_REQUEST
            )
        from suite.locust_engine import LocustEngine
        engine = LocustEngine(pt.id)
        engine.stop()
        pt.refresh_from_db()
        return Response(PerformanceTestSerializer(pt).data)

    @action(detail=True, methods=['get'], url_path='report')
    def report(self, request, pk=None):
        """返回 HTML 报告的访问 URL"""
        pt = self.get_object()
        if not pt.work_dir:
            return Response({'msg': '报告尚未生成'}, status=status.HTTP_404_NOT_FOUND)
        report_path = Path(pt.work_dir) / 'report.html'
        if not report_path.exists():
            return Response({'msg': '报告文件不存在'}, status=status.HTTP_404_NOT_FOUND)
        # 将绝对路径转换为相对 upload_yaml 的相对路径，通过 /api/suite/static/ 访问
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
        return Response({
            'report_url': report_url,
            'work_dir': pt.work_dir,
        })

    @action(detail=True, methods=['get'], url_path='log')
    def log(self, request, pk=None):
        """读取 locust.log 最新 N 行（默认 200 行）"""
        pt = self.get_object()
        if not pt.work_dir:
            return Response({'lines': [], 'msg': '工作目录尚未创建'})
        log_path = Path(pt.work_dir) / 'locust.log'
        if not log_path.exists():
            return Response({'lines': [], 'msg': '日志文件尚未生成'})
        try:
            n = int(request.query_params.get('n', 200))
            with open(log_path, 'r', encoding='utf-8', errors='replace') as f:
                lines = f.readlines()
            return Response({
                'lines': [l.rstrip('\n') for l in lines[-n:]],
                'total': len(lines),
                'status': pt.status,
            })
        except Exception as e:
            logger.warning(f'[PerfAPI] 读取日志失败: {e}')
            return Response({'lines': [], 'msg': str(e)})

    @action(detail=True, methods=['get'], url_path='stats')
    def stats(self, request, pk=None):
        """实时统计数据（轮询用）"""
        pt = self.get_object()
        return Response({
            'id':         pt.id,
            'status':     pt.status,
            'stats_data': pt.stats_data or [],
            'summary':    pt.summary or {},
            'started_at': pt.started_at,
            'finished_at': pt.finished_at,
        })
