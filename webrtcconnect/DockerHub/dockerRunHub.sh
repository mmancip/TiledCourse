#!/bin/bash

StudentFileName=$1
RTMPPort=$2
JitsiServer=$3
VideoDevice=$4
HostFile=$5
network=$6
domain=$7
init_IP=$8
CLIENT=$9
shift 9
TileSetPort=$1
FRONTEND=$2
DOCKER_NAME=$3
DATE=$4

if [ "$#" -eq 4 ]
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

	myuid=$(ssh ${realhost} id -u)
	mygid=$(ssh ${realhost} id -g)
	DOCKEROPTIONS="-p ${TileSetPort} -h $USER@${FRONTEND} "
	DOCKERARGS='-r 1920x1080 -u '${myuid}' -g '${mygid}' '${DOCKEROPTIONS} 
	SSHPort=$IdClassroom"222"

	ssh ${realhost} bash -c "mkdir /tmp/hub-${DATE} && chmod 700 /tmp/hub-${DATE}"
	ssh ${realhost} docker create \
	    -p 0.0.0.0:${SSHPort}:22 \
	    -p 0.0.0.0:${RTMPPort}:1935 \
	    -e ID_CLASSROOM="${IdClassroom}" \
	    -e VIDEO_DEVICE="${VideoDevice}" \
	    -e JITSI_SERVER="${JitsiServer}" \
	    -e TEACHER_NAME="${TEACHER_NAME}" \
	    -e TEACHER_EMAIL="${TEACHER_EMAIL}" \
	    -e DOCKER_NAME="${DOCKER_NAME}" \
	    -e DATE="${DATE}" \
	    -e DOCKERID="001" \
	    -v /tmp/hub-${DATE}:/home/myuser/.vnc/ \
	    --add-host ${CLIENT} \
	    --net ${network} \
	    --ip=${domain}.$((init_IP-1)) \
	    --hostname HUB-CR${IdClassroom} \
	    --name HUB-CR${IdClassroom} \
	    --rm hub_dev_classroom:1.1 ${DOCKERARGS}

	DIR=/tmp/Hub_$(date +%F_%H-%M-%S)

	ssh ${realhost} mkdir $DIR

	scp ${thispath}/${StudentFileName} ${realhost}:$DIR
	ssh ${realhost} docker cp $DIR/${StudentFileName} \
		HUB-CR${IdClassroom}:/home/myuser/students.list

	ssh ${realhost} rm -rf $DIR

	ssh ${realhost} docker start HUB-CR${IdClassroom}
	exit $?
else
	echo " Wrong arguments "
	echo "Usage: "
	echo " $0 StudentFileName PKFileName  RTMPPort JitsiServer VideoDevice HostFile"
	echo " StudentFileName is the name of the generated list "
	echo " JitsiServer is the address of your jitsi server [Format: your_jitsi_server_address.ext "
	echo " VideoDevice is the number of the attributed video device in /dev/video "
fi

