# coding=utf-8
import os
import subprocess

from rest_framework import status

from rest_framework.decorators import api_view
from rest_framework.response import Response

# from common.constants import make_sn_log, make_date_log
from serversApp.models import Servers
from serversApp.serializers import ServerSerializer
from serversApp.models import SubmitLog
from .fastdfs import *
from common import constants
from common import operation as on
# Create your views here.


@api_view(['POST'])
def create_server(request):
    """
    添加服务器信息
    :param request:
    :return: add data
    """
    subprocess.getstatusoutput("rm -rf /home/autotest/log/*")
    serializers = ServerSerializer(data=request.data)
    sn = request.data.get("sn")
    if len(sn) < 6:
        response_data = {"errors": "The serial number is too short. Please re-enter SN!", "status": "fail"}
        return Response(response_data, status=status.HTTP_403_FORBIDDEN)
    if serializers.is_valid():
        serializers.save()
        # check log dir
        subprocess.getstatusoutput("mkdir /home/autotest/log/" + str(sn))
        print("success")
        response_data = {"summit": "summit formal!", "status": "true"}
    return Response(response_data, status=status.HTTP_201_CREATED)


# 导入封装类，日志文件上传
@api_view(["POST"])
def upload(request):
    sn = str(Servers.objects.order_by("-submission_date")[0])
    cmd = "mv /home/autotest/log/*.log /home/autotest/log/{}".format(sn)
    subprocess.getstatusoutput(cmd)
    # print(Servers.objects.get(sn=sn))
    sn_path = "/home/autotest/log"
    on.remove_log(sn_path + "/" + sn + ".zip")
    cmd = "cd {0} && zip -r {1}.zip {2}".format(sn_path, sn, sn)
    log_zip = subprocess.getstatusoutput(cmd)
    file_zip = sn_path + "/" + sn + ".zip"
    file_fast = FastDfsStroage()
    # 检查文件是否存在
    # if file_fast.exists(file_zip):
    #     print(111)
    #     file_fast.delete(file_zip)
    # 存入远程服务器
    ret = file_fast._save(file_zip)
    # 返回存入图片的url
    url = file_fast.url(ret)
    print(url)
    url = url + "?filename=" + sn + ".zip"
    # url保存到数据库中
    if url:
        sava_data = SubmitLog()
        sava_data.server = Servers.objects.get(sn=sn)
        sava_data.file_path = url
        sava_data.save()
        print("保存成功")
        response_data = {"url": url, "mes": "upload success", "status": "true"}
    else:
        response_data = {"mes": "upload fail", "status": "false"}
    return Response(response_data)


"""
# 日志下载功能
@api_view(['GET'])
def download(request):
    path = "http://192.168.33.3:8888/group1/M00/00/00/wKghA2J7lj-ABU0sAAKICOBXArA401.zip"
    if not os.path.exists(path):
        raise IOError("File not find!")
    response = FileResponse(path)
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment;filename="123.txt"'
    return response
"""