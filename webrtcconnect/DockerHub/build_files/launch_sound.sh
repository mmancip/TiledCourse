#!/bin/bash

NATIVE=$1
IP=$2
LOGIN=$3

DIR_PULSE=${HOME}/.config/pulse
mkdir -p ${DIR_PULSE}
LOCAL_CONF=${DIR_PULSE}/client.conf

#pulseaudio --daemonize=no &

# All pulseaudio in container listen to 4000
echo 'default-server = tcp:localhost:4000' > ${LOCAL_CONF}

ssh -4 -fNT -L4000:$NATIVE $LOGIN@$IP &


