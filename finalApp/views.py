# coding=utf-8
import json
import re
import subprocess
import sys

from rest_framework.decorators import api_view
from rest_framework.response import Response
from utils import handle as h
from common import constants as c, operation as on
import os
import time


@api_view(['GET'])
def run_item(request):
    on.remove_log(c.BLACK_LIST_LOG_PATH)
    check_hdd()
    check_nvme()
    # check_mce_log()
    check_ethernet_errors()
    check_PCIE_errors()
    check_SEL()
    check_mce_ecc()
    response_data = {"msg": "Black Check Finish!", "status": "PASS"}
    return Response(response_data)


# 读取日志，0为没有运行完成，或者出现错误；1为运行完成
@api_view(['GET'])
def get_black_log(request):
    black_result = black_result_check()
    # f = open(c.BLACK_LIST_LOG_PATH, "r", encoding="utf-8")
    with open(c.BLACK_LIST_LOG_PATH, "r") as f:
        data = f.read()
        if black_result:
            response_data = {'black_log': black_result, "status": "FAIL"}
        elif "All Black check is successful!" in data:
            response_data = {"black_log": data, "status": "PASS"}
        else:
            response_data = {"black_log": data, "status": "Checking..."}

        f.flush()
        f.close()
    return Response(response_data)


# SSD和HDD检查
def check_hdd():
    write_log("\n" + "**" * 12 + " Check HDD and SSD  " + get_local_time_string() + "  " + "**" * 12)
    pgone = 'SMART overall-health self-assessment test result: PASSED'
    SAS = 'Transport protocol:   SAS (SPL-3)'
    SAS_h = 'SMART Health Status: OK'
    cmd = 'lspci |grep -i "raid"'
    all = subprocess.getstatusoutput(cmd)
    # Raid卡
    if len(all[1]) != 0:
        panfu_list = []
        yingpan_list = []

        cmd = '/home/autotest/tools/MegaCli64 -LdPdInfo -aALL | grep "Device Id:"'
        hdd_number = h.cmd_msg(cmd).split('\n')

        cmd = 'ls /sys/block |grep -Ev "loop*|ram*|nvme|dm"'
        hdd_name = h.cmd_msg(cmd).split('\n')
        # SAS和SATA硬盘
        if len(hdd_name) != 0:

            for i in hdd_number:
                panfu = i.split()[2]
                panfu = int(panfu)
                panfu_list.append(panfu)

            for i in hdd_name:
                yingpan = i.split()[0]
                yingpan_list.append(yingpan)

            for i in range(0, len(panfu_list)):
                panduan = False
                cmd = 'smartctl -a -d megaraid,%d /dev/%s' % (panfu_list[i], yingpan_list[i])
                yp_info = subprocess.getstatusoutput(cmd)
                # sn=re.findall(r'(Serial Number:(.*))',yp_info[1])
                cmd = 'smartctl -a -d megaraid,%d /dev/%s |grep -i "Serial number:"' % (panfu_list[i], yingpan_list[i])
                sn = subprocess.getstatusoutput(cmd)
                for line in yp_info[1].split('\n'):
                    if re.search(pgone, line, re.IGNORECASE):
                        write_log('the check hdd is go :SMART overall-health self-assessment test result: PASSED')
                        panduan = True

                if panduan == True:
                    write_log(sn[1])
                    RS = re.findall(r'(Reallocated_Sector_Ct(.*))', yp_info[1])
                    x = RS[0][1].split()[-1]
                    x = int(x)
                    if x <= 10:
                        write_log('Reallocated_Sector_Ct is OK')
                    else:
                        write_log(sn[1])
                        write_log("Reallocated_Sector_Ct is fail")
                        h.run_fail()
                    EE = re.findall(r'(End-to-End_Error(.*))', yp_info[1])
                    CP = re.findall(r'(Current_Pending_Sector(.*))', yp_info[1])
                    x = CP[0][-1].split()[-1]
                    x = int(x)
                    if x == 0:
                        write_log("Current_Pending_Sector is OK")
                    else:
                        write_log(sn[1])
                        write_log("Current_Pending_Sector is fail")
                        h.run_fail()
                        return
                else:
                    write_log(sn[1])
                    write_log("SMART overall-health self-assessment test result is fail")
                    return
        # 没有SAS和SATA硬盘
        else:
            write_log("Cannot find the SATA HDD and SSD,Pleace check about")
    # 没有Raid卡
    else:
        cmd = 'ls /sys/block |grep -Ev "loop*|ram*|nvme|dm"'
        hdd_name = h.cmd_msg(cmd).split('\n')
        # SSD、HDD
        if len(hdd_name) != 0:
            for i in hdd_name:
                panduan = False
                cmd = 'smartctl -a /dev/%s' % i
                yp_info = subprocess.getstatusoutput(cmd)
                cmd = 'smartctl -a /dev/%s |grep -i "Transport protocol:   SAS"' % i
                wtf = subprocess.getstatusoutput(cmd)
                cmd = 'smartctl -a /dev/%s |grep -i "Serial number:"' % i
                sn = subprocess.getstatusoutput(cmd)
                if len(wtf[1]) != 0:
                    write_log("this hdd is SAS:%s" % i)
                    for line in yp_info[1].split('\n'):
                        if re.search(SAS_h, line, re.IGNORECASE):
                            write_log('the check SAS hdd is go :SMART Health Status: OK')
                            panduan = True
                    if panduan == True:
                        write_log(sn[1])
                        EL = re.findall(r'(Elements in grown defect list:(.*))', yp_info[1])
                        x = EL[0][-1].split()[-1]
                        x = int(x)
                        if x <= 5:
                            write_log('Elements in grown defect list is OK')
                        else:
                            write_log(sn[1])
                            write_log("Elements in grown defect list is fail")
                            h.run_fail()
                else:
                    for line in yp_info[1].split('\n'):
                        if re.search(pgone, line, re.IGNORECASE):
                            write_log('the check hdd is go :SMART overall-health self-assessment test result: PASSED')
                            panduan = True

                    if panduan == True:
                        write_log(sn[1])
                        RS = re.findall(r'(Reallocated_Sector_Ct(.*))', yp_info[1])
                        for i in RS:
                            x = i[0].split()[-1]
                            x = int(x)
                            if x <= 10:
                                write_log('Reallocated_Sector_Ct is OK')
                            else:
                                write_log(sn[1])
                                write_log("Reallocated_Sector_Ct is fail")
                                h.run_fail()
                        EE = re.findall(r'(End-to-End_Error(.*))', yp_info[1])

                        CP = re.findall(r'(Current_Pending_Sector(.*))', yp_info[1])
                        for i in CP:
                            x = i[0].split()[-1]
                            x = int(x)
                            if x == 0:
                                write_log("Current_Pending_Sector is OK")
                            else:
                                write_log(sn[1])
                                write_log("Current_Pending_Sector is fail")
                                h.run_fail()
                    else:
                        write_log(sn[1])
                        write_log("SMART overall-health self-assessment test result is fail")
                        h.run_fail()
            write_log("Check SSD and HDD successful")
        else:
            write_log("Cannot find the HDD and SSD,Pleace check about")
        return


# NVME检查
def check_nvme():
    write_log("\n" + "**" * 15 + "     Check NVME  " + get_local_time_string() + "     " + "**" * 15)
    cmd = 'ls /sys/block |grep -Ev "loop*|ram*|sd*|dm"'
    nvme_name = subprocess.getstatusoutput(cmd)
    if len(nvme_name[1]) != 0:
        for xxl in nvme_name[1].split("\n"):
            write_log("the check nvme is go,this is :%s" % xxl)
            cmd = 'nvme smart-log /dev/%s' % (xxl)
            nvme_info = subprocess.getstatusoutput(cmd)
            # nvme_info = nvme_info[1].split('\n')
            CW = re.findall(r'(critical_warning(.*))', nvme_info[1])
            x = CW[0][-1].split()[-1]
            x = int(x)
            if x == 0:
                write_log('critical_warning is OK')
            else:
                write_log("critical_warning is fail")
                h.run_fail()
            cmd = 'nvme smart-log /dev/%s |grep "available_spare                     :"' % (xxl)
            AS = subprocess.getstatusoutput(cmd)
            AS = re.findall(r'(available_spare(.*))', AS[1])
            x = AS[0][1].split()[-1]
            x = str(x)
            if x == '100%' or x == '99%':
                write_log('available_spare is OK')
            else:
                write_log("available_spare is fail")
                h.run_fail()
            cmd = 'nvme smart-log /dev/%s |grep "percentage_used"' % (xxl)
            PU = subprocess.getstatusoutput(cmd)
            PU = re.findall(r'(percentage_used(.*))', PU[1])
            x = PU[0][1].split()[-1]
            x = str(x)
            if x == '0%':
                write_log('percentage_used is OK')
            else:
                write_log("percentage_used is fail")
                h.run_fail()
        write_log("Check nvme successful")
    else:
        write_log("Cannot find the NVME,Pleace check about.")


# CPU MCE Check
def check_mce_log():
    write_log("\n" + "**" * 15 + "     Check MCE  " + get_local_time_string() + "      " + "**" * 15)
    error_log = []
    match_keys = "above temperature, being removed, CATEER, critical, Corrected, scrub error, degraded, dead device, " \
                 "Device offlined, device_unblocked, error, err,  failed, failure, fault, HDD block removing handle, " \
                 "hard resetting link, IERR, lost, machine check events, MCA, MCE Log, no readable, resetting link, " \
                 "scsi hang, single - bit ECC, soft lockup timeout, Temperature  above threshold, task abort," \
                 "overcurrent, offline device,retry,uncorrect,call_trace, blocked for more than"
    white_list = "qwert,yuiop, XCB error, gssproxy"
    cmd = "cat /var/log/messages"
    msg_info = subprocess.getstatusoutput(cmd)
    if msg_info[0] == 0:
        for line in msg_info[1].split('\n'):
            pattern = "|".join(match_keys.split(","))
            ignore = "|".join(white_list.split(","))
            if re.search(pattern, line, re.IGNORECASE):
                if not re.search(ignore, line, re.IGNORECASE):
                    error_log.append(line)
    else:
        write_log(msg_info[1])
    if len(error_log) > 0:
        for log in error_log:
            write_log(log)
        h.run_fail()
    else:
        write_log("-->>> MCE Black Check keys PASS")
    return


# 网口误码
def check_ethernet_errors():
    write_log("\n" + "**" * 14 + "   Check Ethernet  " + get_local_time_string() + "   " + "**" * 14)
    errors_dev = {}
    result = h.cmd_msg('ls -1 /sys/class/net/ |grep -Ev "lo|enx|vir|docker"').split('\n')

    for dev in result:
        cmd = "ethtool  %s |grep Speed" % (dev)
        ret_info = h.cmd_msg(cmd)
        if 'Mb/s' in ret_info:
            speed = int(ret_info.split()[1].split('Mb/s')[0])
            if speed <= 1000:
                continue

        err_count = 0
        cmd = 'ethtool -S  %s |grep -iE "err|drop|crc"' % (dev)
        dev_info = h.cmd_msg(cmd).split('\n')
        for i in dev_info:
            index = i.rfind(":")
            value = int(i[index + 1:].strip())
            err_count += value
        if (err_count != 0):
            errors_dev[dev] = str(err_count)
        write_log("%s network port Bit number: %d" % (dev, err_count))

    if (len(errors_dev) > 0):
        write_log("check network port Bit:" + str(errors_dev))
        write_log("network port Bit error")
        h.run_fail()
    write_log("network ethernet successful")
    return


# PCIE误码检查
def check_PCIE_errors():
    write_log("\n" + "**" * 14 + "     Check PCIE  " + get_local_time_string() + "     " + "**" * 14)
    dev_AER = {}
    dev_list = []
    cmd = "lspci"
    dev_info = h.cmd_msg(cmd).split('\n')
    for dev in dev_info:
        bdf = dev.split()[0]
        dev_list.append(bdf)
    for dev in dev_list:
        cmd = "lspci -s  %s -vvvv" % (dev)
        dev_info = h.cmd_msg(cmd).split('\n')
        for num in range(0, len(dev_info)):
            if "Advanced Error Reporting" in dev_info[num]:
                write_log("check %s AER start" % dev)
                if "UESta" in dev_info[num + 1]:
                    UESta = dev_info[num + 1]
                if "UEMsk" in dev_info[num + 2]:
                    UEMsk = dev_info[num + 2]
                if "CESta" in dev_info[num + 4]:
                    CESta = dev_info[num + 4]
                if "CEMsk" in dev_info[num + 5]:
                    CEMsk = dev_info[num + 5]

                for index in range(0, len(UEMsk.split())):
                    if "-" in UEMsk.split()[index]:
                        if "+" in UESta.split()[index]:
                            write_log(UESta)
                            dev_AER[dev + ".UESta"] = UESta
                            # self.on_fail(dev)

                for index in range(0, len(CEMsk.split())):
                    if "-" in CEMsk.split()[index]:
                        if "+" in CESta.split()[index]:
                            write_log(CESta)
                            dev_AER[dev + ".CESta"] = CESta
                            # self.on_fail(dev)
                write_log("check %s AER end" % dev)
    if (len(dev_AER) > 0):
        write_log('check PCIE AER Bit have error')
        h.run_fail()
    else:
        write_log('check PCIE AER Bit normal')
    return


# SEL报错关键字查找
def check_SEL():
    write_log("\n" + "**" * 15 + "      Check SEL  " + get_local_time_string() + "     " + "**" * 15)
    cmd = "ipmitool sel clear"
    sel_clear = h.cmd_msg(cmd)
    match_keys = "abort,cancel,correctable ECC,critical,degrate,disconnect,Deasserted,down,expired,Err,Error," \
                 "exception,failed,failure,Fault,halt,hot,insufficient,link down,linkdown,limit,lost,miss," \
                 "Mismatch,shutdown,shut down,shortage,unstable,unrecoverable,unreachable," \
                 "Uncorrectable ECC,warning"
    white_list = "qwert,yuiop"
    sel_lists = []
    cmd = "ipmitool sel elist"
    sel_info = h.cmd_msg(cmd).split('\n')
    for line in sel_info:
        pattern = "|".join(match_keys.split(","))
        ignore = "|".join(white_list.split(","))
        if re.search(pattern, line, re.IGNORECASE):
            if not re.search(ignore, line, re.IGNORECASE):
                sel_lists.append(line)

    if (len(sel_lists) > 0):
        for sel_list in sel_lists:
            write_log(sel_list)
        write_log("blacklist SEL key error")
        h.run_fail()
    else:
        write_log("blacklist SEL key successful")
    return


# MCE and ECC 检查
def check_mce_ecc():
    write_log("\n" + "**" * 12 + "  Check MCE AND ECC  " + get_local_time_string() + "  " + "**" * 12)
    cpu_mec_display = h.cmd_msg("ras-mc-ctl --summary")
    # write_log(cpu_mec_display)
    cpu_mce = cpu_mce_errors(cpu_mec_display)
    if cpu_mce:
        write_log(cpu_mce)
        write_log("CPU MCE have error")
        h.run_fail()
    else:
        write_log("CPU MCE successful")

    # 再次检查ECC SEL
    check_SEL()
    write_log("\n" + "**" * 21 + "  All  Black  End  " + "**" * 20)
    write_log("-->> All Black check is successful!")
    return


# CPU MCE 检测出现错误
def cpu_mce_errors(mce_errors):
    temp = mce_errors.split('\n')
    for mce in temp:
        if mce == '':
            continue
        result = re.match("No", mce)
        if not result:
            errors_information = h.run_cmd("ras-mc-ctl --errors")
            return errors_information
    return


# 检查log是否错误
def black_result_check():
    with open(c.BLACK_LIST_LOG_PATH, "r+") as f:
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
        f.close()
        return


def write_log(s):
    with open(c.BLACK_LIST_LOG_PATH, 'a+') as f:
        print(s)
        f.write(str(s) + '\n')
        f.flush()
        os.fsync(f)


def get_local_time_string():
    return time.strftime('%04Y-%m-%d %H:%M:%S', time.localtime(time.time()))
