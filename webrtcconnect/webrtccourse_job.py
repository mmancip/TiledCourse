#!/usr/bin/env python
# -*- coding: utf-8 -*-

import configparser
import sys,os,time
import code
import argparse
import re, datetime
import inspect

sys.path.append(os.path.realpath('/TiledViz/TVConnections/'))
from connect import sock

import json
import csv

SITE_config='./site_config.ini'
CASE_config="./case_config.ini"

# repoDockerWebRTC="https://github.com/mmancip/"
DockerWebRTC="DockerWebRTC"


if __name__ == '__main__':
    #def job(globals,locals)
    actions_file=open("/home/myuser/actions.json",'r')
    tiles_actions=json.load(actions_file)

    config = configparser.ConfigParser()
    config.optionxform = str

    config.read(SITE_config)

    NOVNC_URL=config['SITE']['NOVNC_URL']

    HTTP_FRONTEND=config['SITE']['HTTP_FRONTEND']

    GPU_FILE=config['SITE']['GPU_FILE']

    SERVER_JITSI=config['SITE']['SERVER_JITSI']
    
    config.read(CASE_config)

    CASE=config['CASE']['CASE_NAME']

    CONFIGPATH=config['CASE']['CONFIGPATH']	
    # OriginalList=${DATA[0]}
    # IdClassroom=${DATA[1]} # Identifiant de la classe
    # TeacherFirstname=${DATA[2]}
    # TeacherLastname=${DATA[3]}
    # TeacherEmail=${DATA[4]}
    # DateDMY=${DATA[6]} # Jour du cour
    # DateHM=${DATA[7]} # Heure du cour
    # JitsiServer=${DATA[8]} # Adresse Jitsi sans https://
    # SchoolName=${DATA[9]} # Nom de l'ecole
    # SenderName=${DATA[10]} # Nom de l'emetteur
    # SenderEmail=${DATA[11]} # Adresse email de l'emetteur

    SOCKETdomain=config['CASE']['SOCKETdomain']

    # reader csv sur le configpath
    dataclass=[]
    with open(CONFIGPATH) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=';')
        count_lines=0
        for row in csv_reader:
            dataclass.append(row)
            print(", ".join(row))
            count_lines=count_lines+1

    FILEPATH=dataclass[0][0]
    IdClassroom=dataclass[0][1]
    
    def countlines(filename):
        f = open(filename) 
        lines = 0
        buf_size = 1024 * 1024
        read_f = f.read # loop optimization
        buf = read_f(buf_size)
        while buf:
            lines += buf.count('\n')
            buf = read_f(buf_size)
        return lines

    NUM_STUDENTS=countlines(FILEPATH)
    print("Number of students :"+str(NUM_STUDENTS))
    
    CreateTS='create TS='+TileSet+' Nb='+str(NUM_STUDENTS)
    client.send_server(CreateTS)
    
    NOM_FICHIER_ETUDIANT_GENERE=IdClassroom+"_classroom.list"

    # IdClassroom < 65 ! car num port < 65535
    RTMPPORT=SOCKETdomain+"000"

    # get TiledCourse package from Github
    # os.system("git clone "repoDockerWebRTC+DockerWebRTC+".git")
    COMMAND_TAR="tar xfz "+DockerWebRTC+".tgz"
    print("command_tar : "+COMMAND_TAR)
    os.system(COMMAND_TAR)
    
    #os.system("cp "+FILECLASS+" "+DockerWebRTC+"/original_list") => cf remarque README.md

    COMMAND_MAIL="cd DockerWebRTC; ./fastGenerateMail.sh "+CONFIGPATH
    print("command_mail :"+COMMAND_MAIL)
    os.system(COMMAND_MAIL)

    # get TiledCourse package from Github
    COMMAND_GIT="git clone https://github.com/mmancip/TiledCourse.git"
    print("command_git : "+COMMAND_GIT)
    os.system(COMMAND_GIT)
    
    # Send CASE and SITE files
    try:
#        send_file_server(client,TileSet,"TiledCourse/webrtcconnect", "build_nodes_file", JOBPath)
        send_file_server(client,TileSet,".", "build_nodes_file", JOBPath)
        
        send_file_server(client,TileSet,".", CASE_config, JOBPath)
        CASE_config=os.path.join(JOBPath,os.path.basename(CASE_config))
        send_file_server(client,TileSet,".", SITE_config, JOBPath)
        SITE_config=os.path.join(JOBPath,os.path.basename(SITE_config))

        send_file_server(client,TileSet,".", CONFIGPATH, JOBPath)
        send_file_server(client,TileSet,".", FILEPATH, JOBPath)
        send_file_server(client,TileSet,"DockerWebRTC/generated_list", NOM_FICHIER_ETUDIANT_GENERE, JOBPath)
        send_file_server(client,TileSet,".", "list_hostsgpu", JOBPath)
        send_file_server(client,TileSet,"DockerWebRTC", "dockerRunHub.sh", JOBPath)
        send_file_server(client,TileSet,"DockerWebRTC", "dockerRunVm.sh", JOBPath)
        #send_file_server(client,TileSet,".", dockerCreateNetwork.sh, JOBPath)
        #send_file_server(client,TileSet,".", dockerConnection.sh, JOBPath)
        send_file_server(client,TileSet,"DockerWebRTC", "dockerStop.sh", JOBPath)

    except:
        print("Error sending files !")
        traceback.print_exc(file=sys.stdout)
        try:
            code.interact(banner="Try sending files by yourself :",local=dict(globals(), **locals()))
        except SystemExit:
            pass


        
    # ???? Comment 
    VideoDeviceNumber=str(0)
    
    def Run_Hub():
        COMMAND='launch TS='+TileSet+" "+JOBPath+' ./dockerRunHub.sh '+NOM_FICHIER_ETUDIANT_GENERE+' '+HomeFront+'/.ssh/id_rsa.pub '+RTMPPORT+' '+SERVER_JITSI+' '+VideoDeviceNumber+' '+GPU_FILE
    
        print("\nCommand RunHub : "+COMMAND)
        client.send_server(COMMAND)

        #code.interact(local=locals())
        print("Out of launch Hub : "+ str(client.get_OK()))
    Run_Hub()

    def Run_Vm():
        COMMAND='launch TS='+TileSet+" "+JOBPath+' ./dockerRunVm.sh '+NOM_FICHIER_ETUDIANT_GENERE+' '+VideoDeviceNumber+' '+GPU_FILE+' '+SOCKETdomain
    
        print("\nCommand RunVm : "+COMMAND)
        client.send_server(COMMAND)

        #code.interact(local=locals())
        print("Out of launch Vm : "+ str(client.get_OK()))
    Run_Vm()
    
    # Build nodes.json file from new dockers list
    def build_nodes_file():
        print("Build nodes.json file from new dockers list.")
        COMMAND='launch TS='+TileSet+" "+JOBPath+' chmod u+x build_nodes_file '
        client.send_server(COMMAND)
        print("Out of chmod build_nodes_file : "+ str(client.get_OK()))

        COMMAND='launch TS='+TileSet+" "+JOBPath+' ./build_nodes_file '+CASE_config+' '+SITE_config+' '+TileSet
        print("\nCommand dockers : "+COMMAND)

        client.send_server(COMMAND)
        print("Out of build_nodes_file : "+ str(client.get_OK()))
        os.system('rm -f ./nodes.json')
        get_file_client(client,TileSet,JOBPath,"nodes.json",".")

    build_nodes_file()

    # # Launch Server for commands from FlaskDock
    # print("GetActions=ClientAction("+str(connectionId)+",globals=dict(globals()),locals=dict(**locals()))")
    # sys.stdout.flush()

    # try:
    #     GetActions=ClientAction(connectionId,globals=dict(globals()),locals=dict(**locals()))
    #     outHandler.flush()
    # except:
    #     traceback.print_exc(file=sys.stdout)
    #     code.interact(banner="Error ClientAction :",local=dict(globals(), **locals()))

    print("Actions \n",str(tiles_actions))
    sys.stdout.flush()
    try:
        code.interact(banner="Interactive console to use actions directly :",local=dict(globals(), **locals()))
    except SystemExit:
        pass

    client.send_server('execute TS='+TileSet+' killall Xvfb')
    print("Out of killall command : "+ str(client.get_OK()))

    client.send_server('launch TS='+TileSet+" "+JOBPath+" "+COMMANDStop)

    sys.exit(0)


