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

    # network=config['CASE']['network']
    # nethost=config['CASE']['nethost']
    # domain=config['CASE']['domain']

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

#TODO : classroom.config must be an output from case_config.ini!
#    	cf SERVER_JITSI var

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


    # get TiledCourse package from Github
    COMMAND_GIT="git clone https://github.com/mmancip/TiledCourse.git"
    print("command_git : "+COMMAND_GIT)
    os.system(COMMAND_GIT)

    
    os.system('cp '+CONFIGPATH+' TiledCourse/webrtcconnect')
    os.system('cp '+FILEPATH+' TiledCourse/webrtcconnect')
    COMMAND_MAIL="cd TiledCourse/webrtcconnect;  ./fastGenerateMail.sh "+CONFIGPATH
    print("command_mail :"+COMMAND_MAIL)

    #TODO randomize roomname => before sendmail
    os.system(COMMAND_MAIL)

    # Send CASE and SITE files
    try:
        client.send_server('launch TS='+TileSet+" "+JOBPath+' chmod og-rxw '+JOBPath)
        print("Out of chmod JOBPath : "+ str(client.get_OK()))
        
        send_file_server(client,TileSet,".", CASE_config, JOBPath)
        CASE_config=os.path.join(JOBPath,os.path.basename(CASE_config))
        send_file_server(client,TileSet,".", SITE_config, JOBPath)
        SITE_config=os.path.join(JOBPath,os.path.basename(SITE_config))

        send_file_server(client,TileSet,".", CONFIGPATH, JOBPath)
        send_file_server(client,TileSet,".", FILEPATH, JOBPath)
        send_file_server(client,TileSet,".", "list_hostsgpu", JOBPath)
        send_file_server(client,TileSet,"TiledCourse/webrtcconnect/", NOM_FICHIER_ETUDIANT_GENERE, JOBPath)
    except:
        print("Error sending files !")
        traceback.print_exc(file=sys.stdout)
        try:
            code.interact(banner="Try sending files by yourself :",local=dict(globals(), **locals()))
        except SystemExit:
            pass


    COMMAND='launch TS='+TileSet+" "+JOBPath+' '
    COMMAND_TiledCourse=COMMAND+COMMAND_GIT
    client.send_server(COMMAND_TiledCourse)
    print("Out of git clone TiledCourse : "+ str(client.get_OK()))

    COMMAND_copy=COMMAND+"cp -r TiledCourse/webrtcconnect/DockerHub/dockerRunHub.sh "+\
                   "TiledCourse/webrtcconnect/DockerHub/dockerStop.sh "+\
                   "TiledCourse/webrtcconnect/build_nodes_file "+\
                   "TiledCourse/webrtcconnect/launch_obs.sh "+\
                   "TiledCourse/webrtcconnect/get_DISPLAY.sh "+\
                   "TiledCourse/webrtcconnect/obs "+\
                   "./"
    client.send_server(COMMAND_copy)
    print("Out of copy scripts from TiledCourse : "+ str(client.get_OK()))
        
    # Must have only one /dev/video0 device or test on each machine v4l2loopback dev?
    VideoDeviceNumber=str(0)
    
    network="classroom"+IdClassroom
    # "X" for no swarm !
    domain="11.0.0"

    # Client for teacher must be the Frontend (in site_config.ini) from TVConnection (detect Frontend IP ?)
    CLIENT=HTTP_FRONTEND+":"+HTTP_IP
    HUBName='HUB-CR'+IdClassroom 

    ID="id_rsa_"+HTTP_IP        
    
    def Run_Hub():
        COMMAND='launch TS='+TileSet+" "+JOBPath+' ./dockerRunHub.sh '+\
            NOM_FICHIER_ETUDIANT_GENERE+' '+\
            RTMPPORT+' '+SERVER_JITSI+' '+VideoDeviceNumber+' '+\
            GPU_FILE+" "+network+" "+domain+" "+init_IP+" "+CLIENT+" "+DOCKER_NAME+" "+DATE
    
        print("\nCommand RunHub : "+COMMAND)
        client.send_server(COMMAND)
        print("Out of launch Hub : "+ str(client.get_OK()))

        # Copy ssh key to frontend from connection to HUB :

        send_file_server(client,TileSet,".ssh", ID, JOBPath)
        send_file_server(client,TileSet,".ssh", ID+".pub", JOBPath)

        global HUB_Host
        with open("list_hostsgpu","r") as hostfile :
            HUB_Host=hostfile.readline().split(" ")[0]

        global DOCKER_HUB
        DOCKER_HUB='ssh '+HUB_Host+' docker'
        
        COMMAND='launch TS='+TileSet+" "+JOBPath+' scp '+ID+'* '+HUB_Host+":/tmp"
        client.send_server(COMMAND)
        print("Out of send key : "+ str(client.get_OK()))

        COMMAND='launch TS='+TileSet+" "+JOBPath+' '+DOCKER_HUB+' cp /tmp/'+ID+' '+HUBName+':/home/myuser/.ssh/'
        client.send_server(COMMAND)
        print("Out of put key on Hub : "+ str(client.get_OK()))
        
        COMMAND='launch TS='+TileSet+" "+JOBPath+' '+DOCKER_HUB+' cp /tmp/'+ID+'.pub '+HUBName+':/home/myuser/.ssh/'
        client.send_server(COMMAND)
        print("Out of put pub key on Hub : "+ str(client.get_OK()))

        COMMAND='launch TS='+TileSet+" "+JOBPath+' bash -c " rm -f '+ID+'* ; ssh '+HUB_Host+" rm -f /tmp/"+ID+'* "'
        client.send_server(COMMAND)
        print("Out of rm key : "+ str(client.get_OK()))


        COMMAND='launch TS='+TileSet+" "+JOBPath+' '+DOCKER_HUB+\
            ' exec '+HUBName+' bash -c \'"chown myuser:myuser /home/myuser/.ssh/'+ID+'* ;'+\
            ' chmod 600 /home/myuser/.ssh/'+ID+'* "\''
        client.send_server(COMMAND)
        print("Out of chmod key on Hub : "+ str(client.get_OK()))

    Run_Hub()

    IP_Hub=domain+"."+str(int(init_IP)-1)
    
    
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
        time.sleep(2)
        get_file_client(client,TileSet,JOBPath,"nodes.json",".")
        #os.system('rm -f ./nodes.json')

    build_nodes_file()

    time.sleep(2)
    # Launch docker tools
    def launch_resize(RESOL="1440x900"):
        client.send_server('execute TS='+TileSet+' xrandr --fb '+RESOL)
        print("Out of xrandr : "+ str(client.get_OK()))

    launch_resize()

    def launch_tunnel():
        client.send_server('execute TS='+TileSet+' /opt/tunnel_ssh '+SOCKETdomain+' '+HTTP_FRONTEND+' '+HTTP_LOGIN)
        print("Out of tunnel_ssh : "+ str(client.get_OK()))

    launch_tunnel()

    def launch_vnc():
        client.send_server('execute TS='+TileSet+' /opt/vnccommand')
        print("Out of vnccommand : "+ str(client.get_OK()))

    launch_vnc()

    
    def launch_sound():

        # Get pulseaudio socket on frontend :
        COMMAND='launch TS='+TileSet+" "+JOBPath+' lsof -c pulseaudio  2>/dev/null |grep "/native" '+\
            '| tail -1 | sed -e "s&.* \([a-zA-Z0-9_/]*/native\) .*&\\1&" |tee -a out_native'
        client.send_server(COMMAND)
        print("Out of socket native detection : "+ str(client.get_OK()))

        # Add pulseaudio tunnel on Hub to frontend:
        COMMAND='launch TS='+TileSet+" "+JOBPath+\
            ' bash -c "cat out_native |xargs -I { '+DOCKER_HUB+' exec -u myuser '+HUBName+' /launch_sound.sh { "'+HTTP_IP+' '+HTTP_LOGIN 
        client.send_server(COMMAND)
        print("Out of launch_sound HUB : "+ str(client.get_OK()))

        # Pulse VM :
        COMMAND_Pulse="ssh -4 -fNT -i .ssh/id_rsa_hub -L4000:localhost:4000 "+IP_Hub+" &"
        CommandTS='execute TS='+TileSet+" "+COMMAND_Pulse
        client.send_server(CommandTS)
        print("Out of ssh Hub : "+ str(client.get_OK()))

        # All pulseaudio in container listen to 4000
        client.send_server('execute TS='+TileSet+' /opt/launch_sound.sh')
        print("Out of launch_sound VM : "+ str(client.get_OK()))
    

    # Launch OBS on the frontend
    def launch_OBS():
        COMMAND='launch TS='+TileSet+" "+JOBPath+' '

        COMMAND_DISPLAY=COMMAND+"./get_DISPLAY.sh"
        client.send_server(COMMAND_DISPLAY)
        print("Out of get DISPLAY for user : "+ str(client.get_OK()))

        COMMAND_OBS=COMMAND+"./launch_obs.sh "+HTTP_FRONTEND+" "+IdClassroom
        client.send_server(COMMAND_OBS)
        print("Out of get DISPLAY for user : "+ str(client.get_OK()))

        time.sleep(3)
    
        COMMAND_ffmpeg="/opt/command_ffmpeg "+IdClassroom+" "+VideoDeviceNumber+" "+IP_Hub+" &"
        client.send_server('execute TS='+TileSet+' '+COMMAND_ffmpeg)
        print("Out of ffmpeg : "+ str(client.get_OK()))
    #getteachervideo()
    

    # Launch google-chrome
    def launch_chrome():
        COMMAND_CHROME="/opt/command_chrome "+' '+SERVER_JITSI+' '+TeacherFirstname+'_'+TeacherLastname+' '+TeacherEmail

        with open(FILEPATH) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=';')
            count_lines=0
            for row in csv_reader:

                print(", ".join(row))
                count_lines=count_lines+1

                #UserName=row[0]
                #mail=row[1]
                roomName=row[2]

                TilesStr=' Tiles=('+containerId(count_lines)+') '
                COMMAND_CHROMEi=COMMAND_CHROME+" "+roomName+" &"
                
                print("%d Chrome command : %s" % (count_lines,COMMAND_CHROMEi))
                CommandTS='execute TS='+TileSet+TilesStr+COMMAND_CHROMEi
                client.send_server(CommandTS)
                client.get_OK()
        time.sleep(3)
                
    #TODO
    #./mute ${VM_NAME}
    #./audioOff ${VM_NAME}
    
    
    # Launch 
    # def launch_all(COMMAND):

    #     with open(FILEPATH) as csv_file:
    #         csv_reader = csv.reader(csv_file, delimiter=';')
    #         count_lines=0
    #         for row in csv_reader:

    #             print(", ".join(row))
    #             count_lines=count_lines+1

    #             #UserName=row[0]
    #             #mail=row[1]
    #             #roomName=row[2]

    #             TilesStr=' Tiles=('+containerId(count_lines)+') '
            
    #             print("%d command : %s" % (count_lines,COMMAND))
    #             CommandTS='execute TS='+TileSet+TilesStr+COMMAND
    #             client.send_server(CommandTS)
    #             client.get_OK()
                
                
    def kill_all_containers():
        Kill_Hub()

        COMMAND='launch TS='+TileSet+" "+JOBPath+' killall obs'
        client.send_server(COMMAND)

        COMMAND='launch TS='+TileSet+" "+JOBPath+' exit_sound.sh'
        client.send_server(COMMAND)
        
        client.send_server('execute TS='+TileSet+' killall Xvnc')
        print("Out of killall command : "+ str(client.get_OK()))
        client.send_server('launch TS='+TileSet+" "+JOBPath+" "+COMMANDStop)
        client.close()

        

    launch_actions_and_interact()
            
    kill_all_containers()
        
    sys.exit(0)


