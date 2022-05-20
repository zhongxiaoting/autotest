# coding=utf-8



# 检查进程
import os.path
import subprocess


def check_mem_pid():
    statusoutput = subprocess.getstatusoutput("pidof memtester")
    if statusoutput[0] == 1:
        return None
    else:
        return statusoutput[1]

def remove_log(path):
    if os.path.exists(path):
        os.remove(path)
    return


