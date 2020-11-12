#!/bin/sh

nginx -g "daemon off;" &
echo "export ID_CLASSROOM="${ID_CLASSROOM} >> /etc/profile.d/env_variable.sh
echo "export JITSI_SERVER="${JITSI_SERVER} >> /etc/profile.d/env_variable.sh
echo "export VIDEO_DEVICE="${VIDEO_DEVICE} >> /etc/profile.d/env_variable.sh
echo "export TEACHER_NAME="${TEACHER_NAME} >> /etc/profile.d/env_variable.sh
echo "export TEACHER_EMAIL="${TEACHER_EMAIL} >> /etc/profile.d/env_variable.sh
echo "export DOCKER_NAME="${DOCKER_NAME} >> /etc/profile.d/env_variable.sh
echo "export DATE="${DATE} >> /etc/profile.d/env_variable.sh
/usr/sbin/sshd -D &
exit 0



