# coding=utf-8



# 检查进程
import subprocess


def check_mem_pid():
    statusoutput = subprocess.getstatusoutput("pidof memtester")
    if statusoutput[0] == 1:
        return None
    else:
        return statusoutput[1]

