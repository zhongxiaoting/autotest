# coding=utf-8
import json
import subprocess

from django.shortcuts import render
import os
import sys
import threading
import time

from dwebsocket.decorators import accept_websocket,require_websocket
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from common import constants as c
from common import information as fn
from utils import handle as h


# Create your views here.

def top_log():
    maxTimes = c.RUN_SECONDS / 10
    h.run_cmd("setsid timeout {} top -d 10 -n {} -b -i >> {}".format(c.RUN_SECONDS, maxTimes, c.CPU_STRESS_LOG_PATH))


@api_view(['GET'])
def stress_check():
    thread_num = fn.get_thread_num()
    cmd = "stress -c {} -t {} >>{}".format(thread_num, c.RUN_SECONDS, c.CPU_STRESS_LOG_PATH)
    write_log("=============  CPU Stress Check Begin  " + get_local_time_string() + " ================")
    out = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    pid = out.wait()
    # 127 shell命令错误，0命令正确，1命令正确但是没有输出
    if pid == 127:
        cmd_error = out.stdout.read()
        cmd_msg = {"cmd_error": "command: " + cmd, "cmd_infor": cmd_error, "status": "FAIL"}
        response_data = json.dumps(cmd_msg)
        return Response(response_data)
    t = threading.Thread(target=top_log)
    t.setDaemon(True)
    t.start()
    while True:
        line = out.stdout.readline()
        if line != None:
            infor = {"cmd_infor": line}
        if not line:
            break
        write_log(line)
        response_data = json.dumps(infor)
        return Response(response_data)
    write_log("==============  CPU Stress Check End  " + get_local_time_string() + " =================")
    # 检查log日志中是否成功
    with open(c.CPU_STRESS_LOG_PATH, 'r') as f:
        out = f.read()
        if "successful run completed" in out:
            response_data = {"status": "PASS"}
        else:
            response_data = h.stress_fail("CPU Stress")
    response_data = json.dumps(response_data)
    return Response(response_data, status=status.HTTP_200_OK)


def write_log(s):
    with open(c.CPU_STRESS_LOG_PATH, 'a+') as f:
        print(s)
        f.write(str(s) + '\n')
        f.flush()
        os.fsync(f)


def get_local_time_string():
    return time.strftime('%04Y-%m-%d %H:%M:%S', time.localtime(time.time()))




