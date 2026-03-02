"""
@ Title:
@ Author: Cathy
@ Time: 2024/12/9 15:20
"""
from pathlib import Path
from rest_framework import serializers
from .models import Suite, RunResult


class SuiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Suite
        fields = "__all__"


class RunResultSerializer(serializers.ModelSerializer):
    report_url = serializers.SerializerMethodField()
    log_url = serializers.SerializerMethodField()
    artifacts_url = serializers.SerializerMethodField()

    class Meta:
        model = RunResult
        exclude = ["path"]

    def get_report_url(self, obj):
        path = Path(str(obj.path))
        dir_name = path.name
        return f"/api/suite/static/{dir_name}/report/index.html"

    def get_log_url(self, obj):
        path = Path(str(obj.path))
        dir_name = path.name
        return f"/api/suite/static/{dir_name}/log/pytest.log"

    def get_artifacts_url(self, obj):
        path = Path(str(obj.path))
        dir_name = path.name
        return f"/api/suite/static/{dir_name}/artifacts.zip"


