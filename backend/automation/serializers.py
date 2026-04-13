from rest_framework import serializers

from .models import AutomationProject, AutomationSuite, AutomationRun


class AutomationProjectSerializer(serializers.ModelSerializer):
    product_line_name = serializers.SerializerMethodField()
    project_name = serializers.SerializerMethodField()

    class Meta:
        model = AutomationProject
        fields = '__all__'

    def get_product_line_name(self, obj):
        return obj.product_line.name if obj.product_line else None

    def get_project_name(self, obj):
        return obj.project.name if obj.project else None


class AutomationSuiteSerializer(serializers.ModelSerializer):
    automation_project_name = serializers.SerializerMethodField()
    product_line = serializers.SerializerMethodField()

    class Meta:
        model = AutomationSuite
        fields = '__all__'

    def get_automation_project_name(self, obj):
        return obj.automation_project.name if obj.automation_project else None

    def get_product_line(self, obj):
        return obj.automation_project.product_line_id if obj.automation_project else None


class AutomationRunSerializer(serializers.ModelSerializer):
    suite_name = serializers.SerializerMethodField()
    automation_project_name = serializers.SerializerMethodField()

    class Meta:
        model = AutomationRun
        fields = '__all__'

    def get_suite_name(self, obj):
        return obj.suite.name if obj.suite else None

    def get_automation_project_name(self, obj):
        return obj.suite.automation_project.name if obj.suite and obj.suite.automation_project else None
