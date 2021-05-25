#!/bin/bash

HOSTIP=$1

LOGFILE=${HOME}/etherpad_$(date +%F_%H-%M).log

# create a swarm
DATE=$(date +%F_%H-%M)
docker swarm init --advertise-addr=$HOSTIP 2>&1 > ~/docker_swarm_init_${DATE} 
# TODO : propagate swarm if many servers.
#grep "docker swarm join --" ~/docker_swarm_init_${DATE} |xargs -I_ ssh mandelbrot clush -g visu "'~/BAT/mydocker-join _ &'"

# create a network
NETDOMAIN=11.0.0
docker network create --attachable --subnet=$NETDOMAIN.0/24 --gateway=$NETDOMAIN.1 etherpadnet
# TODO : test overlay driver
# --driver overlay

docker pull etherpad/etherpad > $LOGFILE 2>&1
chmod 600 $LOGFILE

choose() { echo -n ${1:$((RANDOM%${#1})):1}; }
secretkey=$({
	      for i in $(seq 1 8); do
		  choose "-._+0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
	      done
	  })
echo Random Password Generated: $secretkey |tee -a $LOGFILE

COMMAND="docker run --detach --name=etherpad --publish 8081:9001 -e \"ADMIN_PASSWORD=$secretkey\" --network=etherpadnet --ip=$NETDOMAIN.254  etherpad/etherpad"
etherpadd=$(docker container ls -a --filter=name=etherpad 2>&1 >/dev/null && docker container ls -a -q --filter=name=etherpad)
if [ -n $etherpadd ]; then
    etherpadip=$(docker inspect $etherpadd --format='{{.NetworkSettings.Networks.etherpadnet.IPAddress}}')
    if [ X"$etherpadip" != X"$NETDOMAIN.254" ]; then
	# Save old etherpad db
	export DATE=$(date +%F_%H-%M-%S)
	OldEtherpad=etherpad_$DATE.tar
	docker export --output=$OldEtherpad etherpad
	tar xf $OldEtherpad opt/etherpad-lite/var/dirty.db
	mv opt/etherpad-lite/var/dirty.db ./dirty_$DATE.db
	rm -rf opt
	docker rm -f -v $etherpadd
	$COMMAND >> $LOGFILE 2>&1
    fi
else
    $COMMAND >> $LOGFILE 2>&1
fi
export APIKEY=$(docker exec -it etherpad cat /opt/etherpad-lite/APIKEY.txt)
echo $APIKEY  |tee -a $LOGFILE

export DATE=$(date +%F_%H-%M-%S)
mkdir EtherpadEnv_${DATE}
#virtualenv-3.5 EtherpadEnv_${DATE}
python3 -m venv EtherpadEnv_${DATE} && source EtherpadEnv_${DATE}/bin/activate && pip3 install -r requirements.txt
