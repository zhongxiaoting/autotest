# coding=utf-8

# define run cmd in system
import subprocess
import sys
import time

from utils import log as l


def get_local_time_string():
    return time.strftime('%04Y-%m-%d %H:%M:%S', time.localtime(time.time()))


# 基本信息检查结果错误
def result_fail(name):
    infor = l.fail_msg(name + " test Fail, Please check progress!")
    response_data = {"infor": infor, "status": "FAIL"}
    return response_data


# 压力测试结果错误
def stress_fail(name):
    infor = name + " Check Fail !"
    subprocess.run("pkill -9 memtester", shell=True)
    subprocess.run("pkill -9 fio", shell=True)
    subprocess.run("pkill -9 stress", shell=True)
    subprocess.run("pkill -9 lan_while.sh", shell=True)
    response_data = {"cmd_infor": infor}
    return response_data


# 压测cmd, 实时输出信息
def cmd_stress(cmd):
    out = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    cmd_infor = out.stdout.read().decode("utf-8")
    # 127 shell命令错误，0命令正确，1命令正确但是没有输出
    cmd_msg = {"command": cmd, "cmd_infor": cmd_infor}
    return cmd_msg


def run_cmd(cmd):
    statusoutput = subprocess.getstatusoutput(cmd)
    # 命令执行成功，有返回值或者没有返回值
    if statusoutput[0] == 0 or statusoutput[0] == 1:
        cmd_msg = {"comand": cmd, "cmd_infor": statusoutput[1]}
    # 命令执行失败
    else:
        cmd_msg = {"command": cmd + " Fail", "cmd_infor": statusoutput[1]}
    return cmd_msg


def cmd_msg(cmd):
    statusoutput = subprocess.getstatusoutput(cmd)
    # 命令执行成功，有返回值或者没有返回值
    if statusoutput[0] == 0 or statusoutput[0] == 1:
        cmd_msg = statusoutput[1]
    # 命令执行失败
    else:
        cmd_msg = "command: " + cmd + " Fail, " + statusoutput[1]
    return cmd_msg


# 正常停止lan测试
def lan_formal_quit():
    subprocess.getstatusoutput("pkill -9 lan_while.sh")
    return


# 测试出现错误，停止测试
def run_fail():
    sys.exit(0)
    return
