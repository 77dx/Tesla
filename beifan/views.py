from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect, HttpResponseNotFound
from django.http.request import HttpRequest
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User, Group
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework import viewsets
from .serializers import FeedBackSerializer, UserSerializer
import datetime
from .models import FeedBack
import json
import re


# 给大模型调用的接口，将二维数组的数据写进excel
@api_view(['POST'])
def write_excel(request):
    req = json.loads(request.body)
    print(req)
    with open("case_excel.xlsx", "w") as f:
        ...

# rest_framework的接口
# @action(method=['POST'], detail=True)
@api_view(['POST'])
@permission_classes([AllowAny])   # 允许所有人访问，无需认证
def token_login(request):
    # permission_classes = [AllowAny]  # 允许所有人访问，无需认证,与装饰器作用一样
    req = json.loads(request.body)
    # req = request.case_data
    username = req.get("username")
    password = req.get("password")

    user = authenticate(username=username, password=password)

    response_json = {
        "code": 0,
        "msg": "success",
        "case_data": None
    }

    if user is not None:
        if user.is_active:
            token, created = Token.objects.get_or_create(user=user)
            response_json["case_data"] = {
                'token': token.key,
                'user_id': user.pk,
            }
            return Response(response_json)
        else:
            response_json["code"] = -1
            response_json["msg"] = "fail"
            response_json["case_data"] = "error User account is disabled"
            return Response(response_json, status=status.HTTP_401_UNAUTHORIZED)
    else:
        response_json["code"] = -1
        response_json["msg"] = "fail"
        response_json["case_data"] = "error Unable to log in with provided credentials."
        return Response(response_json, status=status.HTTP_401_UNAUTHORIZED)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class FeedBackViewsSet(viewsets.ModelViewSet):
    queryset = FeedBack.objects.all()   # 数据来源
    serializer_class = FeedBackSerializer   # 数据格式


@require_http_methods(["POST"])
def my_login(request):
    req = json.loads(request.body)
    res = {
        "code": 0,
        "msg": "success",
        "case_data": None
    }
    # authenticate()和login()的区别：auth是检查用户证书，若正确返回一个User对象；login则在当前会话中设置用户。
    user = authenticate(request, username=req.get("username"), password=req.get("password"))
    if user is not None:
        if user.is_active:
            msg = login(request, user)
            res["msg"] = msg
        else:
            res["msg"] = "Disabled account"
    else:
        res["msg"] = "invalid login"

    return JsonResponse(res)




@csrf_exempt
@require_http_methods(["POST"])
def register(request):
    req = json.loads(request.body)
    res = {
        "code": 0,
        "msg": "success",
        "case_data": None
    }
    # 判断所有字段不能为空
    params = []
    for key, value in req.items():
        if not value:
            params.append(key)
    if params:
        res["msg"] = f"{params} 不能为空！"
        return JsonResponse(res)

    # 判断用户名是否重复
    username = req.get("username")
    filter_user = User.objects.filter(username=username)
    if filter_user:
        res["msg"] = "用户名不能重复！"
        return JsonResponse(res)

    # 检验密码长度不能小于6
    password = req.get("password")
    password_confirm = req.get("password_confirm")
    if len(password) < 6:
        res["msg"] = "密码长度不能小于6位！"
        return JsonResponse(res)

    # 检验两次密码一致
    if password != password_confirm:
        res["msg"] = "两次密码输入不一致！"
        return JsonResponse(res)

    # 检验邮箱格式，非专业
    email = req.get("email")
    pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    if not re.match(pattern, email):
        res["msg"] = "邮箱格式不正确！"
        return JsonResponse(res)

    # 保存Django用户表和用户授权
    new_user = User.objects.create_user(username, email, password, is_staff=1)
    new_user.save()
    beifan_group = Group.objects.get(name="beifan")
    new_user.groups.add(beifan_group)

    # 注册成功跳转登陆页
    res["msg"] = "注册成功"
    return JsonResponse(res)


def index(request):
    # latest_question_list = Question.objects.order_by("-pub_date")[:5]
    # context = {"latest_question_list": latest_question_list}
    # return render(request, "polls/index.html", context)
    return render(request, "beifan/index.html")

async def current_datetime(request):
    now = datetime.datetime.now()
    html = f"<html><body>It is now {now} </body></html>"
    return HttpResponse(html)

from django.views.decorators.http import require_http_methods
@require_http_methods(["GET", "POST"])

def my_view(request):
    # 查看权限
    # content_type = ContentType.objects.get_for_model(
    #    FeedBack, for_concrete_model=False
    # )
    # user_per = Permission.objects.filter(content_type=content_type)
    # for p in user_per:
    #     print(p.codename)
    user_id = request.user.id
    if FeedBack.objects.filter(user_id=user_id):
        return HttpResponse("该用户已经评论过了")
    return HttpResponse("<h1>It is my view</h1>")

    # return HttpResponseNotFound("<h1> Page not found </h1>")
    # from django.http import Http404
    # num = "2.5"
    # try:
    #     num = int(num)
    # except Exception:
    #     raise Http404("Poll does not exist")
    #
    # return HttpResponse(num)


def hello(request: HttpRequest):
    name = request.GET.get("name") or "world"
    return HttpResponse(f"Hello, {name}!")
    # return redirect("/beifan/my_view")

    # return redirect("my_view", foo="views.my_view")


    # obj = "http://www.baidu.com"
    # return redirect(obj)

    # context = {
    #     "method": f"{request.method}",
    #     "path": f"{request.path}",
    #     "headers": f"{request.headers}",
    #     "get": f"{dict(request.GET)}",
    #     "post": f"{request.POST}",
    #     # "body": f"{request.body}"
    # }
    # print(request.GET)
    # print(request.POST["commodity"])
    # return HttpResponse(json.dumps(context))
    # return HttpResponseRedirect("http://www.baidu.com")

@login_required
def rating(request):
    # 判断用户是否已经评论过
    user_id = request.user.id
    if FeedBack.objects.filter(user_id=user_id):
        data = {
            "code": 9999,
            "msg": "已经评论过了！",
            "case_data": None
        }
        return JsonResponse(data)

    req = json.loads(request.body)
    quality = req.get("quality")
    attitude = req.get("attitude")
    speed = req.get("speed")
    text = req.get("text")
    anonymous = req.get("anonymous")

    # 把数据保存进数据库
    obj = FeedBack()
    obj.quality = quality
    obj.attitude = attitude
    obj.speed = speed
    obj.text = text
    obj.anonymous = anonymous
    obj.user_id = request.user.id
    obj.save()

    # for p in FeedBack.objects.raw("select * from feedback"):
    #     print(p)

    data = {
        "code": 0,
        "msg": "ok",
        "case_data": {
            "quality": quality,
            "attitude": attitude,
            "speed": speed,
            "text": text,
            "anonymous": anonymous,
        }

    }
    return JsonResponse(data)



# 对于settings文件的应用示例
# 如果直接导入settings文件，会有3个问题：1. settings文件可能不存在；
# 2. settings有的设置不存在；3. 第三方库会改变定义方式，导致访问失败。

from django.conf import settings

if __name__ == '__main__':
    if settings.DEBUG:
        ...


