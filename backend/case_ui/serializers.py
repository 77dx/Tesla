"""
@ Title:
@ Author: Cathy
@ Time: 2024/12/9 15:20
"""
from rest_framework import serializers
from .models import Element, Case


class ElementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Element
        fields = "__all__"

class UIStepserializer(serializers.Serializer):
    步骤 = serializers.CharField()
    步骤名 = serializers.CharField()
    关键字 = serializers.CharField()
    参数 = serializers.CharField()
    _BlankField = serializers.ListField()

class CaseUISerializer(serializers.ModelSerializer):
    usefixtures = serializers.ListField()
    steps = UIStepserializer(many=True)

    class Meta:
        model = Case
        fields = "__all__"

