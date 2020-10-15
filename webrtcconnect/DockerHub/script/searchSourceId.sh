#!/usr/bin/env bash

res=$(pactl list source-outputs | grep -i -B23 "application.process.host = \"$1\"")

if [ -n "$res" ]
then
	#id=$(echo -e "$res" | sed -e 's/Source Output #\(.*\).*/\1/' | head -n 1)
	
	echo -e "$res" | grep -o "Source Output #[0-9]*" | grep -o "[0-9]*"
fi
