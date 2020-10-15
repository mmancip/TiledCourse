#!/usr/bin/env bash

if [ "$#" -eq 2 ]
then
	for id in $(/searchSinkId $1)
	do
		pactl move-sink-input $id $2
	done
fi
