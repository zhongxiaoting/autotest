import json

from django.shortcuts import render

from utils import handle as h
# Create your views here.
from rest_framework.decorators import api_view
from rest_framework.response import Response
from checkApp.models import Fireware, Mes_server, Cpu
from common import constants

# 固件信息检验
@api_view(['GET'])
def system_checkout(request):
    cmd = 'dmidecode -t system |grep -i "Product Name:"'
    get_product_name = h.run_cmd(cmd)
    cmd = 'dmidecode -t system |grep -i "Serial Number:"'
    get_system_sn = h.run_cmd(cmd)
    cmd = 'dmidecode -t system |grep -i "Manufacturer:"'
    get_system_manufacturer = h.run_cmd(cmd)
    cmd = 'dmidecode -t system| grep -i "Version:"'
    get_system_version = h.run_cmd(cmd)
    cmd = 'dmidecode -t bios |grep -i "BIOS Revision:"'
    get_bios_version = h.run_cmd(cmd)
    cmd = 'ipmitool mc info |grep -i "Firmware Revision"'
    get_bmc_version = h.run_cmd(cmd)

    product_name = get_product_name['cmd_infor'].split(":")[1].lstrip()
    system_sn = get_system_sn['cmd_infor'].split(":")[1].lstrip()
    system_manufacturer = get_system_manufacturer['cmd_infor'].split(":")[1].lstrip()
    system_version = get_system_version['cmd_infor'].split(":")[1].lstrip()
    bios_version = get_bios_version['cmd_infor'].split(":")[1].lstrip()
    bmc_version = get_bmc_version['cmd_infor'].split(":")[1].lstrip()

    sn = constants.sn
    mes_product_name = Fireware.objects.get(sn=sn)
    mes_product_name = str(mes_product_name)
    mes_fireware = Fireware.objects.values_list().get(sn=sn)
    if product_name == mes_product_name:
        checkout_product = {"product_name": product_name, "mes_product_name": mes_product_name, "status": "pass" }
    else:
        checkout_product = {"product_name": product_name, "mes_product_name": mes_product_name, "status": "fail" }

    if system_sn == mes_fireware[3]:
        checkout_sn = {"system_sn": system_sn, "mes_system_sn": mes_fireware[3], "status": "pass"}
    else:
        checkout_sn = {"system_sn": system_sn, "mes_system_sn": mes_fireware[3], "status": "fail"}

    if system_manufacturer == mes_fireware[4]:
        checkout_manfacturer = {"system_manufacturer": system_manufacturer, "mes_system_manufacturer": mes_fireware[4], "status": "pass"}
    else:
        checkout_manfacturer = {"system_manufacturer": system_manufacturer, "mes_system_manufacturer": mes_fireware[4], "status": "fail"}

    if system_version == mes_fireware[5]:
        checkout_version = {"system_version": system_version, "mes_system_version": mes_fireware[5], "status": "pass"}
    else:
        checkout_version = {"system_version": system_version, "mes_system_version": mes_fireware[5], "status": "fail"}

    if bios_version == mes_fireware[6]:
        checkout_bios_version = {"bios_version": bios_version, "mes_bios_version": mes_fireware[6], "status": "pass"}
    else:
        checkout_bios_version = {"bios_version": bios_version, "mes_bios_version": mes_fireware[6], "status": "fail"}

    if bmc_version == mes_fireware[7]:
        checkout_bmc_version = {"bmc_version": bmc_version, "mes_bmc_version": mes_fireware[7], "status": "pass"}
    else:
        checkout_bmc_version = {"bmc_version": bmc_version, "mes_bmc_version": mes_fireware[7], "status": "fail"}

    response_data = {"checkout_product": checkout_product, "checkout_sn": checkout_sn,
                     "checkout_manfacturer": checkout_manfacturer, "checkout_version": checkout_version,
                     "checkout_bios_version": checkout_bios_version, "checkout_bmc_version": checkout_bmc_version}
    return Response(response_data)


# CPU信息校验
@api_view(['GET'])
def cpu_checkout(request):
    cpu_number = []
    cmd = 'dmidecode -t Processor |grep -i "handle " |awk -F " " \'{print $2}\'|tr -d ","'
    handle = h.run_cmd(cmd)
    for i in handle['cmd_infor'].split("\n"):
        cmd = 'dmidecode -H %s |grep -i "Current Speed: "' % i
        get_cpu_speed = h.run_cmd(cmd)
        cpu_speed = get_cpu_speed['cmd_infor'].split(":")[1].lstrip()
        cpu_number.append(cpu_speed)
    number = len(set(cpu_number))
    if number == 1:
        speed = cpu_number[0]
    else:
        speed = cpu_number
    cmd = 'dmidecode -s processor-version'
    get_cpu_type = h.run_cmd(cmd)['cmd_infor'].split(":")
    if get_cpu_type[0].split('\n')[0] ==  get_cpu_type[0].split('\n')[1]:
        cpu_type = get_cpu_type[0].split('\n')[0]
    else:
        cpu_type = get_cpu_type[0].split('\n')
    cmd = 'arch'
    architecture = h.run_cmd(cmd)['cmd_infor'].split(":")[0]
    cmd = 'grep "physical id" /proc/cpuinfo | sort -u | wc -l'
    core_number = int(h.run_cmd(cmd)['cmd_infor'].split(":")[0])
    cmd = "grep 'processor' /proc/cpuinfo | sort -u | wc -l"
    thread_number = int(h.run_cmd(cmd)['cmd_infor'].split(":")[0])

    sn = constants.sn
    mes_cpu = Cpu.objects.values_list().get(sn=sn)
    if cpu_type == mes_cpu[3]:
        checkout_type = {"cpu_type": cpu_type, "mes_cpu_type": mes_cpu[3], "status": "pass"}
    else:
        checkout_type = {"cpu_type": cpu_type, "mes_cpu_type": mes_cpu[3], "status": "fail"}

    if architecture == mes_cpu[4]:
        checkout_architecture = {"architecture": architecture, "mes_architecture": mes_cpu[4], "status": "pass"}
    else:
        checkout_architecture = {"architecture": architecture, "mes_architecture": mes_cpu[4], "status": "fail"}

    if core_number == mes_cpu[5]:
        checkout_core = {"core_number": core_number, "mes_core_number": mes_cpu[5], "status": "pass"}
    else:
        checkout_core = {"core_number": core_number, "mes_core_number": mes_cpu[5], "status": "fail"}

    if thread_number == mes_cpu[6]:
        checkout_thread = {"thread_number": thread_number, "mes_thread_number": mes_cpu[6], "status": "pass"}
    else:
        checkout_thread = {"thread_number": thread_number, "mes_thread_number": mes_cpu[6], "status": "fail"}

    if speed == mes_cpu[7]:
        checkout_speed = {"speed": speed, "mes_speed": mes_cpu[7], "status": "pass"}
    else:
        checkout_speed = {"speed": speed, "mes_speed": mes_cpu[7], "status": "fail"}

    response_data = {"checkout_type": checkout_type, "checkout_architecture": checkout_architecture,
                     "checkout_core": checkout_core, "checkout_thread": checkout_thread, "checkout_speed": checkout_speed}
    return Response(response_data)