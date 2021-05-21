#!/bin/bash

StudentFileName=$1
HostFile=$2

if [ "$#" -eq 2 ]
then
	OLDIFS="$IFS"
	
	IdClassroom=$(basename ${StudentFileName} | sed -e 's/\(.*\)_.*\.list/\1/')
	
	read Hostline < ${HostFile}
	realhost=${Hostline% *}
	 
	DATE=$( ssh ${realhost} docker inspect HUB-CR${IdClassroom} |grep DATE= |sed -e 's&.*DATE=\(.*\)",&\1&' )
	echo $DATE
	ssh ${realhost} bash -c "'ls -la /tmp/hub-${DATE}'"
	ssh ${realhost} bash -c "'[ -d /tmp/hub-${DATE} ] && rm -rf /tmp/hub-${DATE}'"
	 
	ssh ${realhost} docker stop HUB-CR${IdClassroom}

else
	echo "Usage: ${0} StudentFileName HostFile"
fi
