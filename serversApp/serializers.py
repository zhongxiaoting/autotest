from rest_framework import serializers
from serversApp.models import Server


class ServerSerializer(serializers.ModelSerializer):
    """
    测试前提交的信息
    """
    class Meta:
        model = Server
        fields = "__all__"
