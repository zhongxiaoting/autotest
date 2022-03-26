# coding=utf-8

import sys
import os
from serversApp.models import Server

submission_date = str(Server.objects.values_list("submission_date").first()[0])
sn = str(Server.objects.order_by("-submission_date")[0])
date_time = submission_date.split()
date_dir = date_time[0] + "-" + date_time[1][:8]

###############
# 1. dir and path
###############

TEST_DIR = os.getcwd()
LOG_PATH = TEST_DIR + '/log/' + sn + "/" + date_dir
MCE_ECC_LOG_PATH = LOG_PATH + '/mce_ecc.log'
CPU_STRESS_LOG_PATH = LOG_PATH + '/cpu_stress.log'
MEM_STRESS_LOG_PATH = LOG_PATH + '/mem_stress.log'
HDD_STRESS_LOG_PATH = LOG_PATH
LAN_STRESS_LOG_PATH = LOG_PATH + '/lan_stress.log'
ALL_DISKS_LOG_PATH = LOG_PATH + '/disks_all.log'

###############
# 2. run time
###############
RUN_SECONDS = 60
