#!/bin/bash

StudentFileName="./students.list"

audioOn() {
	for id in $(TiledCourse/webrtcconnect/DockerHub/script/searchSourceId.sh $1)
	do
		pactl set-source-output-mute $id 0
	done
}


if [ "$#" -eq 1 ]
then
	audioOn $1
else
	i=1

	while read line
	do
		audioOn "VM${i}-CR${ID_CLASSROOM}"
		
		i=$(( ${i}+1 ))
		
	done < <(tail -n "+2" ${StudentFileName})

fi
