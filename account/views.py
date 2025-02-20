from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.authtoken.admin import User
from rest_framework.decorators import action
from rest_framework.response import Response
from .serializers import LoginSerializer, ProfileSerializer, ResetPasswordSerializer
from .models import Profile
from drf_spectacular.utils import extend_schema

@extend_schema(
    tags=['Account']
)
class ProfileViewSet(viewsets.GenericViewSet):
    @extend_schema(
        request=LoginSerializer,
        responses=ProfileSerializer,
    )
    @action(methods=['POST'], detail=False)
    def login(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        profile = Profile.objects.get(user=serializer.validated_data['user'])
        serializer = ProfileSerializer(profile)

        return Response(serializer.data)

    @extend_schema(
        request=ResetPasswordSerializer,
    )
    @action(methods=['POST'], detail=False)
    def reset_password(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user: User = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()

    @extend_schema(
        responses=ProfileSerializer
    )
    @action(methods=['POST'], detail=False)
    def profile(self, request):
        profile = Profile.objects.get(user=request.user)
        serializer = ProfileSerializer(profile)
        return Response(serializer.data)

    @extend_schema(
        request=ProfileSerializer,
        responses=ProfileSerializer,
    )
    @action(methods=['POST'], detail=False)
    def modify(self, request):
        profile = Profile.objects.get(user=request.data)
        serializer = ProfileSerializer(profile, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)



















