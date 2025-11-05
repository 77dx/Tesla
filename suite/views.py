import time
from concurrent.futures.thread import ThreadPoolExecutor
from pathlib import Path
from django.views.static import serve
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets, permissions
from rest_framework.decorators import action, permission_classes, api_view
from rest_framework.response import Response

from case_api.views import run_pytest
from suite.serializers import SuiteSerializer, RunResultSerializer
from .models import Suite, RunResult
from case_api.models import Case as CaseAPI
from case_ui.models import Case as CaseUI

@api_view()
def static_server(request, path, document_root=None, show_indexes=False):
    resp = serve(request, path, document_root, show_indexes)

    if resp.status_code == 200:
        if path.endswith(".yaml") or path.endswith(".log"):
            resp.headers["Content-Type"] = "text/css; charset=utf-8"

    return resp

@extend_schema(tags=["Suite"])
class SuiteViewSet(viewsets.ModelViewSet):
    serializer_class = SuiteSerializer
    queryset = Suite.objects.all()

    @action(methods=['POST'], detail=True)
    def run(self, request, pk):
        """执行测试套件"""
        obj: Suite = self.get_object()
        if obj.run_type == obj.RunType.ONCE:
            result = obj.run()
            return Response({"result_id": result.id})
        else:
            return Response({"result_id": -1, "msg": f"本套件不允许手动触发, 运行类型={obj.run_type}"}, status=400)

    @action(methods=['POST', 'GET'], detail=True, permission_classes=[permissions.AllowAny])
    def webhook(self, request, pk):
        """执行测试套件"""
        obj: Suite = self.get_object()
        hook_key = request.query_params.get('key')

        if obj.run_type == obj.RunType.WebHook:
            if hook_key == obj.hook_key:
                result = obj.run()
                return Response({"result_id": result.id})
            else:
                return Response({"result_id": -2, "msg": f"webHook Key不正确,{hook_key}"}, status=400)
        else:
            return Response({"result_id": -1, "msg": f"本套件不允许手动触发, 运行类型={obj.run_type}"}, status=400)


@extend_schema(tags=["Suite"])
class RunResultViewSet(viewsets.mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = RunResult.objects.all()
    serializer_class = RunResultSerializer

    @action(methods=['POST'], detail=True)
    def run_case_api(self, request, pk):
        obj: ... = CaseAPI.objects.get(id=pk)
        path = Path("upload_yaml") / f"{pk}_{time.time()}"
        path.mkdir(parents=True, exist_ok=True)

        obj.to_yaml(path)

        pool = ThreadPoolExecutor(max_workers=6)
        pool.map(run_pytest, [path])
        return Response({"id": pk, "path": str(path)})

    @action(methods=['POST'], detail=True)
    def run_case_ui(self, request, pk):
        obj: ... = CaseUI.objects.get(id=pk)
        path = Path("upload_yaml") / f"{pk}_{time.time()}"
        path.mkdir(parents=True, exist_ok=True)

        obj.to_xlsx(path)

        pool = ThreadPoolExecutor(max_workers=6)
        pool.map(run_pytest, [path])
        return Response({"id": pk, "path": str(path)})