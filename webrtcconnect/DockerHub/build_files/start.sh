#!/bin/sh

PULSESERVER_PORT=4000

# All pulseaudio in container listen to 4000
echo 'default-server = tcp:localhost:4000' > /etc/pulse/client.conf

HOME_user=/home/myuser

LOGFILE=${HOME_user}/.vnc/$(hostname).log
touch $LOGFILE
chown -R myuser:myuser ${HOME_user}

main() {
    mkdir ${HOME_user}/.vnc
    # Create the xstartup file
    echo "#!/bin/sh 
fluxbox &
xterm
" >${HOME_user}/.vnc/xstartup
    chmod 755 ${HOME_user}/.vnc/xstartup

    chown -R myuser:myuser ${HOME_user}/.vnc

    log_i "Starting vnc virtual display..."
    launch_vnc
    # log_i "Starting window manager..."
    # launch_window_manager
    log_i "Starting VNC server..."
    run_vnc_server
}

launch_vnc() {

    # Set defaults if the user did not specify envs.
    export DISPLAY=${XVFB_DISPLAY:-:1}
    local screen=${XVFB_SCREEN:-0}
    local resolution=${XVFB_RESOLUTION:-1280x960}
    local timeout=${XVFB_TIMEOUT:-5}

    local passwordArgument='-nopw'

    if [ -n "${VNC_SERVER_PASSWORD}" ]
    then
        local passwordFilePath="${HOME_user}/.vnc/passwd"
        if ! x11vnc -storepasswd "${VNC_SERVER_PASSWORD}" "${passwordFilePath}"
        then
            log_e "Failed to store x11vnc password"
            exit 1
        fi
        passwordArgument=-"-rfbauth ${passwordFilePath}"
        log_i "The VNC server will ask for a password"
    else
        log_w "The VNC server will NOT ask for a password"
    fi
    chown myuser:myuser ${passwordFilePath}
    
    # Start and wait for either Xvfb to be fully up or we hit the timeout.
    su - myuser -c "/usr/bin/vncserver -geometry ${resolution} -fg  2>&1 |tee -a $LOGFILE" &

    #Xvfb ${DISPLAY} -screen ${screen} ${resolution} &
}

launch_window_manager() {
    local timeout=${XVFB_TIMEOUT:-5}

    # Start and wait for either fluxbox to be fully up or we hit the timeout.
    fluxbox &
    local loopCount=0
    until wmctrl -m > /dev/null 2>&1
    do
        loopCount=$((loopCount+1))
        sleep 1
        if [ ${loopCount} -gt ${timeout} ]
        then
            log_e "fluxbox failed to start"
            exit 1
        fi
    done
}

run_vnc_server() {
    
    #x11vnc -display ${DISPLAY} -forever ${passwordArgument} &
    sleep 1
    cd websockify
    python3 /opt/build_pem.py ${VNC_SERVER_PASSWORD} > /tmp/out_ssl 2>&1
    ./run 5900 localhost:5901 > ${HOME_user}/.vnc/out_websockify 2>&1 &
}

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

case ${TYPE} in
	"VM")
		log_i "Started"
		su - myuser -c \
			"ssh -4 -fNT \
			-L${PULSESERVER_PORT}:localhost:${PULSESERVER_PORT} \
			myuser@HUB-CR${ID_CLASSROOM}"
		main
		echo "export DISPLAY=:1.0" >> /etc/profile.d/env_variable.sh
		echo ${ROOM_NAME} >> ${HOME_user}/roomName
		chown myuser:myuser ${HOME_user}/roomName 
		/usr/sbin/sshd -D
		#wait $!
		;;
	"Docker0") 
		log_i "Started"
		su - myuser -c \
			"cat ${HOME_user}/.ssh/classroom${ID_CLASSROOM}.pub >> ${HOME_user}/.ssh/authorized_keys"
		nginx -g "daemon off;" &
		echo "export ID_CLASSROOM="${ID_CLASSROOM} >> /etc/profile.d/env_variable.sh
		echo "export JITSI_SERVER="${JITSI_SERVER} >> /etc/profile.d/env_variable.sh
		echo "export VIDEO_DEVICE="${VIDEO_DEVICE} >> /etc/profile.d/env_variable.sh
		echo "export TEACHER_NAME="${TEACHER_NAME} >> /etc/profile.d/env_variable.sh
		echo "export TEACHER_EMAIL="${TEACHER_EMAIL} >> /etc/profile.d/env_variable.sh
		/usr/sbin/sshd -D
		;;
	*)
		log_e "${TYPE} - Wrong type"
		exit 1
		;;
esac


