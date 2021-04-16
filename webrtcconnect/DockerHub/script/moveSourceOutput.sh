#!/bin/bash

if [ "$#" -eq 2 ]
then
	for id in $(TiledCourse/webrtcconnect/DockerHub/script/searchSourceId.sh $1)
	do
		pactl move-source-output $id $2
	done
fi

