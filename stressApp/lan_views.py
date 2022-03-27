# coding=utf-8
import datetime
import os
import re
import sys
import time
import threading


def run_item(self):
    self.start_lan_run()
    self.check_network_link()
    self.check_speed()


def start_lan_run(self):
    write_log("================= " + " Begin Lan Stress Check " + get_local_time_string() + " =================")
    # cv.remove_log(c.LAN_STRESS_LOG_PATH)
    lan_while = threading.Thread(target=self.lan_while)
    # lan_while.setDaemon(True)
    lan_while.start()
    time.sleep(10)
    pktgen = self.run_cmd("cd /home/hw_stress/lan_stress && ./pktgen.sh")
    write_log(pktgen)


def lan_while(self):
    self.run_cmd("cd /home/hw_stress/lan_stress && chmod +x lan_while.sh && ./lan_while.sh")
    print("lan_while.sh End!")
    return


# choose server models
def check_product_name(self):
    product_name_ = self.run_cmd("ipmitool fru print | grep 'Product Name' ")
    product_name = product_name_.rsplit(":")[1]
    name = product_name.strip()
    return name


# Check whether the network cable is connected
def check_network_link(self):
    enps = self.run_cmd('ls /sys/class/net | grep -E "enp[a-z0-9]+f[0-1]$"').split('\n')
    for enp in enps:
        eth_infor = self.run_cmd("ethtool {}".format(enp))
        link_detected = re.search("Link detected: (.*)", eth_infor).group()
        link_detected = link_detected.rsplit(":")[1].strip()
        # full_speed = re.search("Speed: (.*)", eth_infor).group()
        # full_speed = full_speed.rsplit(":")[1].strip()
        # full_speed = re.search(r"\d+", full_speed).group()
        if link_detected == 'yes':
            write_log("->>> {} is link! Formal ".format(enp))
        else:
            write_log("->>> {} is not link! Error ".format(enp))
            self.stress_fail()
    return link_detected


def check_speed(self):
    count = 1
    # duration_time = 50
    day_time = datetime.datetime.now() + datetime.timedelta(seconds=c.RUN_SECONDS)
    day_time = day_time.strftime("%Y-%m-%d %H:%M:%S")
    enps = self.run_cmd('ls /sys/class/net | grep -E "enp[a-z0-9]+f[0-1]$"').split('\n')
    while True:
        now_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if day_time <= now_time:
            break
        time.sleep(c.WAIT_LAN_SPEED_TIME)
        write_log("=============== NO." + str(
            count) + " Begin Network Speech Check  " + get_local_time_string() + " =================")
        for enp in enps:
            eth_infor = self.run_cmd("ethtool {}".format(enp))
            full_speed = re.search("Speed: (.*)", eth_infor).group()
            full_speed = full_speed.rsplit(":")[1].strip()
            aa = 1
            while aa:
                enp_result = self.run_cmd("cat /proc/net/pktgen/" + enp)
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
                        self.stress_fail()
                else:
                    write_log("->>> {} speed is {}Mb/s, not up to the mark! Error".format(enp, speed))
                    self.stress_fail()
            elif full_speed == "10000Mb/s":
                if int(speed) > 0:
                    write_log("->>> {} speed is {}Mb/s, Formal!".format(enp, speed))
                    if int(errors) != 0:
                        write_log("->>> {} have {} errors !".format(enp, errors))
                        self.stress_fail()
                else:
                    write_log("->>> {} speed is {}Mb/s, not up to the mark! Error".format(enp, speed))
                    self.stress_fail()
            elif full_speed == "25000Mb/s":
                if int(speed) > 0:
                    write_log("->>> {} speed is {}Mb/s, Formal!".format(enp, speed))
                    if int(errors) != 0:
                        write_log("->>> {} have {} errors !".format(enp, errors))
                        self.stress_fail()
                else:
                    write_log("->>> {} speed is {}Mb/s, not up to the mark! Error".format(enp, speed))
                    self.stress_fail()
            else:
                write_log("->>> {} speed is {},not achieved!".format(enp, full_speed))
        write_log(
            "============================= NO." + str(count) + " End  ==========================================")
        count += 1
    self.lan_formal_quit()
    return


def write_log(s):
    with open(c.LAN_STRESS_LOG_PATH, 'a+') as f:
        print(s)
        f.write(str(s) + '\n')
        f.flush()
        os.fsync(f)


def get_local_time_string():
    return time.strftime('%04Y-%m-%d %H:%M:%S', time.localtime(time.time()))
