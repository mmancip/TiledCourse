#!/bin/bash

StudentFileName="./students.list"

unmute() {
	for id in $(/searchSinkId $1)
	do
		pactl set-sink-input-mute $id 0
	done
}

attributeDevice() {
	if [ $2 == "sink" ]
	then
		TiledCourse/webrtcconnect/DockerHub/script/moveSourceOutput.sh $1 "stu_sink.monitor"
		TiledCourse/webrtcconnect/DockerHub/script/moveSinkInput.sh $1 "alsa_output.pci-0000_00_1b.0.analog-stereo"
	elif [ $2 == "source" ]
	then
		TiledCourse/webrtcconnect/DockerHub/script/moveSourceOutput.sh $1 "alsa_input.pci-0000_00_1b.0.analog-stereo"
		TiledCourse/webrtcconnect/DockerHub/script/moveSinkInput.sh $1 "stu_source"	
	fi
}


if [ "$#" -eq 1 ]
then
	if [ -n "$1" ]
	then
		i=1

		while read line
		do
			VM_NAME="VM${i}-CR${ID_CLASSROOM}"
			
			if [ ${VM_NAME} != $1 ]
			then
				attributeDevice "${VM_NAME}" "sink"
			else
				attributeDevice "${VM_NAME}" "source"
			fi
			
			i=$(( ${i}+1 ))

		done < <(tail -n "+2" ${StudentFileName})

		unmute $1
	fi
else
	i=1

	while read line
	do
		unmute "VM${i}-CR${ID_CLASSROOM}"
		
		i=$(( ${i}+1 ))
		
	done < <(tail -n "+2" ${StudentFileName})

fi
