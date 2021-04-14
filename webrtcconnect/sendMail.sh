#!/bin/bash

FileName=$1
DateDMY=$2
DateHM=$3
JitsiServer=$4
MailTemplate=$5
SchoolName=$6
SenderName=$7
SenderEmail=$8

if [ "$#" -eq 8 ]
then
	
	OLDIFS="$IFS"

	read line < ${FileName}
	IFS=';' read -a DATA <<< $(echo ${line} | sed 's/ *; */;/g')
	IFS="$OLDIFS"
	
	TeacherName=${DATA[0]}
	TeacherEmail=${DATA[1]}
	

	while read line
	do
		IFS=';' read -a DATA <<< $(echo ${line} | sed 's/ *; */;/g')
		IFS="$OLDIFS"
		
		StudentName=${DATA[0]}
		StudentEmail=${DATA[1]}
		StudentLink="${JitsiServer}/${DATA[2]}"
		

		MESSAGE=$(cat ${MailTemplate} | sed "s/\${DATE_DMY}/${DateDMY//'/'/"\/"}/g;
			s/\${DATE_HM}/${DateHM}/g;
			s/\${TEACHER_NAME}/${TeacherName//'/'/"\/"}/g;
			s/\${STUDENT_NAME}/${StudentName//'/'/"\/"}/g;
			s/\${JITSI_SESSION}/${StudentLink//'/'/"\/"}/g;
			s/\${SCHOOL_NAME}/${SchoolName//'/'/"\/"}/g")
		

		#COMMAND='echo -e "${MESSAGE}" | iconv --from-code=UTF-8 --to-code=ISO-8859-1 | /usr/sbin/sendmail -F "${SenderName}" -f ${SenderEmail} -t ${StudentEmail}'
		echo ${MESSAGE} | iconv --from-code=UTF-8 --to-code=ISO-8859-1 > "mail_${StudentName}.mel"
		COMMAND='/usr/sbin/sendmail -F "${SenderName}" -f ${SenderEmail} -t ${StudentEmail} < "mail_${StudentName}.mel"'

		eval echo ${COMMAND}
		eval ${COMMAND}

		echo -e " Sender: ${SenderName} - ${SenderEmail} to ${StudentEmail}."
		#\n\n${MESSAGE} \n \n ============================= \n"

	done < <(tail -n "+2" ${FileName})
else
	echo " Wrong arguments "
	echo "Usage: "
	echo " $0 FileName Date JitsiServer MailTemplate SchoolName SenderName SenderEmail"
	echo " FileName is the name of the students list in generated_list directory "
	echo " Date [Format: day/month/year hour:minute] is the date when the meeting start "
	echo " JitsiServer is the address of your jitsi server [Format: https://your_jitsi_server_address.com "
	echo " MailTemplate is a template file in template directory "
fi
