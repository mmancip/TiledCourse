#!/bin/bash

res=$(pactl list sink-inputs | grep -i -B23 "application.process.host = \"$1\"")

if [ -n "$res" ]
then
	#id=$(echo -e "$res" | sed -e 's/Sink Input #\(.*\).*/\1/' | head -n 1)
	
	echo -e "$res" | grep -o "Sink Input #[0-9]*" | grep -o "[0-9]*"
fi
