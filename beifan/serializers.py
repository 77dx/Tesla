"""
@ Title:
@ Author: Cathy
@ Time: 2024/11/13 10:21
"""
from django.contrib.auth.models import User
from rest_framework.serializers import ModelSerializer
from .models import FeedBack


class FeedBackSerializer(ModelSerializer):

    class Meta:
        model = FeedBack
        fields = '__all__'


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'is_superuser']

