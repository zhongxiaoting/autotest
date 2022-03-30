#!/bin/bash
#rmmod pktgen
#sleep 5
#modprobe pktgen

one_sd="Speed: 1000Mb/s"
ten_sd="Speed: 10000Mb/s"
tf_sd="Speed: 25000Mb/s"

ip=1
count=0
j=0

i=0
declare -a array_mac
for enp in `ls /sys/class/net | grep -E "enp[a-z0-9]+f[0-1]$"`
do
  mac=$(ifconfig $enp |grep -Eo '([[:xdigit:]]{1,2}:){5}[[:xdigit:]]{1,2}')
  #echo $mac
  array_mac[$i]=$mac
  echo $enp: ${array_mac[$i]}
  i=$(($i+1))
done

for i in `ls /sys/class/net | grep -E "enp[a-z0-9]+f[0-1]$"`
do
#   echo $mac
    ifconfig $i mtu 9000
    speed=$(ethtool $i |grep "Speed: ")
    echo "->>> $i:$speed"
    speed=$(echo $speed)
        if [ "$speed" = "$ten_sd" -o "$speed" = "$tf_sd" -o "$speed" = "$one_sd" ];then
            # echo "->>> start to check Lan in this time"
            echo rem_device_all >/proc/net/pktgen/kpktgend_$count
            echo add_device $i > /proc/net/pktgen/kpktgend_$count
            echo count 10000 > /proc/net/pktgen/$i
            echo clone_skb 1000 >/proc/net/pktgen/$i
            echo pkt_size 9000 >/proc/net/pktgen/$i

            echo dst 10.11.11.$ip >/proc/net/pktgen/$i
            b=$(($count%2))
            if [ $b -eq 0 ];then
              echo dst_mac ${array_mac[$(($j+1))]} >/proc/net/pktgen/$i
            else
              echo dst_mac ${array_mac[$(($j-1))]} >/proc/net/pktgen/$i
            fi
            ip=`expr $ip + 1`
            count=$(($count+1))
            j=`expr $j + 1`

        else
            echo "->>> $i speed is not 1000Mb/s、10000Mb/s or 25000Mb/s, nothing to do"
        fi
done


