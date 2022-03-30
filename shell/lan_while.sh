#!/bin/bash
rmmod pktgen
sleep 5
modprobe pktgen

# chmod +x 2710P.sh
# chmod +x 2715P2.sh
chmod +x pktgen.sh
while true
do
  echo start >/proc/net/pktgen/pgctrl
done