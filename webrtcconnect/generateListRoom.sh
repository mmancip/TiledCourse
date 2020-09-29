#!/usr/bin/env bash


FileName=$1
IdClassroom=$2
TeacherFirstname=$3
TeacherLastname=$4
TeacherEmail=$5

if [ "$#" -eq 5 ]
then
	echo "${TeacherFirstname} ${TeacherLastname};${TeacherEmail}" > ${IdClassroom}_classroom.list
	cat ${FileName} >> ${IdClassroom}_classroom.list

	echo ${IdClassroom}_classroom.list
else
	echo " Wrong arguments "
	echo "Usage: "
	echo " $0 FileName IdClassroom TeacherFirstname TeacherLastname TeacherEmail "
	echo " FileName is the name of the students list "
	echo " IdClassroom is a unique number to identify the classroom "
	echo " TeacherFirstname is the firstname of the teacher "
	echo " TeacherLastname is the lastname of the teacher "
	echo " TeacherEmail is the e-mail of the teacher "
fi
