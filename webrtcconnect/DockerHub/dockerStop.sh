#!/usr/bin/env bash

StudentFileName=$1
HostFile=$2

if [ "$#" -eq 2 ]
then
	OLDIFS="$IFS"
	
	IdClassroom=$(basename ${StudentFileName} | sed -e 's/\(.*\)_.*\.list/\1/')
	
	read Hostline < ${HostFile}
	realhost=${Hostline% *}
	 
	ssh ${realhost} docker stop HUB-CR${IdClassroom}
	DATE=$( ssh ${realhost} docker inspect HUB-CR${IdClassroom} |grep DATE= |sed -e 's&.*DATE=&&' )
	echo $DATE
	ssh ${realhost} bash -c "'ls -la /tmp/hub-${DATE}'"
	ssh ${realhost} bash -c "'[ -d /tmp/hub-${DATE} ] && rm -rf /tmp/hub-${DATE}'"
	i=1

else
	echo "Usage: ${0} StudentFileName HostFile"
fi
