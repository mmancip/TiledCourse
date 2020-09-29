#!/bin/bash

StudentFileName=$1
PKFileName=$2
RTMPPort=$3
JitsiServer=$4
VideoDevice=$5
HostFile=$6

if [ "$#" -eq 6 ]
then

	OLDIFS="$IFS"
	
	
	IdClassroom=$(basename ${StudentFileName} | sed -e 's/\(.*\)_.*\.list/\1/')

	read line < ${StudentFileName}
	IFS=';' read -a DATA <<< $(echo ${line} | sed 's/ *; */;/g')
	IFS="$OLDIFS"
	
	TEACHER_NAME=${DATA[0]}
	TEACHER_EMAIL=${DATA[1]}
	
	TEACHER_NAME="${TEACHER_NAME// /}"

	#################################
	# START HUB DOCKER

	read Hostline < ${HostFile}
	realhost=${Hostline% *}
	thispath=$(dirname ${BASH_SOURCE[0]})

	SSHPort=$IdClassroom"222"
	ssh ${realhost} docker create -p 0.0.0.0:${SSHPort}:22 \
		-p 0.0.0.0:${RTMPPort}:1935 \
		-e ID_CLASSROOM="${IdClassroom}" \
		-e VIDEO_DEVICE="${VideoDevice}" \
		-e JITSI_SERVER="${JitsiServer}" \
		-e TEACHER_NAME="${TEACHER_NAME}" \
		-e TEACHER_EMAIL="${TEACHER_EMAIL}" \
		--net classroom${IdClassroom} \
		--hostname HUB-CR${IdClassroom} \
		--name HUB-CR${IdClassroom} \
		--rm hub_dev_classroom:1.1

	DIR=/tmp/Hub_$(date +%F_%H-%M-%S)

	ssh ${realhost} mkdir $DIR

	scp ${thispath}/${StudentFileName} ${realhost}:$DIR
	ssh ${realhost} docker cp $DIR/${StudentFileName} \
		HUB-CR${IdClassroom}:/home/myuser/students.list

	scp ${PKFileName} ${realhost}:$DIR
	ssh ${realhost} docker cp $DIR/${PKFileName} \
		HUB-CR${IdClassroom}:/home/myuser/.ssh/classroom${IdClassroom}.pub
	
	ssh ${realhost} rm -rf $DIR

	ssh ${realhost} docker start HUB-CR${IdClassroom}
	exit $?
else
	echo " Wrong arguments "
	echo "Usage: "
	echo " $0 StudentFileName PKFileName  RTMPPort JitsiServer VideoDevice HostFile"
	echo " StudentFileName is the name of the generated list "
	echo " PKFileName is the name of the publickey "
	echo " JitsiServer is the address of your jitsi server [Format: your_jitsi_server_address.ext "
	echo " VideoDevice is the number of the attributed video device in /dev/video "
fi

