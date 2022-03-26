#$/bin/bash
#get EDI:SLOT

sys=`dirname $(pwd)`
echo $sys
cd $sys/tools
chmod +x storcli64

edislot=""
edinum=$(./storcli64 /call show|grep SATA|cut -d ' '  -f1)
for i in $edinum
do
	if [ -z "$edislot" ];then
		edislot="$edislot"$i""
	else
		edislot="$edislot,"$i""
	fi
done
#delete all raid befor make raid
./storcli64 /call /vall delete >/dev/null
sleep 3
#Make raid0 for eache hdd
./storcli64 /c0 add vd each type=raid0 drives="$edislot"

sleep 5
lsblk

