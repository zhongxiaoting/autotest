# coding=utf-8
import json
import multiprocessing
import re
import subprocess

import os
import threading
import time

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from common import constants as c
from common import information as fn, operation as op
from utils import handle as h
from stressApp import disk as dk


# Create your views here.

def top_log():
    maxTimes = c.RUN_SECONDS / 10
    h.run_cmd("setsid timeout {} top -d 10 -n {} -b -i >> {}".format(c.RUN_SECONDS, maxTimes, c.CPU_STRESS_LOG_PATH))


@api_view(['POST'])
def stress_check(request):
    subprocess.getstatusoutput("rm -rf " + c.CPU_STRESS_LOG_PATH)
    b_time = request.body
    run_time = json.loads(b_time).get("time")
    thread_num = fn.get_thread_num()
    shell = "./tools/stress -c {} -t {} ".format(thread_num, run_time)
    cpu_write_log("=============  CPU Stress Check Begin  " + get_local_time_string() + " ================")
    cpu_infor = h.cmd_stress(shell)
    t = threading.Thread(target=top_log)
    t.setDaemon(True)
    t.start()
    cpu_write_log(cpu_infor)
    cpu_write_log("==============  CPU Stress Check End  " + get_local_time_string() + " =================")
    # check errors
    if "successful run completed" in cpu_infor["cmd_infor"]:
        cpu_write_log("->>> CPU Check PASS ")
        response_data = {"cpu_stress": cpu_infor, "status": "PASS"}
    else:
        cpu_write_log("->>> CPU Check Fail ")
        cpu_error = h.stress_fail("CPU Stress")
        cpu_error["cpu_fail"] = cpu_infor
        response_data = {"cpu_stress": cpu_error, "status": "FAIL"}
    return Response(response_data)


@api_view(['POST'])
def run_mem_check(request):
    subprocess.getstatusoutput("rm -rf " + c.MEM_STRESS_LOG_PATH)
    b_time = request.body
    run_time = json.loads(b_time).get("time")
    mem = int(fn.get_mem() * 0.8)
    shell = "timeout {} ./tools/memtester {} 1".format(run_time, mem)
    mem_write_log("=============  MEM Stress Check Begin  " + get_local_time_string() + " ================")
    mem_infor = subprocess.getoutput(shell)
    rep = {'\x2d': '', '\x08': '', '\x5c': '', '\x7c': '', '\x2f\x08': ''}
    rep = dict((re.escape(k), v) for k, v in rep.items())
    patternByte = re.compile("|".join(rep.keys()))
    outByte = patternByte.sub(lambda m: rep[re.escape(m.group(0))], mem_infor)
    ret = re.sub("\s*setting\s*\d*\s*|\s*testing\s*\d*\s*", "", outByte)
    mem_write_log(ret)
    mem_write_log("\n" + "==============  MEM Stress Check End  " + get_local_time_string() + " =================")
    with open(c.MEM_STRESS_LOG_PATH, "r") as f:
        data = f.read()
        if "fail" in data or "error" in data or "timeout" in data:
            response_data = {"mem_stress": ret, "status": "FAIL"}
        else:
            response_data = {"mem_stress": ret, "status": "PASS"}
    return Response(response_data)


@api_view(['POST'])
def run_hdd_check(request):
    subprocess.getstatusoutput("rm -rf " + c.HDD_STRESS_LOG_PATH + "/disk*.log")
    b_time = request.body
    value = json.loads(b_time).get("time")
    make_up_raid()
    i = 0
    all_data_disks = dk.remove_os_disk()
    os_disk = dk.get_os_disk()
    disk_write_log0("->>> System Disk is : " + os_disk)
    disk_write_log0("->>> Tatol Non-system Disks: " + str(len(all_data_disks)))
    disk_write_log0("->>> Non-system Disks is : ")
    disk_write_log0(all_data_disks)
    for data_disk in all_data_disks:
        data_disk_t = threading.Thread(target=random_read_write, args=(data_disk, str(i), value))
        data_disk_t.setDaemon(True)
        data_disk_t.start()
        i += 1
    # response_data = {"hdd_waiting": "硬盘正在测试中......", "status": "PASS"}
    response_data = get_hdd_log()
    return Response(response_data)


@api_view(['GET'])
def stop_stress(request):
    subprocess.run("pkill -9 memtester", shell=True)
    subprocess.run("pkill -9 fio", shell=True)
    subprocess.run("pkill -9 stress", shell=True)
    subprocess.run("pkill -9 lan_while.sh", shell=True)
    response_data = {"cmd_infor": "Stress Test is interrupted", "status": "FAIL"}
    return Response(response_data)


def get_hdd_log():
    time.sleep(c.RUN_SECONDS + 10)
    out = fn.get_pid_hdd()
    if out[0] == 1 and out[1] == '':
        read_and_write_hdd_log()
        hdd_result = hdd_result_check()
        if hdd_result:
            response_data = {'hdd_log': hdd_result, "status": "FAIL"}
        else:
            f = open(c.ALL_DISKS_LOG_PATH, "r")
            response_data = {"hdd_log": f.read(), "status": "PASS"}
            f.close()
    return response_data


# 检查log是否错误
def hdd_result_check():
    with open(c.ALL_DISKS_LOG_PATH, "a+") as f:
        data = f.read()
        error1 = re.findall("fail", data)
        error2 = re.findall("Fail", data)
        error3 = re.findall("error", data)
        error4 = re.findall("ERROR", data)
        error5 = re.findall("FAIL", data)
        if error1 or error2 or error3 or error4 or error5:
            f.write("->> There are ERRORS in the project, Please check！")
            response_data = "HDD Stress Check have ERROR, Please check progress!"
            return response_data
        f.flush()
        f.close()
        return


# 是否要组Raid卡
def make_up_raid():
    disk_write_log0("=========== Disks Read and Write Check  " + get_local_time_string() + " ===============" + "\n")
    raid_or_not = h.run_cmd('lspci | grep "RAID" ')
    if "Fail" in raid_or_not['comand']:
        disk_write_log0("->>> No Raid")
    else:
        disk_write_log0("===================== Building Raid ============================")
        raid = subprocess.getstatusoutput("cd shell && sh ./makeraid0.sh")
        disk_write_log0("============== Build Raid Success, Information ==================")
        disk_write_log0(raid[1])
        disk_write_log0("==================================================================")
    return


# 对每一个非系统盘进行读写测试
def random_read_write(data_disk, i, run_time):
    if int(i) == 0:
        pass
    disk_write_log("========= Data Disk NO." + i + " Read And Write Begin  " + get_local_time_string() + " ==========",
                   i)

    shell = "fio -filename={} -direct=1 -iodepth 1" \
            " -thread -rw=randrw -ioengine=psync -bs=16k" \
            " -size=1G -numjobs=10 -runtime={} -group_reporting -time_based" \
            " -name=mytest_{}".format(data_disk, run_time, i)
    hdd_infor = subprocess.getstatusoutput(shell)
    disk_write_log(hdd_infor[1], i)
    disk_write_log("================== Data disk NO." + i + " End ====================", i)
    return hdd_infor


# 对系统盘进行读测试
def random_read():
    os_disk = dk.get_os_disk()
    h.run_cmd("mkdir /test")
    shell = "fio -directory=/test -direct=1 -iodepth 1" \
            " -thread -rw=randread -ioengine=psync -bs=16k -size=1G" \
            " -numjobs=10 -runtime=60 -group_reporting -name=mytest_0"
    disk_write_log("============ System Disk Read Begin  " + get_local_time_string() + " ==============")
    disk_write_log("The Command Line->>> " + shell + "\n")
    os_disk_read = subprocess.getstatusoutput(shell)
    disk_write_log(os_disk_read[1])
    disk_write_log("==============  System Disk Read End  " + get_local_time_string() + " =================")
    return os_disk_read


# 读取硬盘的log
def read_and_write_hdd_log():
    data_disks = dk.remove_os_disk()
    len_disks = len(data_disks)
    for i in range(len_disks):
        with open(c.HDD_STRESS_LOG_PATH + "/disk" + str(i) + '.log', "r") as f:
            hdd_data = f.read()
        write_disks_log(str(hdd_data) + '\n')
    return hdd_data


# cpu log
def cpu_write_log(s):
    with open(c.CPU_STRESS_LOG_PATH, 'a+') as f:
        print(s)
        f.write(str(s) + '\n')
        f.flush()
        os.fsync(f)


# memory log
def mem_write_log(s):
    with open(c.MEM_STRESS_LOG_PATH, 'a+') as f:
        print(s)
        f.write(str(s) + '\n')
        f.flush()
        os.fsync(f)


# disk0 log
def disk_write_log0(s):
    with open(c.HDD_STRESS_LOG_PATH + '/disk0.log', 'a+') as f:
        print(s)
        f.write(str(s) + '\n')
        f.flush()
        os.fsync(f)


# disk_i log
def disk_write_log(s, i):
    with open(c.HDD_STRESS_LOG_PATH + "/disk" + i + '.log', 'a+') as f:
        print(s)
        f.write(str(s) + '\n')
        f.flush()
        os.fsync(f)


# disk all log
def write_disks_log(s):
    subprocess.getstatusoutput("rm -rf" + c.ALL_DISKS_LOG_PATH)
    with open(c.ALL_DISKS_LOG_PATH, 'a+') as f:
        f.write(str(s) + '\n')
        f.flush()
        os.fsync(f)


def get_local_time_string():
    return time.strftime('%04Y-%m-%d %H:%M:%S', time.localtime(time.time()))

#######################################################
# 网卡测试
#######################################################
