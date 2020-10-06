#!/bin/bash

HTTP_FRONTEND=$1
Id=$2

export DISPLAY=$( ./get_DISPLAY.sh )
mkdir -p ${HOME}/.config/obs-studio

sed -e 's&"server":.*&"server": "rtmp://'${HTTP_FRONTEND}':56000/live"&' \
    -e 's&"key": .*,&"key": "classroom'${Id}'",&' \
    -i obs/tiledviz/service.json

cp -rpf obs/tiledviz ${HOME}/.config/obs-studio/basic/profiles/
cp obs/basic/scenes/tiledviz.json ${HOME}/.config/obs-studio/scenes/

obs --profile tiledviz --startstreaming 
