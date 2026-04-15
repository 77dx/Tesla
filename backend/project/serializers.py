"""
@ Title:
@ Author: Cathy
@ Time: 2024/12/9 14:13
"""
from rest_framework import serializers
from .models import (
    Project, Config, Sprint, Requirement,
    ProjectCaseRef, ProjectSuiteRef, SprintCaseRef, SprintSuiteRef,
)
from case_api.models import Case
# from suite.models import Suite


class ProjectSerializer(serializers.ModelSerializer):
    intro = serializers.CharField(required=False, default='', allow_blank=True)
    url = serializers.CharField(required=False, default='', allow_blank=True)
    pm_name = serializers.SerializerMethodField(read_only=True)
    product_line_name = serializers.SerializerMethodField(read_only=True)
    sprint_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Project
        fields = "__all__"
        extra_kwargs = {
            'name': {'required': False},
        }

    def get_pm_name(self, obj):
        if obj.pm:
            try:
                return obj.pm.profile.nickname or obj.pm.username
            except Exception:
                return obj.pm.username
        return None

    def get_product_line_name(self, obj):
        return obj.product_line.name if obj.product_line else None

    def get_sprint_count(self, obj):
        return obj.sprints.count()


class ConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = Config
        fields = "__all__"


class RefBaseSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'


class ProjectCaseRefSerializer(RefBaseSerializer):
    case_name = serializers.CharField(source='case.name', read_only=True)

    class Meta(RefBaseSerializer.Meta):
        model = ProjectCaseRef


class ProjectSuiteRefSerializer(RefBaseSerializer):
    suite_name = serializers.CharField(source='suite.name', read_only=True)

    class Meta(RefBaseSerializer.Meta):
        model = ProjectSuiteRef


class SprintCaseRefSerializer(RefBaseSerializer):
    case_name = serializers.CharField(source='case.name', read_only=True)

    class Meta(RefBaseSerializer.Meta):
        model = SprintCaseRef


class SprintSuiteRefSerializer(RefBaseSerializer):
    suite_name = serializers.CharField(source='suite.name', read_only=True)

    class Meta(RefBaseSerializer.Meta):
        model = SprintSuiteRef


class SprintSerializer(serializers.ModelSerializer):
    project_name       = serializers.SerializerMethodField(read_only=True)
    product_line_name  = serializers.SerializerMethodField(read_only=True)
    created_by_name    = serializers.SerializerMethodField(read_only=True)
    owner_name         = serializers.SerializerMethodField(read_only=True)
    operator_name      = serializers.SerializerMethodField(read_only=True)
    requirement_count  = serializers.SerializerMethodField(read_only=True)
    is_overdue         = serializers.SerializerMethodField(read_only=True)
    done_count         = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model  = Sprint
        fields = [
            'id', 'project', 'project_name', 'product_line', 'product_line_name', 'name', 'goal',
            'status', 'start_date', 'end_date', 'is_overdue',
            'requirement_count', 'done_count',
            'owner', 'owner_name', 'operator_name',
            'created_by', 'created_by_name', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_project_name(self, obj):
        return obj.project.name if obj.project else None

    def get_product_line_name(self, obj):
        return obj.product_line.name if obj.product_line else None

    def get_created_by_name(self, obj):
        if not obj.created_by: return None
        try: return obj.created_by.profile.nickname or obj.created_by.username
        except Exception: return obj.created_by.username

    def get_owner_name(self, obj):
        if not obj.owner: return None
        try: return obj.owner.profile.nickname or obj.owner.username
        except Exception: return obj.owner.username

    def get_operator_name(self, obj):
        u = obj.updated_by or obj.created_by
        if not u: return None
        try: return u.profile.nickname or u.username
        except Exception: return u.username

    def get_requirement_count(self, obj):
        return obj.requirements.count()

    def get_done_count(self, obj):
        return obj.requirements.filter(status='done').count()

    def get_is_overdue(self, obj):
        return obj.is_overdue


class RequirementSerializer(serializers.ModelSerializer):
    sprint_name      = serializers.SerializerMethodField(read_only=True)
    project_name     = serializers.SerializerMethodField(read_only=True)
    assignee_name    = serializers.SerializerMethodField(read_only=True)
    created_by_name  = serializers.SerializerMethodField(read_only=True)
    priority_label   = serializers.SerializerMethodField(read_only=True)
    status_label     = serializers.SerializerMethodField(read_only=True)
    case_count       = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model  = Requirement
        fields = [
            'id', 'sprint', 'sprint_name', 'project_name',
            'title', 'desc', 'status', 'status_label',
            'priority', 'priority_label',
            'assignee', 'assignee_name',
            'start_date', 'due_date', 'estimate',
            'case_count',
            'created_by', 'created_by_name', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_sprint_name(self, obj):
        return obj.sprint.name if obj.sprint else None

    def get_project_name(self, obj):
        return obj.sprint.project.name if obj.sprint and obj.sprint.project else None

    def get_assignee_name(self, obj):
        if not obj.assignee: return None
        try: return obj.assignee.profile.nickname or obj.assignee.username
        except Exception: return obj.assignee.username

    def get_created_by_name(self, obj):
        if not obj.created_by: return None
        try: return obj.created_by.profile.nickname or obj.created_by.username
        except Exception: return obj.created_by.username

    def get_priority_label(self, obj):
        return obj.get_priority_display()

    def get_status_label(self, obj):
        return obj.get_status_display()

    def get_case_count(self, obj):
        return obj.cases.count() if hasattr(obj, 'cases') else 0