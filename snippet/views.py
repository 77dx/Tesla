from PIL.ImtImagePlugin import field

from snippet.models import Snippet
from snippet.serializers import SnippetSerializer
from rest_framework import generics, viewsets
from rest_framework.decorators import api_view, action
from django.http import JsonResponse

# 第二版 ViewSet版
class SnippetViewSet(viewsets.ModelViewSet):
    queryset = Snippet.objects.all()
    serializer_class = SnippetSerializer

    # 自己写个api
    @ action(detail=False, methods=["post"])
    def get_by_id(self, request):
        snippet_id = request.data.get("id")
        instance = self.get_queryset().get(pk=snippet_id)
        serializer = self.get_serializer(instance)
        return JsonResponse({"status": "success", "data": serializer.data})

    @action(detail=False, methods=["post"], url_path="update_title")
    def update_title(self, request):
        snippet_id = request.data.get("id")
        instance = self.get_queryset().get(pk=snippet_id)
        serializer = self.get_serializer(instance=instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return JsonResponse({"status": "success", "data": serializer.data})

# 第一版
# @api_view(["GET", "POST"])
# def snippet_list(request):
#     """获取列表"""
#     snippets = Snippet.objects.all()
#     serializer = SnippetSerializer(snippets, many=True)
#     return JsonResponse({"status": "success", "data": serializer.data})
# @api_view(["GET", "POST"])
# def snippet_create(request):
#     """创建新数据"""
#     serializer = SnippetSerializer(data=request.data)
#     if serializer.is_valid():
#         serializer.save()
#         return JsonResponse({"status": "success", "data": serializer.data})
# @api_view(["GET", "POST"])
# def snippet_update(request):
#     """修改指定数据"""
#     snippet_id = request.data.get("id")
#     instance = Snippet.objects.get(pk=snippet_id)
#     serializer = SnippetSerializer(instance=instance, data=request.data, partial=True)
#     if serializer.is_valid():
#         serializer.save()
#         return JsonResponse({"status": "success", "data": serializer.data})
# @api_view(["GET", "POST"])
# def snippet_delete(request):
#     """删除指定数据"""
#     snippet_id = request.data.get("id")
#     Snippet.objects.filter(pk=snippet_id).delete()
#     return JsonResponse({"status": "success", "data": {"id": snippet_id}})





# class Snippetlist(generics.ListCreateAPIView):
#     queryset = Snippet.objects.all()
#     serializer_class = SnippetSerializer
#
# class SnippetDetail(generics.RetrieveUpdateDestroyAPIView):
#     queryset = Snippet.objects.all()
#     serializer_class = SnippetSerializer









# from django.http import HttpResponse
# from django.views.decorators.csrf import csrf_exempt
# from rest_framework.renderers import JSONRenderer
# from rest_framework.parsers import JSONParser
# from rest_framework.decorators import api_view
# from snippet.models import Snippet
# from snippet.serializers import SnippetSerializer
#
# class JSONResponse(HttpResponse):
#     """
#     An HttpResponse that renders its content into JSON.
#     """
#     def __init__(self, data, **kwargs):
#         content = JSONRenderer().render(data)
#         kwargs['content_type'] = 'application/json'
#         super(JSONResponse, self).__init__(content, **kwargs)
#
# @csrf_exempt
# @api_view(['POST'])
# def get_snippet(request):
#     """返回表中所有的数据"""
#     data = request.data
#     snippet = Snippet.objects.get(id=data["id"])
#     serializer = SnippetSerializer(snippet)
#     return JSONResponse(serializer.data)
#
# @csrf_exempt
# @api_view(['POST'])
# def update_snippet(request):
#     """update数据"""
#     snippet_id = request.data.get("id")  # 获取要修改的数据的id
#     snippet = Snippet.objects.get(pk=snippet_id)  # 从数据库查询到要修改的数据对象
#     serializer = SnippetSerializer(instance=snippet, data=request.data, partial=True) # 给序列化器传入实例和数据，parital是允许部分修改
#     if serializer.is_valid():  # 验证并保存
#         serializer.save()
#         return JSONResponse({"status": "success", "data": serializer.data})
#     return JSONResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
# @csrf_exempt
# @api_view(['POST'])
# def create_snippet(request):
#     snippet = request.data
#     serializer = SnippetSerializer(data=snippet, partial=True)
#     if serializer.is_valid():
#         serializer.save()
#         return JSONResponse({"status": "success", "data": serializer.data})
#     return JSONResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#
# @csrf_exempt
# def snippet_list(request):
#     """
#     列出所有的code snippet，或创建一个新的snippet。
#     """
#     if request.method == 'GET':
#         snippets = Snippet.objects.all()
#         serializer = SnippetSerializer(snippets, many=True)
#         return JSONResponse(serializer.data)
#
#     elif request.method == 'POST':
#         data = JSONParser().parse(request)
#         serializer = SnippetSerializer(data=data)
#         if serializer.is_valid():
#             serializer.save()
#             return JSONResponse(serializer.data, status=201)
#         return JSONResponse(serializer.errors, status=400)
#
# @csrf_exempt
# def snippet_detail(request, pk):
#     """
#     获取，更新或删除一个 code snippet。
#     """
#     try:
#         snippet = Snippet.objects.get(pk=pk)
#     except Snippet.DoesNotExist:
#         return HttpResponse(status=404)
#
#     if request.method == 'GET':
#         serializer = SnippetSerializer(snippet)
#         return JSONResponse(serializer.data)
#
#     elif request.method == 'PUT':
#         data = JSONParser().parse(request)
#         serializer = SnippetSerializer(snippet, data=data)
#         if serializer.is_valid():
#             serializer.save()
#             return JSONResponse(serializer.data)
#         return JSONResponse(serializer.errors, status=400)
#
#     elif request.method == 'DELETE':
#         snippet.delete()
#         return HttpResponse(status=204)





























from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action, permission_classes, api_view
# from rest_framework.permissions import AllowAny, IsAuthenticated
# from beifan.models import FeedBack
# from rest_framework.response import Response
# from django.contrib.auth.models import User
# from django.contrib.auth import authenticate
# from snippet.customresponse import CustomResponse
# from rest_framework.authtoken.models import Token
# # from snippet.serializers import LoginSerializer, RegisterSerializer, FeedBackAllSerializer
# from rest_framework.exceptions import ValidationError


# class SnippetViewSet(viewsets.GenericViewSet):
#     permission_classes = [AllowAny]
#     """保存数据进django的用户表中"""
#     @action(detail=False, methods=["post"], url_path="register")
#     def register(self, request):
#         serializer = RegisterSerializer(data=request.data)
#         try:
#             serializer.is_valid(raise_exception=True)
#             User.objects.create_user(
#                 username=serializer.validated_data["username"],
#                 email=serializer.validated_data["email"],
#                 password=serializer.validated_data["password"])
#             return CustomResponse(data=serializer.data, msg="success", code=status.HTTP_201_CREATED)
#         except ValidationError as e:
#             error_msg = "; ".join([f"{key}: {', '.join(val)}" for key, val in e.detail.items()])
#             return CustomResponse(data={}, msg=f"fail, {error_msg}", code=status.HTTP_400_BAD_REQUEST)
#
#
#     @action(detail=False, methods=["post"], url_path="login")
#     def login(self, request):
#         serializer = LoginSerializer(data=request.data)
#         try:
#             serializer.is_valid(raise_exception=True) # 此时验证不通过会抛出异常
#             return CustomResponse(data=serializer.data, msg="success", code=status.HTTP_200_OK)
#         except ValidationError as e:
#             error_msg = "; ".join([f"{key}: {', '.join(val)}" for key, val in e.detail.items()])
#             return CustomResponse(data={}, msg=f"fail，{error_msg}", code=e.status_code)
#
# class FeedBackAllViewSet(viewsets.GenericViewSet):
#     @action(detail=False, methods=["post"], url_path="feedbackall")
#     def feedback(self, request):
#         req = request.data
#         if "id" in req:
#             try:
#                 feedback = FeedBack.objects.get(id=req.get("id"))
#                 serializer = FeedBackAllSerializer(feedback)
#             except FeedBack.DoesNotExist:
#                 return CustomResponse(data={}, msg="feedback not found", code=status.HTTP_500_INTERNAL_SERVER_ERROR)
#         else:
#             feedbacks = FeedBack.objects.all()
#             serializer = FeedBackAllSerializer(feedbacks, many=True)
#
#         return CustomResponse(data=serializer.data, msg="success", code=status.HTTP_200_OK)
#





