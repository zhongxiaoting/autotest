
from django.contrib.auth import authenticate, login, logout
# Create your views here.

# 登录功能实现
from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(['POST'])
def user_login(request):
    # 从请求中获取用户名、密码
    username = request.data.get("username")
    password = request.data.get("password")
    # print(username, password)
    user = authenticate(username=username, password=password)
    if user is not None:
        # login方法登录
        login(request, user)
        # 返回登录成功信息
        response_data = {"message": "登陆成功", "status": "true"}
    else:
        # 返回登录失败信息
        response_data = {"message": "登陆失败", "status": "false"}
    return Response(response_data)


@api_view(['POST'])
def user_logout(request):
    logout(request)
    response_data = {"message": "注销用户成功"}
    return Response(response_data)