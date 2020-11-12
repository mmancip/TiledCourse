#!/bin/bash

RESOL=3840x2160

ARGS=$@
#echo ${ARGS[@]}

#1920x1080
myUID=1000
myGID=1000
myPORT=55555
myFront=myuser@localhost
if [ -z "$1" ]; then
	echo Usage: $0 [-r RESOL_XxRESOL_Y] -u UID [-g GID] -p PORTserver -h Frontend
	exit 1
else
    IFS=' ' read -ra ADDR <<< "$ARGS"
    lenADDR=${#ADDR[@]}
    if [ ${lenADDR} -gt 0 ]; then
	i=0
	while [ $i -lt ${lenADDR} ]; do
	    case "${ADDR[$i]}" in
		'-r') 
		    RESOL=${ADDR[$((i+1))]};;
		'-u')
		    myUID=${ADDR[$((i+1))]};;
		'-g')
		    myGID=${ADDR[$((i+1))]};;
		'-p')
		    myPORT=${ADDR[$((i+1))]};;
		'-h')
		    myFront=${ADDR[$((i+1))]};;
		'.*')
		    myGID=${myUID}
	    esac
	    i=$((i+2));
	done
    fi
fi


groupadd -g ${myGID} myuser
useradd -r -u ${myUID} -g myuser myuser
#adduser --disabled-password --gecos "My User" --uid 1000 myuser

HOME_user=/home/myuser
if [ -d ${HOME_user} ]; then
    mkdir -p ${HOME_user}/.vnc
fi 
chmod 700 ${HOME_user}/.vnc
chown -R myuser:myuser ${HOME_user}

chmod 600 ${HOME_user}/.ssh/config

LOGFILE=${HOME_user}/.vnc/$(hostname).log
touch $LOGFILE
chown myuser:myuser $LOGFILE

echo Random Password Generated: nopasshub > $LOGFILE

echo "start.sh with args : ${ARGS[*]}" >> $LOGFILE


chown -R myuser:myuser ${HOME_user}

echo export DOCKERID=$DOCKERID >> ${HOME_user}/.bashrc

/opt/start-hub.sh

# Run the client_python
cd
echo $( hostname )
echo "export HOSTNAME="${HOSTNAME} >> /etc/profile.d/env_variable.sh

su - myuser -c "/opt/client_python ${DOCKERID} ${myPORT} ${myFront}"
# while true; do
#     sleep 100
# done
