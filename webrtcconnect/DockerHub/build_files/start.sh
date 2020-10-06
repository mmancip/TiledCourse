#!/bin/sh

HOME_user=/home/myuser
mkdir -p ${HOME_user}/.vnc
chown -R myuser:myuser ${HOME_user}

LOGFILE=${HOME_user}/.vnc/$(hostname).log
touch $LOGFILE
chown -R myuser:myuser ${HOME_user}


log_i() {
    log "[INFO] ${@}" >> $LOGFILE
}

log_w() {
    log "[WARN] ${@}" >> $LOGFILE
}

log_e() {
    log "[ERROR] ${@}" >> $LOGFILE
}

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ${@}"
}

control_c() {
    echo ""
    exit
}

#trap control_c SIGINT SIGTERM SIGHUP

log_i "Started"
nginx -g "daemon off;" &
echo "export ID_CLASSROOM="${ID_CLASSROOM} >> /etc/profile.d/env_variable.sh
echo "export JITSI_SERVER="${JITSI_SERVER} >> /etc/profile.d/env_variable.sh
echo "export VIDEO_DEVICE="${VIDEO_DEVICE} >> /etc/profile.d/env_variable.sh
echo "export TEACHER_NAME="${TEACHER_NAME} >> /etc/profile.d/env_variable.sh
echo "export TEACHER_EMAIL="${TEACHER_EMAIL} >> /etc/profile.d/env_variable.sh
echo "export DOCKER_NAME="${DOCKER_NAME} >> /etc/profile.d/env_variable.sh
echo "export DATE="${DATE} >> /etc/profile.d/env_variable.sh
/usr/sbin/sshd -D




