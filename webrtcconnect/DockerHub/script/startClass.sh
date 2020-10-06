#!/usr/bin/env bash

StudentFileName="./students.list"


pactl load-module module-null-sink sink_name=stu_source sink_properties=device.description="stu_source" &> /dev/null
pactl load-module module-null-sink sink_name=stu_sink sink_properties=device.description="stu_sink" &> /dev/null

sleep 2

pactl load-module module-loopback source=stu_source.monitor sink=alsa_output.pci-0000_00_1b.0.analog-stereo &> /dev/null
pactl load-module module-loopback source=stu_source.monitor sink=stu_sink &> /dev/null
pactl load-module module-loopback source=alsa_input.pci-0000_00_1b.0.analog-stereo sink=stu_sink &> /dev/null

sleep 2

i=1

echo "Start classroom"

while read line
do
    IFS=';' read -a DATA <<< $(echo ${line} | sed 's/ *; */;/g')
    IFS="$OLDIFS"
    
    RoomName=${DATA[2]}

    COMMAND_STREAM="ffmpeg -nostdin -nostats -hide_banner -loglevel warning -i rtmp://hub-cr${ID_CLASSROOM}/live/classroom${ID_CLASSROOM} -f v4l2 /dev/video${VIDEO_DEVICE} > /home/myuser/.vnc/out_ffmpeg 2>&1 < /dev/null &"
	
    COMMAND_NAV="export DISPLAY=:1.0; google-chrome \"https://${JITSI_SERVER}/${RoomName}#config.prejoinPageEnabled=false&userInfo.displayName=%22${TEACHER_NAME}%22&userInfo.email=%22${TEACHER_EMAIL}%22&interfaceConfig.DISABLE_VIDEO_BACKGROUND=true&interfaceConfig.SHOW_CHROME_EXTENSION_BANNER=false\" --no-first-run --start-fullscreen --ignore-certificate-errors --use-fake-ui-for-media-stream --test-type --disable-dev-shm-usage > /home/myuser/.vnc/out_chrome 2>&1 &"	
	

    i0=$(printf "%03d" $i)
    VM_NAME="${DOCKER_NAME}_${DATE}_${i0}"

    ssh -fT myuser@${VM_NAME} ${COMMAND_STREAM} &> /dev/null

    # Need a sleep to wait the connection between ffmpeg & the streaming server
    sleep 5
	
    ssh -fT myuser@${VM_NAME} ${COMMAND_NAV} &> /dev/null
	
    #/moveSourceOutput ${VM_NAME} "alsa_input.pci-0000_00_1b.0.analog-stereo"
    #/moveSinkInput ${VM_NAME} "alsa_output.pci-0000_00_1b.0.analog-stereo"

    sleep 2	
	
    ./mute ${VM_NAME}

    sleep 1

    ./audioOff ${VM_NAME}

    echo "Room ${i} started"	
	
    i=$(( ${i}+1 ))

done < <(tail -n "+2" ${StudentFileName})

echo "Classroom started"
