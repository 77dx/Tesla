from rest_framework import serializers

from product_line.models import ProductLine
from project.models import Project

from .models import Element, Case, CaseRunHistory


class ElementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Element
        fields = '__all__'


class CaseRunHistorySerializer(serializers.ModelSerializer):
    environment_name = serializers.CharField(source='environment.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = CaseRunHistory
        fields = '__all__'


class CaseUISerializer(serializers.ModelSerializer):
    project = serializers.PrimaryKeyRelatedField(queryset=Project.objects.all(), required=False, allow_null=True)
    product_line = serializers.PrimaryKeyRelatedField(queryset=ProductLine.objects.all(), required=False, allow_null=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    product_line_name = serializers.CharField(source='product_line.name', read_only=True)
    created_by_name = serializers.SerializerMethodField(read_only=True)
    sprint_name = serializers.SerializerMethodField(read_only=True)
    requirement_title = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Case
        fields = '__all__'

    def get_created_by_name(self, obj):
        return obj.updated_by.username if obj.updated_by else (obj.created_by.username if obj.created_by else None)

    def get_sprint_name(self, obj):
        return obj.sprint.name if obj.sprint else None

    def get_requirement_title(self, obj):
        return obj.requirement.title if obj.requirement else None

    def update(self, instance, validated_data):
        instance.version = (instance.version or 1) + 1
        obj = super().update(instance, validated_data)
        obj.save(update_fields=['version'])
        return obj
