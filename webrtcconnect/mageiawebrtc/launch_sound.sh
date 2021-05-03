#!/bin/bash

DIR_PULSE=${HOME}/.config/pulse
mkdir -p ${DIR_PULSE}

LOCAL_CONF=${DIR_PULSE}/client.conf

RET=1
if [[ -e ${LOCAL_CONF} ]] ; then
    cp ${LOCAL_CONF} ${LOCAL_CONF}_sav
    sed -e 's&default-server = .*&default-server = tcp:localhost:4000' > ${LOCAL_CONF}
    RET=$?
fi
if [ $RET -gt 0 ]; then
    echo 'default-server = tcp:localhost:4000' >> ${LOCAL_CONF}
fi

killall -9 pulseaudio
pulseaudio --daemonize=no &

