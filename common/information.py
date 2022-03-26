# coding=utf-8
import subprocess
import time

from utils import handle as h
from serversApp.models import Server


# CPU的使用率
def get_current_cpu_use():
    out = h.run_cmd("cat /proc/stat|head -n 1")
    l = out.split()
    user = int(l[1])
    nice = int(l[2])
    sys = int(l[3])
    idle = int(l[4])
    current_cpu_use = (user + sys) / (user + nice + sys + idle)
    return current_cpu_use


# 获取线程数
def get_thread_num():
    core_num = h.run_cmd("cat /proc/cpuinfo | grep -c processor")
    free_cpu = 1 - get_current_cpu_use()
    thread_num = int(free_cpu * (int(core_num) - 1))
    return thread_num


# 获取当前的执行进程
def get_pid(cmd):
    statusoutput = subprocess.getstatusoutput(cmd)
    # 进程正在执行,进程执行结束
    if statusoutput[0] == 0 or statusoutput[0] == 1:
        return statusoutput[1]
    return


# get free memory
def get_mem(self):
    out = self.run_cmd("free -m|grep Mem")
    mem = out.split()[3]
    # print(mem)
    return int(mem) - 10240


# 硬盘测试是否已经停止
def get_pid_hdd():
    out = subprocess.getstatusoutput("pidof fio")
    return out
