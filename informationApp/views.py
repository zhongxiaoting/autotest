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
network_port_look = 'logical name:'
getout_virb = 'logical name: virbr0'
getout_docker = 'logical name: docker0'


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
    # response_data = json.dumps(response_data)
    # print(response_data)
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


@api_view(['GET'])
def cpu_info(request):
    cpu_list = []
    cmd = 'cat /proc/cpuinfo| grep "physical id"| sort| uniq| wc -l'
    cpu_number = h.run_cmd(cmd)
    write_log('------------ The cpu physical number have %s ------------' % cpu_number['cmd_infor'])
    write_log('------------ cpu info come ------------')
    cmd = 'dmidecode -t Processor |grep -i "handle " |awk -F " " \'{print $2}\'|tr -d ","'
    handle = h.run_cmd(cmd)

    for i in handle['cmd_infor'].split("\n"):
        cpu_di = {}
        # |awk -F ":" \'{$1="";print}\'
        cmd = 'dmidecode -H %s |grep -i "Socket Designation: " ' % i
        get_cpu = h.run_cmd(cmd)
        write_log(get_cpu['cmd_infor'])
        cmd = 'dmidecode -H %s |grep -i "Manufacturer: " ' % i
        get_cpu_manufacturer = h.run_cmd(cmd)
        write_log(get_cpu_manufacturer['cmd_infor'])
        cmd = 'dmidecode -H %s |grep -i "Version: " ' % i
        get_cpu_version = h.run_cmd(cmd)
        write_log(get_cpu_version['cmd_infor'])
        cmd = 'dmidecode -H %s |grep -i "Current Speed: "' % i
        get_cpu_speed = h.run_cmd(cmd)
        write_log(get_cpu_speed['cmd_infor'])
        cmd = 'dmidecode -H %s |grep -i "Core Count: " ' % i
        get_cpu_core = h.run_cmd(cmd)
        write_log('The cpu core number is %s' % get_cpu_core['cmd_infor'])
        cmd = 'dmidecode -H %s |grep -i "Thread Count: " ' % i
        get_cpu_thread = h.run_cmd(cmd)
        write_log(get_cpu_thread['cmd_infor'])
        write_log('------------ The cpu is ok next is coming ------------')
        cpu_di['slot'] = get_cpu['cmd_infor'].split(":")[1]
        # all_memory['Mandufact'] = get_mem_mandufact['cmd_infor'].rsplit(":")
        cpu_di['manufacturer'] = get_cpu_manufacturer['cmd_infor'].split(":")[1]
        cpu_di['version'] = get_cpu_version['cmd_infor'].split(":")[1]
        cpu_di['speed'] = get_cpu_speed['cmd_infor'].split(":")[1]
        cpu_di['core'] = get_cpu_core['cmd_infor'].split(":")[1]
        cpu_list.append(cpu_di)

        response_data = {"cpu_info": cpu_list}
    return Response(response_data)


# 系统信息
@api_view(['GET'])
def system_info(request):
    system_list = []
    system_di = {}
    cmd = 'dmidecode -t bios |grep -i "Version":'
    get_bios_info = h.run_cmd(cmd)
    cmd = 'dmidecode -t bios |grep -i "Release Date":'
    get_Release_Date = h.run_cmd(cmd)
    cmd = 'dmidecode -t system |grep -i "Manufacturer:"'
    get_system_manufacturer = h.run_cmd(cmd)
    cmd = 'dmidecode -t system |grep -i "Product Name:"'
    get_system_pn = h.run_cmd(cmd)
    cmd = 'dmidecode -t system |grep -i "Serial Number:"'
    get_system_sn = h.run_cmd(cmd)
    system_di['info'] = get_bios_info['cmd_infor'].split(":")[1]
    system_di['date'] = get_Release_Date['cmd_infor'].split(":")[1]
    system_di['manufacturer'] = get_system_manufacturer['cmd_infor'].split(":")[1]
    system_di['version'] = get_system_pn['cmd_infor'].split(":")[1]
    system_di['sn'] = get_system_sn['cmd_infor'].split(":")[1]
    system_list.append(system_di)

    response_data = {"system_info": system_list}
    return Response(response_data)


# 内存信息查看
@api_view(['GET'])
def memory_info(request):
    memory_list = []
    cmd = 'dmidecode -t memory | grep -A 11 -B 5 "Size:.*GB" | grep \'Size:.*GB\' | wc -l '
    mem_number = h.run_cmd(cmd)
    write_log2('------------ The memory physical number have %s ------------' % mem_number['cmd_infor'])
    write_log2('------------ mem info come ------------')
    cmd = 'dmidecode -t 17 |grep -i "handle " |awk -F " " \'{print $2}\'|tr -d ","'
    handle = h.run_cmd(cmd)

    for i in handle['cmd_infor'].split("\n"):
        memory_dir = {}
        cmd = 'dmidecode -H %s |grep -i "Locator: "|head -n 1' % i
        get_mem = h.run_cmd(cmd)
        write_log2(get_mem['cmd_infor'])

        cmd = 'dmidecode -H %s |grep -i "Manufacturer:"' % i
        get_mem_mandufact = h.run_cmd(cmd)
        write_log2(get_mem_mandufact['cmd_infor'])
        cmd = 'dmidecode -H %s |grep -i "Speed:"|head -n 1' % i
        get_mem_speed = h.run_cmd(cmd)
        write_log2(get_mem_speed['cmd_infor'])
        cmd = 'dmidecode -H %s |grep -i "Serial Number:"' % i
        get_mem_SN = h.run_cmd(cmd)
        write_log2(get_mem_SN['cmd_infor'])
        cmd = 'dmidecode -H %s |grep -i "Part Number:"' % i
        get_mem_PN = h.run_cmd(cmd)
        write_log2(get_mem_PN['cmd_infor'])
        write_log2('------------ The memory is ok next is coming ------------')
        memory_dir['mem_slot'] = get_mem['cmd_infor'].split(":")[1]
        memory_dir['mem_manufacturer'] = get_mem_mandufact['cmd_infor'].split(":")[1]
        memory_dir['mem_speed'] = get_mem_speed['cmd_infor'].split(":")[1]
        memory_dir['mem_sn'] = get_mem_SN['cmd_infor'].split(":")[1]
        memory_dir['mem_version'] = get_mem_PN['cmd_infor'].split(":")[1]
        memory_list.append(memory_dir)
    response_data = {"memory_info": memory_list}
    return Response(response_data)


@api_view(['GET'])
def hdd_info_check(request):
    hdd_list = []
    cmd = 'lspci |grep -i "raid"'
    look_raid = h.run_cmd(cmd)

    if len(look_raid['cmd_infor']) != 0:
        # print(look_raid)
        panfu_list = []
        yingpan_list = []
        yp_info = []
        # nvme_name=[]

        cmd = '/opt/MegaRAID/MegaCli/MegaCli64 -LdPdInfo -aALL | grep "Device Id:"'
        raid_hdd_number = h.run_cmd(cmd)
        raid_hdd_number = raid_hdd_number['cmd_infor'].split('\n')

        cmd = 'ls /sys/block |grep -Ev "loop*|ram*|nvme|dm"'
        raid_hdd_name = h.run_cmd(cmd)
        raid_hdd_name = raid_hdd_name['cmd_infor'].split('\n')

        if len(raid_hdd_name) != 0:
            raid_hdd_number_count = len(raid_hdd_name)
            write_log('------------ The hdd number count is %s ------------' % raid_hdd_number_count)

            for i in raid_hdd_number:
                panfu = i.split()[2]
                panfu = int(panfu)
                panfu_list.append(panfu)
            # much=len(panfu_list)

            for i in raid_hdd_name:
                yingpan = i.split()[0]
                yingpan_list.append(yingpan)

            # for num in range(0, len(dev_info)):

            for i in range(0, len(panfu_list)):
                hdd_di = {}
                write_log("------------ This hdd is %s ------------" % yingpan_list[i])
                # cmd = "cat /var/log/messages"
                # msg_info = commands.getstatusoutput(cmd)
                cmd = 'smartctl -a -d megaraid,%d /dev/%s |grep -i "Device Model:"' % (panfu_list[i], yingpan_list[i])
                yp_info = h.run_cmd(cmd)
                write_log(yp_info['cmd_infor'])
                # sn=re.findall(r'(Serial Number:(.*))',yp_info[1])
                cmd = 'smartctl -a -d megaraid,%d /dev/%s |grep -i "Serial number:"' % (panfu_list[i], yingpan_list[i])
                hdd_sn = h.run_cmd(cmd)
                write_log(hdd_sn['cmd_infor'])
                cmd = 'smartctl -a -d megaraid,%d /dev/%s |grep -i "User Capacity:"' % (panfu_list[i], yingpan_list[i])
                get_hdd_capacity = h.run_cmd(cmd)
                write_log(get_hdd_capacity['cmd_infor'])
                write_log('------------ This hdd is ok next coming ------------')

                hdd_di['version'] = yp_info['cmd_infor'].split(":")[1]
                # hdd_di['硬盘'] = yp_firmware_version['cmd_infor'].split(":")[1]
                hdd_di['size'] = get_hdd_capacity['cmd_infor'].split(":")[1]
                hdd_di['sn'] = hdd_sn['cmd_infor'].split(":")[1]
                hdd_list.append(hdd_di)
            response_data = {"hdd_info": hdd_list}
            return Response(response_data)

        else:
            write_log("cannot find the hdd and ssd,pleace check about and check about raid what happen")

    else:
        write_log("------------ This type server is no raid ------------")
        cmd = 'ls /sys/block |grep -Ev "loop*|ram*|nvme|dm"'
        hdd_name = h.run_cmd(cmd)
        hdd_name = hdd_name['cmd_infor'].split('\n')
        if len(hdd_name) != 0:

            panduan = False
            no_raid_hdd_count = len(hdd_name)
            write_log('The hdd number count is %s' % no_raid_hdd_count)
            for i in hdd_name:
                hdd_di = {}
                write_log('------------ This hdd is %s ------------' % i)
                cmd = 'smartctl -a /dev/%s |grep -i "Device Model:"' % i
                no_raid_yp_info = h.run_cmd(cmd)
                write_log(no_raid_yp_info['cmd_infor'])
                cmd = 'smartctl -a /dev/%s |grep -i "Transport protocol:   SAS"' % i
                sas_type = h.run_cmd(cmd)
                if len(sas_type['cmd_infor']) != 0:
                    write_log(sas_type['cmd_infor'])
                else:
                    pass
                cmd = 'smartctl -a /dev/%s |grep -i "Firmware Version:"' % i
                no_raid_yp_firmware_version = h.run_cmd(cmd)
                if len(no_raid_yp_firmware_version['cmd_infor']) != 0:
                    write_log(no_raid_yp_firmware_version['cmd_infor'])
                else:
                    pass
                cmd = 'smartctl -a /dev/%s |grep -i "Serial number:"' % i
                no_raid_yp_sn = h.run_cmd(cmd)
                write_log(no_raid_yp_sn['cmd_infor'])
                cmd = 'smartctl -a /dev/%s |grep -i "User Capacity:"' % (i)
                no_raid_yp_capacity = h.run_cmd(cmd)
                write_log(no_raid_yp_capacity['cmd_infor'])
                write_log('------------ This hdd is ok next coming ------------')

                hdd_di['version'] = no_raid_yp_info['cmd_infor'].split(":")[1]
                # hdd_di['硬盘fw版本'] = no_raid_yp_firmware_version['cmd_infor'].split(":")[1]
                hdd_di['size'] = no_raid_yp_capacity['cmd_infor'].split(":")[1]
                hdd_di['sn'] = no_raid_yp_sn['cmd_infor'].split(":")[1]
                hdd_list.append(hdd_di)
            response_data = {"hdd_info": hdd_list}
            return Response(response_data)


        else:
            write_log("------------ cannot find the hdd and ssd,pleace check about ------------")


@api_view(['GET'])
def network_info_check(request):
    network_list = []
    cmd = 'lspci |grep -i "eth" |awk -F " " \'{$1 ="";print}\' | uniq |wc -l'
    cmd_network_count = h.run_cmd(cmd)
    write_log('------------ The network number is %s ------------' % cmd_network_count['cmd_infor'])
    cmd = 'lshw -class network > %s' % c.Network_info
    cmd_network_info = h.run_cmd(cmd)
    get_all_network_info = open(c.Network_info)
    read_all_network_info = get_all_network_info.read()
    read_all_network_info = read_all_network_info.split('*-network:')
    for i in read_all_network_info:
        for line in i.split('\n'):
            if re.search(network_port_look, line, re.IGNORECASE):
                if not re.search(getout_virb, line, re.IGNORECASE):
                    network_dir = {}
                    write_log(line)
                    network_product_name = re.findall(r'product: (.*)', i)[0]
                    write_log(network_product_name)
                    network_vendor = re.findall(r'vendor: (.*)', i)[0]
                    write_log(network_vendor)
                    network_speed = re.findall(r'size: (.*)', i)
                    if len(network_speed) != 0:
                        write_log(network_speed)
                        speed_network_i = network_speed
                    else:
                        pass
                    write_log("------------ next one -------------")
                    network_dir['logical_name'] = line[-9:]
                    network_dir['version'] = network_product_name
                    # print(type(network_product_name))
                    network_dir['manufacturer'] = network_vendor
                    network_dir['speed'] = speed_network_i[0]
                    network_list.append(network_dir)
    response_data = {"network_info": network_list}
    return Response(response_data)


def write_log(s):
    with open(c.MCE_ECC_LOG_PATH, 'a+') as f:
        # print(s)
        f.write(str(s) + '\n')
        f.flush()
        os.fsync(f)


def write_log2(s):
    with open(c.memory_info, 'a+') as f:
        # print(s)
        f.write(str(s) + '\n')
        f.flush()
        os.fsync(f)


def get_local_time_string():
    return time.strftime('%04Y-%m-%d %H:%M:%S', time.localtime(time.time()))
