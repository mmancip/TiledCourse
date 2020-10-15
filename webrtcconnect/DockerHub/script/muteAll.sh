#!/usr/bin/env bash

StudentFileName="./students.list"

attributeDevice() {
	/moveSourceOutput $1 "alsa_input.pci-0000_00_1b.0.analog-stereo"

	/moveSinkInput $1 "alsa_output.pci-0000_00_1b.0.analog-stereo"
}

mute() {
	for id in $(/searchSinkId $1)
	do
		attributeDevice $1
		pactl set-sink-input-mute $id 1
	done
}


if [ "$#" -eq 1 ]
then
	mute $1
else
	i=1

	while read line
	do
		mute "VM${i}-CR${ID_CLASSROOM}"

		i=$(( ${i}+1 ))
		
	done < <(tail -n "+2" ${StudentFileName})

fi
