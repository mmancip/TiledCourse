#!/bin/bash

FileName=$1

if [ "$#" -eq 1 ]
then

	MailTemplate="template/Invite.template"
	
	
	OLDIFS="$IFS"
	IFS=';' read -a DATA <<< $(cat ${FileName} | sed 's/ *; */;/g')
	IFS="$OLDIFS"

	OriginalList=${DATA[0]}
	IdClassroom=${DATA[1]} # Identifiant de la classe
	TeacherFirstname=${DATA[2]}
	TeacherLastname=${DATA[3]}
	TeacherEmail=${DATA[4]}
	DateDMY=${DATA[5]} # Jour du cours
	DateHM=${DATA[6]} # Heure du cours
	JitsiServer=${DATA[7]} # Adresse Jitsi sans https://
	SchoolName=${DATA[8]} # Nom de l'ecole
	SenderName=${DATA[9]} # Nom de l'emetteur
	SenderEmail=${DATA[10]} # Adresse email de l'emetteur
	

	GeneratedList=$(./generateListRoom.sh \
		${OriginalList} \
		${IdClassroom} \
		${ClassroomName} \
		${TeacherFirstname} \
		${TeacherLastname} \
		${TeacherEmail})

	./sendMail.sh \
		${GeneratedList} \
		${DateDMY} \
		${DateHM} \
		${JitsiServer} \
		${MailTemplate} \
		${SchoolName} \
		${SenderName} \
		${SenderEmail}

else
	echo " Wrong arguments "
	echo "Usage: "
	echo " $0 FileName"
	echo " FileName which contains the fast configuration "

fi
