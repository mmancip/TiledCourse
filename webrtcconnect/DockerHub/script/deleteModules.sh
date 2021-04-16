#!/bin/bash

for id in $(pactl list modules | grep -B1 "null-sink\|loopback" | grep -o "[0-9]*")
do 
	pactl unload-module $id &> /dev/null 
done

for id in $(seq 1 $(( $(wc -l ./students.list | grep -o "^[0-9]*") -1)) )
do 
	ssh myuser@VM${id}-CR${ID_CLASSROOM} "/killVisio" 2>&1 < /dev/null
done
