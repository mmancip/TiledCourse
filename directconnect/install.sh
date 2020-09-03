#!/bin/bash

# Site parameters :
if [ ! -f ./site_config ]; then
    sed -e "s@\[SITE\]@#!/bin/bash@" ./site_config.ini > /tmp/site_config
    . /tmp/site_config
    mkdir -p ${INSTALLPATH}
    mv /tmp/site_config ${INSTALLPATH}
else
    . ./site_config
    mkdir -p ${INSTALLPATH}
fi

sed -e "s&/opt/nfs/mdls/TiledViz&$INSTALLPATH&" vnc.desktop > ${INSTALLPATH}/vnc.desktop
chmod a+x ${INSTALLPATH}/vnc.desktop
sed -e "s&/opt/nfs/mdls/TiledViz&$INSTALLPATH&" vncoff.desktop > ${INSTALLPATH}/vncoff.desktop
chmod a+x ${INSTALLPATH}/vncoff.desktop
cp ./unTiledViz.png ./TiledViz.png ./del_vnc ./launch_vnc $INSTALLPATH

# test xdg-open (linux MIME application)
#which xdg-open

# TODO : INSTALLPATH on HTTP_FRONTEND server
cd ${INSTALLPATH}
git clone https://github.com/novnc/websockify.git websockify

