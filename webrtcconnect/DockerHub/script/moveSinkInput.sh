#!/bin/bash

if [ "$#" -eq 2 ]
then
	for id in $(TiledCourse/webrtcconnect/DockerHub/script/searchSinkId.sh $1)
	do
		pactl move-sink-input $id $2
	done
fi
