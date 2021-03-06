# coding=utf-8
import datetime
import json
import os
import re
import sys
import time
import threading

from rest_framework.decorators import api_view

from common import constants as c, operation as on, information as fn
from utils import handle as h
from rest_framework.response import Response


@api_view(['POST'])
def run_item(request):
    on.remove_log(c.LAN_STRESS_LOG_PATH)
    # 获取前端传回的时间,将得到的时间全部转化为秒
    b_time = request.body
    run_time = json.loads(b_time).get("time")
    time_unit = run_time[-1]
    time_number = re.findall(r'\d+', run_time)
    if time_unit == 'm':
        time_seconds = int(time_number[0]) * 60
    elif time_unit == 'h':
        time_seconds = int(time_number[0]) * 3600
    else:
        time_seconds = int(time_number[0])
    start_lan_run()
    check_network_link()
    check_speed(time_seconds)
    response_data = {"lan_infor": "网卡测试完成！"}
    return Response(response_data)


# 读取网卡日志
@api_view(['GET'])
def get_lan_log(request):
    lan_result = lan_result_check()
    with open(c.LAN_STRESS_LOG_PATH, "r+") as f:
        data = f.read()

        if lan_result:
            response_data = {'lan_log': lan_result, "status": "FAIL"}
        elif "Network Stress Check Finish!" in data:
            response_data = {"lan_log": data, "status": "PASS"}
        else:
            response_data = {'lan_log': data, "status": "Checking..."}
        f.flush()
        f.close()
    return Response(response_data)


# 检查log是否错误
def lan_result_check():
    with open(c.LAN_STRESS_LOG_PATH, "r+") as f:
        data = f.read()
        error1 = re.findall("fail", data)
        error2 = re.findall("Fail", data)
        error3 = re.findall("error", data)
        error4 = re.findall("ERROR", data)
        error5 = re.findall("errors", data)
        error6 = re.findall("ERRORS", data)
        error7 = re.findall("FAIL", data)
        if error1 or error2 or error3 or error4 or error5 or error6 or error7:
            f.write("->> There are ERRORS in the project, Please check！")
            response_data = "Stress Check have ERROR, Please check progress!"
            return response_data
        f.flush()

        return


def start_lan_run():
    on.remove_log(c.LAN_STRESS_LOG_PATH)
    write_log("================= " + " Begin Lan Stress Check " + get_local_time_string() + " =================")
    lan_while = threading.Thread(target=run_lan_while)
    # lan_while.setDaemon(True)
    lan_while.start()
    time.sleep(10)
    pktgen = h.cmd_msg("cd /home/autotest/shell && ./pktgen.sh")
    write_log(pktgen)


def run_lan_while():
    h.cmd_msg("cd /home/autotest/shell && chmod +x lan_while.sh && ./lan_while.sh")
    print("lan_while.sh End!")
    return


# choose server models
def check_product_name():
    product_name_ = h.cmd_msg("ipmitool fru print | grep 'Product Name' ")
    product_name = product_name_.rsplit(":")[1]
    name = product_name.strip()
    return name


# Check whether the network cable is connected
def check_network_link():
    enps = h.cmd_msg('ls /sys/class/net | grep -E "enp[a-z0-9]+f[0-1]$"').split('\n')
    for enp in enps:
        eth_infor = h.cmd_msg("ethtool {}".format(enp))
        link_detected = re.search("Link detected: (.*)", eth_infor).group()
        link_detected = link_detected.rsplit(":")[1].strip()
        # full_speed = re.search("Speed: (.*)", eth_infor).group()
        # full_speed = full_speed.rsplit(":")[1].strip()
        # full_speed = re.search(r"\d+", full_speed).group()
        if link_detected == 'yes':
            write_log("->>> {} is link! Formal ".format(enp))
        else:
            write_log("->>> {} is not link! ERROR ".format(enp))
            h.stress_fail()
    return link_detected


def check_speed(run_seconds):
    count = 1
    # duration_time = 50
    day_time = datetime.datetime.now() + datetime.timedelta(seconds=run_seconds)
    day_time = day_time.strftime("%Y-%m-%d %H:%M:%S")
    enps = h.cmd_msg('ls /sys/class/net | grep -E "enp[a-z0-9]+f[0-1]$"').split('\n')
    time.sleep(5)
    while True:
        now_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        out = fn.get_pid_lan()
        if day_time <= now_time:
            break
        time.sleep(c.WAIT_LAN_SPEED_TIME)
        write_log("=============== NO." + str(
            count) + " Begin Network Speech Check  " + get_local_time_string() + " =================")
        for enp in enps:
            eth_infor = h.cmd_msg("ethtool {}".format(enp))
            full_speed = re.search("Speed: (.*)", eth_infor).group()
            full_speed = full_speed.rsplit(":")[1].strip()
            aa = 1
            while aa:
                enp_result = h.cmd_msg("cat /proc/net/pktgen/" + enp)
                result1 = re.search("OK", enp_result)
                if result1 is None:
                    time.sleep(3)
                else:
                    aa = 0
            result = enp_result.split('\n')[-1]
            true_speed = result.split()[1]
            speed_ = re.search(r"\d+", true_speed)
            speed = speed_.group()
            errors = result.split()[-1]

            if full_speed == "1000Mb/s":
                if int(speed) > 0:
                    write_log("->>> {} speed is {}Mb/s, Formal!".format(enp, speed))
                    if int(errors) != 0:
                        write_log("->>> {} have {} errors !".format(enp, errors))
                        h.stress_fail()
                else:
                    write_log("->>> {} speed is {}Mb/s, not up to the mark! ERROR".format(enp, speed))
                    h.stress_fail()
            elif full_speed == "10000Mb/s":
                if int(speed) > 0:
                    write_log("->>> {} speed is {}Mb/s, Formal!".format(enp, speed))
                    if int(errors) != 0:
                        write_log("->>> {} have {} errors !".format(enp, errors))
                        h.stress_fail()
                else:
                    write_log("->>> {} speed is {}Mb/s, not up to the mark! ERROR".format(enp, speed))
                    h.stress_fail()
            elif full_speed == "25000Mb/s":
                if int(speed) > 0:
                    write_log("->>> {} speed is {}Mb/s, Formal!".format(enp, speed))
                    if int(errors) != 0:
                        write_log("->>> {} have {} errors !".format(enp, errors))
                        h.stress_fail()
                else:
                    write_log("->>> {} speed is {}Mb/s, not up to the mark! ERROR".format(enp, speed))
                    h.stress_fail()
            else:
                write_log("->>> {} speed is {},not achieved!".format(enp, full_speed))
        write_log(
            "================================== NO." + str(count) + " End  ==================================")
        count += 1
    h.lan_formal_quit()
    write_log("--->>> Network Stress Check Finish! ")
    return


def write_log(s):
    with open(c.LAN_STRESS_LOG_PATH, 'a+') as f:
        print(s)
        f.write(str(s) + '\n')
        f.flush()
        os.fsync(f)

def get_local_time_string():
    return time.strftime('%04Y-%m-%d %H:%M:%S', time.localtime(time.time()))


