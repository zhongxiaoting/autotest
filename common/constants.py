# coding=utf-8
import subprocess
import sys
import os
from serversApp.models import Server

TEST_DIR = os.getcwd()
submission_date = str(Server.objects.values_list("submission_date").first()[0])
sn = str(Server.objects.order_by("-submission_date")[0])
date_time = submission_date.split()
date_dir = date_time[0] + "-" + date_time[1][:8]

# 创建log日志目录
def make_sn_log():
    if not os.path.exists(TEST_DIR + "/log/" + sn):
        subprocess.getstatusoutput("cd log && mkdir " + sn)
    return


def make_date_log():
    if not os.path.exists(TEST_DIR + "/log/" + sn + "/" + date_dir):
        subprocess.getstatusoutput("cd /%s/log/%s && mkdir %s" % (TEST_DIR, sn, date_dir))
    return

# check log dir
make_sn_log()
make_date_log()

###############
# 1. dir and path
###############


LOG_PATH = TEST_DIR + '/log/' + sn + "/" + date_dir
MCE_ECC_LOG_PATH = LOG_PATH + '/mce_ecc.log'
CPU_STRESS_LOG_PATH = LOG_PATH + '/cpu_stress.log'
MEM_STRESS_LOG_PATH = LOG_PATH + '/mem_stress.log'
HDD_STRESS_LOG_PATH = LOG_PATH
LAN_STRESS_LOG_PATH = LOG_PATH + '/lan_stress.log'
ALL_DISKS_LOG_PATH = LOG_PATH + '/disks_all.log'
BLACK_LIST_LOG_PATH = LOG_PATH + '/black_check.log'

###############
# 2. run time
###############
RUN_SECONDS = 60

# wait lan speed time
WAIT_LAN_SPEED_TIME = 10
