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
which xdg-open

#XDG_DESKTOP_DIR="$HOME/Desktop"

# https://wiki.archlinux.org/index.php/desktop_entries
# https://specifications.freedesktop.org/desktop-entry-spec/desktop-entry-spec-latest.html
#For example, if $XDG_DATA_DIRS contains the default paths /usr/local/share:/usr/share, then /usr/local/share/applications/org.foo.bar.desktop and /usr/share/applications/org.foo.bar.desktop both have the same desktop file ID org.foo.bar.desktop, but only the first one will be used.
