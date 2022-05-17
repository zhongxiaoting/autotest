from rest_framework import serializers
from serversApp.models import Servers, SubmitLog


class ServerSerializer(serializers.ModelSerializer):
    """
    测试前提交的信息
    """

    class Meta:
        model = Servers
        fields = "__all__"


class SubmitLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubmitLog
        fields = "__all__"
