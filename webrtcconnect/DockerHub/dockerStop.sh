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

	i=1

else
	echo "Usage: ${0} StudentFileName "
fi
