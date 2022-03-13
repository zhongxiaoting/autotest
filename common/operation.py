# coding=utf-8

import os
import time
import subprocess
from common import information as fn
from utils import handle as h

# 获取当前目录
cwd_path = os.getcwd()

sn_path = fn.get_recent_sn()

# log文件目录

log_dir_log = cwd_path + '/log'

sn_dir_log = cwd_path + "/log/" + sn_path


# make an SN folder to save logs
def make_sn_dir():
    if not os.path.exists(sn_dir_log):
        make_dir = h.run_cmd('cd % && mkdir %s' % (log_dir_log, sn_path))
        return sn_path
    return sn_path


# save logs for each run
def make_date_log_dir():
    make_sn_dir()
    date_dir = str(get_local_time_string())
    if not os.path.exists(sn_dir_log + '/' + date_dir):
        make_date_dir = h.run_cmd("cd %s && mkdir %s" % (sn_dir_log, date_dir))
        return date_dir
    return date_dir


# 获取当前执行的时间
def get_local_time_string():
    return time.strftime('%04Y-%m-%d %H:%M:%S', time.localtime(time.time()))
