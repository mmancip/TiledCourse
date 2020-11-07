#!/bin/bash

NATIVE=$1
IP=$2
LOGIN=$3

DIR_PULSE=${HOME}/.config/pulse
mkdir -p ${DIR_PULSE}
LOCAL_CONF=${DIR_PULSE}/client.conf

# All pulseaudio in container listen to 4000
echo 'default-server = tcp:localhost:4000' > ${LOCAL_CONF}

ssh -4 -fNT -i ${HOME}/.ssh/id_rsa_$IP -L4000:$NATIVE $LOGIN@$IP &

sleep 2

export dev_source=$(pactl info | sed -En 's/Default Source: (.*)/\1/p')
export dev_sink=$(pactl info | sed -En 's/Default Sink: (.*)/\1/p')

pactl load-module module-null-sink sink_name=stu_source sink_properties=device.description="stu_source" &> /dev/null
pactl load-module module-null-sink sink_name=stu_sink sink_properties=device.description="stu_sink" &> /dev/null

sleep 2

pactl load-module module-loopback source=stu_source.monitor sink=${dev_sink} &> /dev/null
pactl load-module module-loopback source=stu_source.monitor sink=stu_sink &> /dev/null
pactl load-module module-loopback source=${dev_source} sink=stu_sink &> /dev/null


