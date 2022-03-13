# coding=utf-8

from django.shortcuts import render
from rest_framework import status

from rest_framework.decorators import api_view
from rest_framework.response import Response

from serversApp.serializers import ServerSerializer
from serversApp.models import Server

# Create your views here.


@api_view(['POST'])
def create_server(request):
    """
    添加服务器信息
    :param request:
    :return: add data
    """
    serializers = ServerSerializer(data=request.data)
    sn = request.data.get("sn")
    if len(sn) < 6:
        response_data = {"errors": "The serial number is too short. Please re-enter SN!"}
        return Response(response_data, status=status.HTTP_403_FORBIDDEN)
    if serializers.is_valid():
        serializers.save()
        response_data = {"summit": "summit formal!", "status": "PASS"}
    return Response(response_data, status=status.HTTP_201_CREATED)


