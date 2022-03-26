# coding=utf-8
import re
from utils import handle as h

# 获取所有sd*,nvme*硬盘
def get_all_disk():
    sd_disk = h.run_cmd('find /dev/ -name "sd*" | grep -E "sd[a-z]$" | sort ')
    nvme_disk = h.run_cmd('find /dev/ -name "nvme*" | grep -E "nvme[0-9][a-z][0-9]$" | sort ')
    if nvme_disk['cmd_infor']:
        all_disk = sd_disk['cmd_infor'] + "\n" + nvme_disk['cmd_infor']
    else:
        all_disk = sd_disk['cmd_infor']
    return all_disk


# 移除系统盘的所有盘
def remove_os_disk():
    all_disk = get_all_disk().split()
    os_disk = get_os_disk()
    # print(all_disk)
    for disk in all_disk:
        os_disk_ = re.findall(os_disk, disk)
        for os in os_disk_:
            if os == os_disk:
                remove_os = "/dev/" + os_disk
                all_disk.remove(remove_os)
    return all_disk


# 获取到系统盘
def get_os_disk():
    i = 0
    os_disk = ""
    list_disk = []
    all_disk = h.run_cmd("lsblk")
    disk_list = all_disk['cmd_infor'].split("\n")
    # print(one_disk)
    for disk in disk_list:
        units = disk.split()
        # print(units)
        list_disk.append(units)
        if len(list_disk[i]) == 7:
            if list_disk[i][-1] == '/boot':
                os_num = int(list_disk[i][0][-1])
                os_disk = list_disk[i - os_num][0]
        i += 1
    return os_disk



