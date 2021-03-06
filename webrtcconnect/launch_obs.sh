#!/bin/bash

HTTP_FRONTEND=$1
RTMPPort=$2
Id=$3

export $( tail -1 out_DISPLAY )
mkdir -p ${HOME}/.config/obs-studio

sed -e 's&"server":.*&"server": "rtmp://'${HTTP_FRONTEND}':'${RTMPPort}'/live"&' \
    -e 's&"key": .*,&"key": "classroom'${Id}'",&' \
    -i obs/tiledviz/service.json

cp -rp obs/tiledviz ${HOME}/.config/obs-studio/basic/profiles/
cp obs/scenes/tiledviz.json ${HOME}/.config/obs-studio/basic/scenes/

nohup obs --profile tiledviz --startstreaming </dev/null &> /dev/null &

exit 0
