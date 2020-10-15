#!/usr/bin/env bash

if [ "$#" -eq 2 ]
then
	for id in $(/searchSourceId $1)
	do
		pactl move-source-output $id $2
	done
fi

