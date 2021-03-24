#!/bin/bash

LOGFILE=${HOME}/etherpad_$(date +%F_%H-%M).log
docker pull etherpad/etherpad > $LOGFILE 2>&1
chmod 600 $LOGFILE

choose() { echo -n ${1:$((RANDOM%${#1})):1}; }
secretkey=$({
	      for i in $(seq 1 8); do
		  choose "-._+0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
	      done
	  })
echo Random Password Generated: $secretkey |tee -a $LOGFILE

docker run --detach --name=etherpad --publish 8081:9001 -e "ADMIN_PASSWORD=$secretkey" etherpad/etherpad >> $LOGFILE 2>&1
export APIKEY=$(docker exec -it etherpad cat /opt/etherpad-lite/APIKEY.txt)
echo $APIKEY  |tee -a $LOGFILE

export DATE=$(date +%F_%H-%M-%S)
mkdir EtherpadEnv_${DATE}
#virtualenv-3.5 EtherpadEnv_${DATE}
virtualenv3 EtherpadEnv_${DATE} && source EtherpadEnv_${DATE}/bin/activate && pip3 install -r requirements.txt
