# coding=utf-8

# define run cmd in system
import subprocess
import sys
import time

from django.core.serializers import json
from rest_framework import status
from rest_framework.response import Response
from rest_framework.status import HTTP_403_FORBIDDEN


from utils import log as l
from main import controller as ctr


def get_local_time_string():
    return time.strftime('%04Y-%m-%d %H:%M:%S', time.localtime(time.time()))


# 基本信息检查结果错误
def result_fail(name):
    infor = l.fail_msg(name + " test Fail, Please check progress!")
    response_data = {"infor": infor, "status": "FAIL"}
    return response_data


# 压力测试结果错误
def stress_fail(name):
    infor = l.fail_msg(name + " Check Fail !")
    subprocess.run("pkill -9 memtester", shell=True)
    subprocess.run("pkill -9 fio", shell=True)
    subprocess.run("pkill -9 stress", shell=True)
    subprocess.run("pkill -9 lan_while.sh", shell=True)
    subprocess.run("pkill -9 python", shell=True)
    response_data = {"name": infor, "status": "FAIL"}
    return response_data


# def run_command(cmd):
#     output = subprocess.run(cmd, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
    # 命令执行成功，有返回值或者没有返回值
    # if output.returncode == 0 or output[0] == 1:
    #     cmd_msg = {"cmd_formal": "command: " + output.args, "cmd_infor": output}
    #     return Response(cmd_msg, status=status.HTTP_201_CREATED)
    # # 命令执行失败
    # else:
    #     cmd_msg = {"cmd_error": "command:" + cmd + "Fail", "cmd_infor": statusoutput[1]}
    #     return Response(cmd_msg, status=status.HTTP_403_FORBIDDEN)

# 压测cmd, 实时输出信息
def cmd_stress(cmd):
    out = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    pid = out.wait()
    # 127 shell命令错误，0命令正确，1命令正确但是没有输出
    if pid == 127:
        cmd_error = out.stdout.read()
        cmd_msg = {"cmd_error": "command: " + cmd, "cmd_infor": cmd_error, "status": "FAIL"}
        response_data = json.dumps(cmd_msg)
        return Response(response_data)
    while True:
        line = out.stdout.readline()
        if line != None:
            infor = {"cmd_formal": "command: " + cmd, "cmd_infor": line}
        if not line:
            break
        return infor


def run_cmd(cmd):
    statusoutput = subprocess.getstatusoutput(cmd)
    # 命令执行成功，有返回值或者没有返回值
    if statusoutput[0] == 0 or statusoutput[0] == 1:
        cmd_msg = {"cmd_formal": "command: " + cmd, "cmd_infor": statusoutput[1]}

    # 命令执行失败
    else:
        cmd_msg = {"cmd_error": "command:" + cmd + " Fail", "cmd_infor": statusoutput[1]}
    return cmd_msg
