# coding=utf-8

# define run cmd in system
import subprocess


def run_cmd(cmd, w=False):
    statusoutput = subprocess.getstatusoutput(cmd)
    # l.write_debug_log("[command: " + cmd + "]" + '\n')
    # l.log("[command: " + cmd + "]", 0 ,w  )
    if statusoutput[0] != 0:
        # l.fail_msg("[command: " + cmd + "]"+ "Fail!")
        # return None
        fail_msg = "[command: " + cmd + "]" + " Fail!"
        return fail_msg
    else:
        # 有可能发送命令成功，但是是设定命令，没有返回值
        if statusoutput[1]:
            return statusoutput[1]
        return None