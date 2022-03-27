#coding=utf-8

import subprocess
import sys

out = subprocess.Popen('ls -a', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
print(out.stdout.read().decode('utf-8'))

