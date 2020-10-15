#!/usr/bin/env bash

StudentFileName="./students.list"

audioOff() {
	for id in $(/searchSourceId $1)
	do
		pactl set-source-output-mute $id 1
	done
}


if [ "$#" -eq 1 ]
then
	audioOff $1
else
	i=1

	while read line
	do
		audioOff "VM${i}-CR${ID_CLASSROOM}"
		
		i=$(( ${i}+1 ))
		
	done < <(tail -n "+2" ${StudentFileName})

fi
