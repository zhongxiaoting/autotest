# coding=utf-8
import commands
import os
import re
import sys
from main.item import Item
from common import constants as c
from utils import decorator, log as l
from common import common_value
import time
from station_stress.MCE_ECC import MCE_ECC

sys.path.append("..")

class BlackListCheck(Item):

    def __init__(self,info):
        super(BlackListCheck, self).__init__()
        self.info=info
        self.finished = False
        self.results = {}

    def run_item(self):
        self.report_info('S')
        self.check_hdd()
        self.check_nvme()
        self.check_mcelog()
        self.check_ethernet_errors()
        self.check_PCIE_errors()
        self.check_SEL()
        self.look_ecc()
        write_log('check blacklist finished')
        if len(self.results) == 0:
            self.report_info('P')
            #self.on_pass()
            write_log("ALL GOOD")
        else:
            self.report_info('F')
            write_log(self.results, False)
            self.on_fail()
        self.finished = True

    def check_nvme(self):
        # cmd = 'lspci |grep -i "raid"'
        # all = commands.getstatusoutput(cmd)
        nvme_name=[]
        cmd = 'ls /sys/block |grep -Ev "loop*|ram*|sd*|dm"'
        nvme_name = commands.getstatusoutput(cmd)
        if len(nvme_name[1]) != 0:
            for xxl in nvme_name[1]:

                write_log("the check nvme is go,this is :%s" % xxl)

                cmd = 'nvme smart-log /dev/%s' % (xxl)
                nvme_info = commands.getstatusoutput(cmd)
                nvme_info=nvme_info[1].split('\n')
                CW=re.findall(r'(critical_warning(.*))',nvme_info[1])
                #print(CW)
                for i in CW:
                    x = i[0].split()[-1]
                    #write_log(x)
                    x=int(x)
                    if x ==0:
                        write_log('critical_warning is OK')
                    else:
                        write_log("critical_warning is fail")
                        self.results['nvme_log'] = 'fail'
                        self.result_fail()

                #AS = re.findall(r'(available_spare(.*))',nvme_info[1])
                #print(AS)
                cmd ='nvme smart-log /dev/%s |grep "available_spare                     :"' % (xxl)
                AS=commands.getstatusoutput(cmd)
                AS=re.findall(r'(available_spare(.*))',AS[1])
                #print(AS)

                for i in AS:
                    x = i[0].split()[-1]
                    #write_log(x)
                    x = str(x)
                    if x == '100%' or x=='99%':
                        write_log('available_spare is OK')
                    else:
                        write_log("available_spare is fail")
                        self.results['nvme_log'] = 'fail'
                        self.result_fail()

                # PU = re.findall(r'(percentage_used(.*))',nvme_info[1])
                # print(PU)
                cmd = 'nvme smart-log /dev/%s |grep "percentage_used"' % (xxl)

                PU=commands.getstatusoutput(cmd)
                #print(PU)

                PU=re.findall(r'(percentage_used(.*))',PU[1])
                for i in PU:
                    x = i[0].split()[-1]
                    #write_log(x)
                    x = str(x)
                    if x == '0%':
                        write_log('percentage_used is OK')
                    else:
                        write_log("percentage_used is fail")
                        self.results['nvme_log'] = 'fail'
                        self.result_fail()

        else:
            write_log("cannot find the nvme,pleace check about.")
                # print(POH)
                # cmd='nvme smart-log /dev/%s |grep "power_on_hours"' % (xxl)
                # POH=commands.getstatusoutput(cmd)
                # POH = re.findall(r'(power_on_hours(.*))',POH[1])
                # print(POH)
                # for i in POH:
                #     x = i[0].split()[-1]
                #     print(x)
                #     x = float(x)
                #     if x <= 10000:
                #         write_log('power_on_hours is ok')
                #     else:
                #         write_log("power_on_hours is fail")
                #         self.results['nvme_log'] = 'fail'
                #         self.result_fail()




    def check_hdd(self):
        pgone = 'SMART overall-health self-assessment test result: PASSED'
        SAS='Transport protocol:   SAS (SPL-3)'
        SAS_h='SMART Health Status: OK'
        cmd='lspci |grep -i "raid"'
        all=commands.getstatusoutput(cmd)


        if len(all[1])!=0:
            print(all)
            panfu_list=[]
            yingpan_list=[]
            yp_info = []
            #nvme_name=[]

            cmd='/opt/MegaRAID/MegaCli/MegaCli64 -LdPdInfo -aALL | grep "Device Id:"'
            hdd_number=self.run_cmd(cmd).split('\n')

            cmd='ls /sys/block |grep -Ev "loop*|ram*|nvme|dm"'
            hdd_name=self.run_cmd(cmd).split('\n')

            if len(hdd_name)!=0:

                for i in hdd_number:
                    panfu=i.split()[2]
                    panfu=int(panfu)
                    panfu_list.append(panfu)
                #much=len(panfu_list)

                for i in hdd_name:
                    yingpan=i.split()[0]
                    yingpan_list.append(yingpan)

            #for num in range(0, len(dev_info)):


                for i in range(0,len(panfu_list)):
                    # cmd = "cat /var/log/messages"
                    # msg_info = commands.getstatusoutput(cmd)
                    cmd = 'smartctl -a -d megaraid,%d /dev/%s' % (panfu_list[i],yingpan_list[i])
                    yp_info=commands.getstatusoutput(cmd)
                    #sn=re.findall(r'(Serial Number:(.*))',yp_info[1])
                    cmd = 'smartctl -a -d megaraid,%d /dev/%s |grep -i "Serial number:"' % (panfu_list[i],yingpan_list[i])
                    sn = commands.getstatusoutput(cmd)
                    for line in yp_info[1].split('\n'):
                        if re.search(pgone,line,re.IGNORECASE):
                            write_log('the check hdd is go :SMART overall-health self-assessment test result: PASSED')
                            panduan=True
                        else:
                            pass


                    if panduan == True:
                        write_log(sn[1])
                        RS=re.findall(r'(Reallocated_Sector_Ct(.*))',yp_info[1])
                        for i in RS:
                            x=i[0].split()[-1]
                            #write_log(x)
                            x=int(x)
                            if x <=10:
                                write_log('Reallocated_Sector_Ct is OK')
                            else:
                                write_log(sn[1])
                                write_log("Reallocated_Sector_Ct is fail")
                                self.results['hdd_log'] = 'fail'
                                # result_fail(self)
                                self.result_fail()
                        EE=re.findall(r'(End-to-End_Error(.*))',yp_info[1])
                        CP=re.findall(r'(Current_Pending_Sector(.*))',yp_info[1])
                        for i in CP:
                            x=i[0].split()[-1]
                            #write_log(x)
                            x=int(x)
                            if x == 0:
                                write_log("Current_Pending_Sector is OK")
                            else:
                                write_log(sn[1])
                                write_log("Current_Pending_Sector is fail")
                                self.results['hdd_log'] = 'fail'
                                # result_fail(self)
                                self.result_fail()
                        #UC=re.findall(r'(UDMA_CRC_Error_Count(.*))',yp_info[1])
                        #print(UC)
                    else:
                        write_log(sn[1])
                        write_log("SMART overall-health self-assessment test result is fail")
                        self.results['hdd_log'] = 'fail'
                        # result_fail(self)
                        self.result_fail()

            else:
                write_log("cannot find the hdd and ssd,pleace check about")
        else:
            cmd = 'ls /sys/block |grep -Ev "loop*|ram*|nvme|dm"'
            hdd_name = self.run_cmd(cmd).split('\n')
            if len(hdd_name) != 0:
                panduan =False
                for i in hdd_name:
                    print(i)
                    cmd = 'smartctl -a /dev/%s' %i
                    yp_info = commands.getstatusoutput(cmd)
                    cmd = 'smartctl -a /dev/%s |grep -i "Transport protocol:   SAS"' %i
                    wtf=commands.getstatusoutput(cmd)
                    cmd = 'smartctl -a /dev/%s |grep -i "Serial number:"' %i
                    sn=commands.getstatusoutput(cmd)
                    if len(wtf[1])!=0:
                        #write_log(wtf)
                        write_log("this hdd is SAS:%s" %i)
                        for line in yp_info[1].split('\n'):
                            if re.search(SAS_h, line, re.IGNORECASE):
                                write_log('the check SAS hdd is go :SMART Health Status: OK')
                                panduan = True
                            else:
                                pass
                        if panduan == True:
                            write_log(sn[1])
                            EL=re.findall(r'(Elements in grown defect list:(.*))',yp_info[1])
                            for i in EL:
                                x=i[0].split()[-1]
                                x=int(x)
                                if x<=5:
                                    write_log('Elements in grown defect list is OK')
                                else:
                                    write_log(sn[1])
                                    write_log("Elements in grown defect list is fail")
                                    self.results['hdd_log'] = 'fail'
                                    # result_fail(self)
                                    self.result_fail()

                    else:
                        for line in yp_info[1].split('\n'):
                            if re.search(pgone, line, re.IGNORECASE):
                                write_log('the check hdd is go :SMART overall-health self-assessment test result: PASSED')
                                panduan = True

                            else:
                                pass
                        if panduan == True:
                            write_log(sn[1])
                            RS = re.findall(r'(Reallocated_Sector_Ct(.*))',yp_info[1])
                            for i in RS:
                                x = i[0].split()[-1]
                                # write_log(x)
                                x = int(x)
                                if x <= 10:
                                    write_log('Reallocated_Sector_Ct is OK')
                                else:
                                    write_log(sn[1])
                                    write_log("Reallocated_Sector_Ct is fail")
                                    self.results['hdd_log'] = 'fail'
                                    # result_fail(self)
                                    self.result_fail()

                            EE = re.findall(r'(End-to-End_Error(.*))', yp_info[1])

                            CP = re.findall(r'(Current_Pending_Sector(.*))', yp_info[1])
                            for i in CP:
                                x = i[0].split()[-1]
                                # write_log(x)
                                x = int(x)
                                if x == 0:
                                    write_log("Current_Pending_Sector is OK")
                                else:
                                    write_log(sn[1])
                                    write_log("Current_Pending_Sector is fail")
                                    self.results['hdd_log'] = 'fail'
                                    # result_fail(self)
                                    self.result_fail()
                        else:
                            write_log(sn[1])
                            write_log("SMART overall-health self-assessment test result is fail")
                            self.results['hdd_log'] = 'fail'
                            # result_fail(self)
                            self.result_fail()

            else:
                write_log("cannot find the hdd and ssd,pleace check about")

    def look_ecc(self):
        MCE_ECC(Item).cpu_mce_check()
        MCE_ECC(Item).mem_ecc_check()
        #class MCE_ECC(Item):

    def check_mcelog(self):
        error_log = []
        match_keys = "above temperature, being removed, CATEER, critical, Corrected, scrub error, degraded, dead device, " \
                     "Device offlined, device_unblocked, error, err,  failed, failure, fault, HDD block removing handle, " \
                     "hard resetting link, IERR, lost, machine check events, MCA, MCE Log, no readable, resetting link, " \
                     "scsi hang, single - bit ECC, soft lockup timeout, Temperature  above threshold, task abort," \
                     "overcurrent, offline device,retry,uncorrect,call_trace, blocked for more than"
        white_list = "qwert,yuiop"
        white_list = "qwert,yuiop, XCB error, gssproxy"
        # cmd = "dmesg"
        # dmsg_info = self.run_cmd(cmd).split('\n')
        # for line in dmsg_info:
        #     pattern = "|".join(match_keys.split(","))
        #     ignore = "|".join(white_list.split(","))
        #     if re.search(pattern, line, re.IGNORECASE):
        #         if not re.search(ignore, line, re.IGNORECASE):
        #             print('gg')
                    #error_log.append(line)

        #write_log(error_log)
        cmd = "cat /var/log/messages"
        msg_info = commands.getstatusoutput(cmd)
        if msg_info[0] == 0:
            for line in msg_info[1].split('\n'):
                pattern = "|".join(match_keys.split(","))
                ignore = "|".join(white_list.split(","))
                if re.search(pattern, line, re.IGNORECASE):
                    if not re.search(ignore, line, re.IGNORECASE):
                        error_log.append(line)
           # write_log(error_log)
        else:
            #write_log(msg_info)
            self.report_info('F')
            self.on_fail("get mce log messages error")
            self.results['mce_log'] = 'fail'
            #result_fail(self)
            self.result_fail()





        if (len(error_log) > 0):
            write_log(error_log)
            self.report_info('F')
            self.on_fail("mce log black keys error")
            self.results['mce_log'] = 'fail'
            self.result_fail()


        #hdd_keys="SMART overall-health self-assessment test result: PASSED"\




    def check_PCIE_errors(self):
        dev_AER = {}
        dev_list = []
        cmd = "lspci"
        dev_info = self.run_cmd(cmd).split('\n')
        for dev in dev_info:
            bdf = dev.split()[0]
            dev_list.append(bdf)
        for dev in dev_list:
            cmd = "lspci -s  %s -vvvv" % (dev)
            dev_info = self.run_cmd(cmd).split('\n')
            for num in range(0, len(dev_info)):
                if "Advanced Error Reporting" in dev_info[num]:
                    write_log("check %s AER start" % dev, False)
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
                                self.on_fail(dev)

                    for index in range(0, len(CEMsk.split())):
                        if "-" in CEMsk.split()[index]:
                            if "+" in CESta.split()[index]:
                                write_log(CESta)
                                dev_AER[dev + ".CESta"] = CESta
                                self.on_fail(dev)
                    write_log("check %s AER end" % dev, False)


        if (len(dev_AER) > 0):
            self.report_info('F')
            self.on_fail()
            self.results['check_AER'] = 'fail'
            self.result_fail()
        else:
            write_log('check PCIE AER Bit normal')

        return


    def check_SEL(self):
        match_keys = "abort,cancel,correctable ECC,critical,degrate,disconnect,Deasserted,down,expired,Err,Error," \
                     "exception,failed,failure,Fault,halt,hot,insufficient,link down,linkdown,limit,lost,miss," \
                     "Mismatch,reset,shutdown,shut down,shortage,unstable,unrecoverable,unreachable," \
                     "Uncorrectable ECC,warning"
        white_list = "qwert,yuiop"
        sel_list = []
        cmd = "ipmitool sel elist"
        sel_info = self.run_cmd(cmd).split('\n')
        for line in sel_info:
            pattern = "|".join(match_keys.split(","))
            ignore = "|".join(white_list.split(","))
            if re.search(pattern, line, re.IGNORECASE):
                if not re.search(ignore, line, re.IGNORECASE):
                    sel_list.append(line)

        if (len(sel_list) > 0):
            write_log(sel_list)
            self.report_info('F')
            self.on_fail("balcklist SEL key error")
            #self.finished = True
            self.results['check_SEL_ERROR'] = 'fail'
            self.result_fail()
            #ar.pause()





    def check_ethernet_errors(self):
        errors_dev = {}
        result = self.run_cmd('ls -1 /sys/class/net/ |grep -Ev "lo|enx|vir"').split('\n')

        for dev in result:
            cmd = "ethtool  %s |grep Speed"%(dev)
            ret_info = self.run_cmd(cmd)
            if 'Mb/s' in ret_info:
                speed = int(ret_info.split()[1].split('Mb/s')[0])
                if speed <= 1000:
                    continue

            err_count = 0
            cmd = 'ethtool -S  %s |grep -iE "err|drop|crc"'%(dev)
            dev_info = self.run_cmd(cmd).split('\n')
            for i in dev_info:
                index = i.rfind(":")
                #index=0
                #key_name = l[:index].strip()
                value = int(i[index+1:].strip())
                #value=int(l[1].strip())
                err_count += value
                #err_count =0
            '''
            cmd = 'ifconfig %s|grep -iE "err|drop"'%(dev)
            dev_info = self.run_command(cmd,False).get_payload().split('\n')
            for l in dev_info:
                errors_cnt = int(l.strip().split()[2])
                dropped_cnt = int(l.strip().split()[4])
                err_count += errors_cnt
                err_count += dropped_cnt
            '''

            if (err_count != 0):
                errors_dev[dev] = str(err_count)
            write_log("%s network port Bit number: %d" %(dev, err_count))

        if ( len(errors_dev) > 0 ):
            write_log("check network port Bit:" + str(errors_dev))
            self.on_fail("network port Bit")
            self.report_info('F')
            #self.finished = True
            self.results['check_Eth_ERROR'] = 'fail'
            self.result_fail()


    def report_info(self,st):
        #loopinfo = "%s-%s\n" % (self.loop, time.strftime("%H%M%S%Y%m%d", time.localtime()))
        #status = 'Testing\n'
        if st == 'F':
            #status = 'FAIL\n'
            write_log("This test fail")
        if st == 'P':
            #status = 'PASS\n'
            write_log("test pass!")

    def on_fail(self,msg=None):
        #write_log("error")
        #write_log("end of this test")
        self.success = False
        self.finished = True
        #self.show_fail(msg)


def write_log(s):
    with open(c.BLACK_LIST_LOG, 'a+') as f:
        print(s)
        f.write(str(s) + '\n')
        f.flush()
        os.fsync(f)

