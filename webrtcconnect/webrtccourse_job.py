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
    HTTP_IP=config['SITE']['HTTP_IP']
    init_IP=config['SITE']['init_IP']

    TILEDOCKERS_path=config['SITE']['TILEDOCKER_DIR']
    DOCKERSPACE_DIR=config['SITE']['DOCKERSPACE_DIR']

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
    # DateDMY=${DATA[5]} # Jour du cours
    # DateHM=${DATA[6]} # Heure du cours
    # JitsiServer=${DATA[7]} # Adresse Jitsi sans https://
    # SchoolName=${DATA[8]} # Nom de l'ecole
    # SenderName=${DATA[9]} # Nom de l'emetteur
    # SenderEmail=${DATA[10]} # Adresse email de l'emetteur

    SOCKETdomain=config['CASE']['SOCKETdomain']

    DOCKER_NAME=config['CASE']['DOCKER_NAME']

    HTTP_LOGIN=config['CASE']['HTTP_LOGIN']
    
    OPTIONS=config['CASE']['OPTIONS'].replace("$","").replace('"','')
    print("\nOPTIONS from CASE_CONFIG : "+OPTIONS)
    def replaceconf(x):
        if (re.search('}',x)):
            varname=x.replace("{","").replace("}","")
            return config['CASE'][varname]
        else:
            return x
    OPTIONS=OPTIONS.replace("JOBPath",JOBPath)
    OPTIONS=OPTIONS.replace('{','|{').replace('}','}|').split('|')
    OPTIONS="".join(list(map( replaceconf,OPTIONS)))

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
    TeacherFirstname=dataclass[0][2]
    TeacherLastname=dataclass[0][3]
    TeacherEmail=dataclass[0][4]
    DateDMY=dataclass[0][5] # Jour du cours
    DateHM=dataclass[0][6] # Heure du cours
    
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

    #os.system("cp "+FILECLASS+" "+DockerWebRTC+"/original_list") => cf remarque README.md

    # get TiledCourse package from Github
    COMMAND_GIT="git clone https://github.com/mmancip/TiledCourse.git"
    print("command_git : "+COMMAND_GIT)
    os.system(COMMAND_GIT)

    
    os.system('cp '+CONFIGPATH+' TiledCourse/webrtcconnect')
    os.system('cp '+FILEPATH+' TiledCourse/webrtcconnect')
    COMMAND_MAIL="cd TiledCourse/webrtcconnect;  ./fastGenerateMail.sh "+CONFIGPATH
    print("command_mail :"+COMMAND_MAIL)
    os.system(COMMAND_MAIL)

    # Send CASE and SITE files
    try:
        send_file_server(client,TileSet,".", CASE_config, JOBPath)
        CASE_config=os.path.join(JOBPath,os.path.basename(CASE_config))
        send_file_server(client,TileSet,".", SITE_config, JOBPath)
        SITE_config=os.path.join(JOBPath,os.path.basename(SITE_config))

        send_file_server(client,TileSet,".", CONFIGPATH, JOBPath)
        send_file_server(client,TileSet,".", FILEPATH, JOBPath)
        send_file_server(client,TileSet,".", "list_hostsgpu", JOBPath)
        send_file_server(client,TileSet,"TiledCourse/webrtcconnect/", NOM_FICHIER_ETUDIANT_GENERE, JOBPath)
        send_file_server(client,TileSet,".", "dockerRunHub.sh", JOBPath)
        COMMAND='launch TS='+TileSet+" "+JOBPath+' chmod u+x ./dockerRunHub.sh'
        client.send_server(COMMAND)
        client.get_OK()
        #send_file_server(client,TileSet,"TiledCourse/webrtcconnect/DockerHub", "dockerRunHub.sh", JOBPath)
        send_file_server(client,TileSet,"TiledCourse/webrtcconnect", "build_nodes_file", JOBPath)
        
        #send_file_server(client,TileSet,".", dockerCreateNetwork.sh, JOBPath)
        #send_file_server(client,TileSet,".", dockerConnection.sh, JOBPath)

    except:
        print("Error sending files !")
        traceback.print_exc(file=sys.stdout)
        try:
            code.interact(banner="Try sending files by yourself :",local=dict(globals(), **locals()))
        except SystemExit:
            pass


        
    # ???? Comment 
    VideoDeviceNumber=str(0)
    
    network="classroom"+IdClassroom
    #"X"
    domain="11.0.0"

    CLIENT=HTTP_FRONTEND+":"+HTTP_IP
    
    def Run_Hub():
        COMMAND='launch TS='+TileSet+" "+JOBPath+' ./dockerRunHub.sh '+\
            NOM_FICHIER_ETUDIANT_GENERE+' '+\
            RTMPPORT+' '+SERVER_JITSI+' '+VideoDeviceNumber+' '+\
            GPU_FILE+" "+network+" "+domain+" "+init_IP+" "+CLIENT
    
        print("\nCommand RunHub : "+COMMAND)
        client.send_server(COMMAND)

        print("Out of launch Hub : "+ str(client.get_OK()))
    Run_Hub()

    # IP from Hub : domain.INIT_IP-1
    
    def Kill_Hub():
        COMMAND='launch TS='+TileSet+" "+JOBPath+' ./dockerStop.sh '+NOM_FICHIER_ETUDIANT_GENERE+' '+GPU_FILE
    
        print("\nCommand stop Hub : "+COMMAND)
        client.send_server(COMMAND)

        print("Out of stop Hub : "+ str(client.get_OK()))


    REF_CAS=str(NUM_STUDENTS)+" "+DATE+" "+DOCKERSPACE_DIR+" "+DOCKER_NAME
    
    COMMANDStop=os.path.join(TILEDOCKERS_path,"stop_dockers")+" "+REF_CAS+" "+os.path.join(JOBPath,GPU_FILE)
    print("\n"+COMMANDStop)

    nethost="VM"

    OPTIONS=OPTIONS+" -e ID_CLASSROOM="+IdClassroom+" --device=/dev/video"+VideoDeviceNumber
    
    def Run_Vm():
        # Launch containers HERE
        COMMAND=os.path.join(TILEDOCKERS_path,"launch_dockers")+" "+REF_CAS+" "+GPU_FILE+" "+CLIENT+\
                 " "+network+" "+nethost+" "+domain+" "+init_IP+" TileSetPort "+UserFront+"@"+Frontend+" "+OPTIONS
        print("\nCommand RunVm : "+COMMAND)
        client.send_server('launch TS='+TileSet+" "+JOBPath+' '+COMMAND)
        sys.stdout.flush()
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

    time.sleep(2)
    # Launch docker tools
    def launch_tunnel():
        client.send_server('execute TS='+TileSet+' /opt/tunnel_ssh '+SOCKETdomain+' '+HTTP_FRONTEND+' '+HTTP_LOGIN)
        print("Out of tunnel_ssh : "+ str(client.get_OK()))
    launch_tunnel()

    def launch_vnc():
        client.send_server('execute TS='+TileSet+' /opt/vnccommand')
        print("Out of vnccommand : "+ str(client.get_OK()))
    launch_vnc()

    def launch_resize(RESOL="1440x900"):
        client.send_server('execute TS='+TileSet+' xrandr --fb '+RESOL)
        print("Out of xrandr : "+ str(client.get_OK()))
    launch_resize()

    # TODO Poste du prof :
    # Prof OBS + rtmp://Host_DU_HUB:RTMPport/live

    # Copy connection key to HTTP_FRONTEND to HUB => 
    # Add pulseaudio tunnel :
    # TODO reverse (native socket pulseaudio in Hub)
    #ssh  -R4000:/run/user/$(id -u)/pulse/native @${Host_DU_HUB}
    #p${PORT_SSH_HUB} => pas besoin de copie du ssh.pub

    # Pulse VM : 
    # "ssh -4 -fNT \
    # -L${PULSESERVER_PORT}:localhost:${PULSESERVER_PORT} \
    # myuser@HUB-CR${ID_CLASSROOM}"

    
    # startClass :
    def getteachervideo():
        COMMAND_ffmpeg="/opt/command_ffmpeg "+IdClassroom+" "+VideoDeviceNumber+" &"    
        client.send_server('execute TS='+TileSet+' '+COMMAND_ffmpeg)
        print("Out of ffmpeg : "+ str(client.get_OK()))
    #getteachervideo()
    
    ## Need a sleep to wait the connection between ffmpeg & the streaming server
    #time.sleep(5)

    # Launch google-chrome
    def launch_chrome():
        COMMAND_CHROME="/opt/command_chrome "+' '+SERVER_JITSI+' '+TeacherFirstname+'_'+TeacherLastname

        with open(FILEPATH) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=';')
            count_lines=0
            for row in csv_reader:

                print(", ".join(row))
                count_lines=count_lines+1

                roomName=row[2]

                TilesStr=' Tiles=('+containerId(count_lines)+') '     
                COMMAND_CHROMEi=COMMAND_CHROME+" "+roomName+" &"
            
                print("%d VMD command : %s" % (count_lines,COMMAND_CHROMEi))
                CommandTS='execute TS='+TileSet+TilesStr+COMMAND_CHROMEi
                client.send_server(CommandTS)
                client.get_OK()
                
                
    #time.sleep(3)

    # TODO Poste du prof :
    #	./mute ${VM_NAME}
    #	./audioOff ${VM_NAME}
    
    def kill_all_containers():
        Kill_Hub()
        client.send_server('execute TS='+TileSet+' killall Xvnc')
        print("Out of killall command : "+ str(client.get_OK()))
        client.send_server('launch TS='+TileSet+" "+JOBPath+" "+COMMANDStop)
        client.close()
        
    # # Launch Server for commands from FlaskDock
    # print("GetActions=ClientAction("+str(connectionId)+",globals=dict(globals()),locals=dict(**locals()))")
    # sys.stdout.flush()
    
    print("Actions \n",str(tiles_actions))
    sys.stdout.flush()
    try:
        code.interact(banner="Interactive console to use actions directly :",local=dict(globals(), **locals()))
    except SystemExit:
        pass
    
    kill_all_containers()
    
    sys.exit(0)


