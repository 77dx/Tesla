"""
@ Title:
@ Author: Cathy
@ Time: 2024/12/9 15:20
"""
from rest_framework import serializers
from .models import Endpoint, Case


class EndpointSerializer(serializers.ModelSerializer):
    class Meta:
        model = Endpoint
        fields = "__all__"


class CaseSerializer(serializers.ModelSerializer):
    # endpoint = EndpointSerializer()
    class Meta:
        model = Case
        fields = "__all__"