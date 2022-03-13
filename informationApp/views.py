# coding=utf-8

from django.shortcuts import render
import os
import re
import sys
import time
import json
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from common import constants as c
from utils import handle as h
# Create your views here.

"""
ECC Check and MCE Check
"""


CMD_GET_CPU_MCE = 'ras-mc-ctl --summary'

# CPU MCE检测
@api_view(['GET'])
def cpu_mce_check(request):
    cpu_mec_display = h.run_cmd(CMD_GET_CPU_MCE)
    write_log("=============  CPU MCE Check Begin  " + get_local_time_string() + " ================")
    write_log(cpu_mec_display)
    write_log("==============  CPU MCE Check End  " + get_local_time_string() + " =================")
    cpu_mce_errors(cpu_mec_display['cmd_infor'])
    response_data = {"cpu_mec": cpu_mec_display, "status": "PASS"}
    # response_data1 = data.append(response_data)
    response_data = json.dumps(response_data)
    print(response_data)
    return Response(response_data, status=status.HTTP_200_OK)


# 内存ECC检测
@api_view(['GET'])
def mem_ecc_check(request):
    ecc_clear = h.run_cmd("ipmitool sel clear")
    ecc_infor = h.run_cmd("ipmitool sel list")
    write_log("=============  MEM ECC Check Begin  " + get_local_time_string() + " ================")
    write_log(ecc_infor)
    write_log("==============  MEM ECC Check End  " + get_local_time_string() + " =================")
    if "ECC" in ecc_infor:
        write_log("->>> MEM ECC Fail")
        h.result_fail("MEM ECC")
        return
    write_log("->>> MEM ECC PASS ")
    response_data = {"mem_ecc": ecc_infor, "status": "PASS"}
    response_data = json.dumps(response_data)
    # print(response_data)
    return Response(response_data, status=status.HTTP_200_OK)


# CPU MCE 检测出现错误
def cpu_mce_errors(mce_errors):
    temp = mce_errors.split('\n')
    for mce in temp:
        if mce == '':
            continue
        result = re.match("No", mce)
        if not result:
            errors_information = h.run_cmd("ras-mc-ctl --errors")
            write_log("============  CPU MCE ERROR Check Begin " + get_local_time_string() + " ==============")
            write_log(errors_information)
            write_log("==============  CPU MCE ERROR Check End " + get_local_time_string() + " ================")
            write_log("->>> MCE ERROR ")
            response_data = {"mce_error": errors_information, "status": "FAIL"}
            return Response(json.dumps(response_data), status=status.HTTP_403_FORBIDDEN)
    write_log("->>> CPU MCE PASS ")
    return


def write_log(s):
    with open(c.MCE_ECC_LOG_PATH, 'a+') as f:
        # print(s)
        f.write(str(s) + '\n')
        f.flush()
        os.fsync(f)


def get_local_time_string():
    return time.strftime('%04Y-%m-%d %H:%M:%S', time.localtime(time.time()))
