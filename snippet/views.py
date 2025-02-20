from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from beifan.models import FeedBack
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from snippet.customresponse import CustomResponse
from rest_framework.authtoken.models import Token
from snippet.serializers import LoginSerializer, RegisterSerializer, FeedBackAllSerializer
from rest_framework.exceptions import ValidationError



class SnippetViewSet(viewsets.GenericViewSet):
    permission_classes = [AllowAny]
    """保存数据进django的用户表中"""
    @action(detail=False, methods=["post"], url_path="register")
    def register(self, request):
        serializer = RegisterSerializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            User.objects.create_user(
                username=serializer.validated_data["username"],
                email=serializer.validated_data["email"],
                password=serializer.validated_data["password"])
            return CustomResponse(data=serializer.data, msg="success", code=status.HTTP_201_CREATED)
        except ValidationError as e:
            error_msg = "; ".join([f"{key}: {', '.join(val)}" for key, val in e.detail.items()])
            return CustomResponse(data={}, msg=f"fail, {error_msg}", code=status.HTTP_400_BAD_REQUEST)


    @action(detail=False, methods=["post"], url_path="login")
    def login(self, request):
        serializer = LoginSerializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True) # 此时验证不通过会抛出异常
            return CustomResponse(data=serializer.data, msg="success", code=status.HTTP_200_OK)
        except ValidationError as e:
            error_msg = "; ".join([f"{key}: {', '.join(val)}" for key, val in e.detail.items()])
            return CustomResponse(data={}, msg=f"fail，{error_msg}", code=e.status_code)

class FeedBackAllViewSet(viewsets.GenericViewSet):
    @action(detail=False, methods=["post"], url_path="feedbackall")
    def feedback(self, request):
        req = request.data
        if "id" in req:
            try:
                feedback = FeedBack.objects.get(id=req.get("id"))
                serializer = FeedBackAllSerializer(feedback)
            except FeedBack.DoesNotExist:
                return CustomResponse(data={}, msg="feedback not found", code=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            feedbacks = FeedBack.objects.all()
            serializer = FeedBackAllSerializer(feedbacks, many=True)

        return CustomResponse(data=serializer.data, msg="success", code=status.HTTP_200_OK)






