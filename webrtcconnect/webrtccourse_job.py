#!/usr/bin/env python
# -*- coding: utf-8 -*-

import configparser
import sys,os,time
import code
import argparse
import re, datetime
import inspect

# sys.path.append(os.path.realpath('/TiledViz/TVConnections/'))
# from connect import sock

import json
import csv

SITE_config='site_config.ini'
CASE_config="case_config.ini"


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

# Must v4l2loopback mount on /dev/video${VideoDeviceNumber} device.
# Please Read INSTALL doc for modprobe v4l2loopback command.
VideoDeviceNumber=config['SITE']['VideoDeviceNumber']


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

# TODO : detect RTM free PORT on what machine ? 
# IdClassroom < 65 ! car num port < 65535
RTMPPORT=SOCKETdomain+"000"

# Global commands
# Execute on each/a set of tiles
ExecuteTS='execute TS='+TileSet+" "
# Launch a command on the frontend
LaunchTS='launch TS='+TileSet+" "+JOBPath+' '


# get TiledCourse package from Github
COMMAND_GIT="git clone https://github.com/mmancip/TiledCourse.git"
print("command_git : "+COMMAND_GIT)
os.system(COMMAND_GIT)


os.system('cp '+CONFIGPATH+' TiledCourse/webrtcconnect')
os.system('cp '+FILEPATH+' TiledCourse/webrtcconnect')
COMMAND_MAIL="cd TiledCourse/webrtcconnect;  ./fastGenerateMail.sh "+CONFIGPATH
print("command_mail :"+COMMAND_MAIL)

#TODO randomize roomname (not always login) => before sendmail
os.system(COMMAND_MAIL)

# Send CASE and SITE files
try:
    client.send_server(LaunchTS+' chmod og-rxw '+JOBPath)
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


COMMAND_TiledCourse=LaunchTS+COMMAND_GIT
client.send_server(COMMAND_TiledCourse)
print("Out of git clone TiledCourse : "+ str(client.get_OK()))

COMMAND_copy=LaunchTS+"cp -r TiledCourse/webrtcconnect/DockerHub/dockerRunHub.sh "+\
               "TiledCourse/webrtcconnect/DockerHub/dockerStop.sh "+\
               "./"

client.send_server(COMMAND_copy)
print("Out of copy scripts from TiledCourse : "+ str(client.get_OK()))
    
network="classroom"+IdClassroom
# "X" for no swarm !
domain="11.0.0"

# Client for teacher must be the HTTP_FRONTEND (in site_config.ini) from TVConnection (detect Frontend IP ?)
CLIENT=HTTP_FRONTEND+":"+HTTP_IP
HUBName='HUB-CR'+IdClassroom 

ID="id_rsa_"+HTTP_IP        


TileSetHUB=TileSet+'HUB'
CreateTSHUB='create TS='+TileSetHUB+' Nb=1'
client.send_server(CreateTSHUB)

# Execute on each/a set of tiles
ExecuteTSHUB='execute TS='+TileSetHUB+" "
# Launch a command on the frontend
LaunchTSHUB='launch TS='+TileSetHUB+" "+JOBPath+' '

HTTP=HTTP_LOGIN+"@"+HTTP_IP
ExecuteHTTP=ExecuteTSHUB+" ssh -fT "+HTTP+" "

print("LaunchTSHUB: %s "%(LaunchTSHUB))

def Run_Hub():
    # DEBUG : don't delete Hub on exit
    # COMMAND=LaunchTSHUB+' sed -e \'s&--rm&&\' -i dockerRunHub.sh '
    # client.send_server(COMMAND)
    # print("Out of launch Hub : "+ str(client.get_OK()))
    global LaunchTSHUB
    COMMAND=LaunchTSHUB+' ./dockerRunHub.sh '+\
        NOM_FICHIER_ETUDIANT_GENERE+' '+\
        RTMPPORT+' '+SERVER_JITSI+' '+VideoDeviceNumber+' '+\
        GPU_FILE+" "+network+" "+domain+" "+init_IP+" "+CLIENT+" TileSetPort "+Frontend+" "+DOCKER_NAME+" "+DATE
    
    print("\nCommand RunHub : "+COMMAND)
    client.send_server(COMMAND)
    print("Out of launch Hub : "+ str(client.get_OK()))
    sys.stdout.flush()
    
    COMMAND_TiledCourse=ExecuteTSHUB+COMMAND_GIT
    client.send_server(COMMAND_TiledCourse)
    print("Out of git clone TiledCourse in HUB : "+ str(client.get_OK()))
    
    COMMAND_LS_TiledCourse=ExecuteTSHUB+' bash -c "ls -la TiledCourse > .vnc/ls_TiledCourse "'
    client.send_server(COMMAND_LS_TiledCourse)
    print("Out of ls TiledCourse on HUB: "+ str(client.get_OK()))
    
    COMMAND_SEND_HTTP=ExecuteTSHUB+' scp -rp TiledCourse/webrtcconnect/get_DISPLAY.sh '+\
                     'TiledCourse/webrtcconnect/launch_obs.sh '+\
                     'TiledCourse/webrtcconnect/obs '+HTTP+':\$HOME/tmp/ '
    client.send_server(COMMAND_SEND_HTTP)
    print("Out of send TiledCourse files on HTTP_FRONTEND : "+ str(client.get_OK()))
    
    # global HUB_Host
    # with open("list_hostsgpu","r") as hostfile :
    #     HUB_Host=hostfile.readline().split(" ")[0]
    #     hostfile.close()
        
    # global DOCKER_HUB
    # DOCKER_HUB='ssh '+HUB_Host+' docker'
    
    # ID est une clé pour le HHTP_IP
    # Hors dans TVConnection.py, la clé est pour la Frontend
    #                cmdgen="ssh-keygen -b 1024 -t rsa -N '' -f /home/"+user+"/.ssh/id_rsa_"+Frontend
    # Donc ça va pas.
    # L'idée ne serait pas de créer la clé depuis le HUB avec les mêmes commandes
    # et de copier cette clé dans le HTTP_IP? bof...
    
    # Copy ssh key to frontend from connection to HUB :
    # try:
    # send_file_server(client,TileSetHUB,".ssh", ID, JOBPath)
    # send_file_server(client,TileSetHUB,".ssh", ID+".pub", JOBPath)

    # COMMAND=LaunchTSHUB+' chmod 400 '+ID
    # client.send_server(COMMAND)
    # print("Out of chmod key : "+ str(client.get_OK()))

    # COMMAND=LaunchTSHUB+' scp -p '+ID+'* '+HUB_Host+":/tmp"
    # client.send_server(COMMAND)
    # print("Out of send key : "+ str(client.get_OK()))

    # # COMMAND=LaunchTSHUB+' ssh '+HUB_Host+' chmod 400 /tmp/'+ID
    # # client.send_server(COMMAND)
    # # print("Out of chmod key on Hub : "+ str(client.get_OK()))
    # # sys.stdout.flush()

    # COMMAND=LaunchTSHUB+' '+DOCKER_HUB+' cp -a /tmp/'+ID+' '+HUBName+':/home/myuser/.ssh/'
    # client.send_server(COMMAND)
    # print("Out of put key on Hub : "+ str(client.get_OK()))
    # sys.stdout.flush()

    # COMMAND=LaunchTSHUB+' '+DOCKER_HUB+' cp -a /tmp/'+ID+'.pub '+HUBName+':/home/myuser/.ssh/'
    # client.send_server(COMMAND)
    # print("Out of put pub key on Hub : "+ str(client.get_OK()))

    # COMMAND=LaunchTSHUB+' bash -c " rm -f '+ID+'* ; ssh '+HUB_Host+" rm -f /tmp/"+ID+'* "'
    # client.send_server(COMMAND)
    # print("Out of rm key : "+ str(client.get_OK()))
    # sys.stdout.flush()
    # except Exception as err:
    #     traceback.print_exc(file=sys.stderr)
    #     print("Error ssh ID %s for HTTP %s : %s" % (ID,HTTP_IP,err))

    # client.send_server(ExecuteTSHUB+' chmod 400 /home/myuser/.ssh/'+ID)
    # print("Out of chmod "+ID+" : "+ str(client.get_OK()))
    
    # client.send_server(ExecuteTSHUB+' chmod 700 /home/myuser/.ssh')
    # print("Out of chmod .ssh : "+ str(client.get_OK()))
    
    # COMMAND=LaunchTSHUB+' '+DOCKER_HUB+\
    #     ' exec '+HUBName+' bash -c \'"chown myuser:myuser /home/myuser/.ssh/'+ID+'* ;'+\
    #     ' chmod 600 /home/myuser/.ssh/'+ID+'* "\''
    # client.send_server(COMMAND)
    # print("Out of chmod key on Hub : "+ str(client.get_OK()))

Run_Hub()

IP_Hub=domain+"."+str(int(init_IP)-1)

sys.stdout.flush()

def launch_Hub(C):
    outpactl=True
    while (outpactl):
        time.sleep(1)
        COMMAND='bash -c "'+C+'"'
        client.send_server(ExecuteTSHUB+COMMAND)
        outpactl=client.get_OK()
        print("Out of "+C+" :"+str(outpactl))
        outpactl=bool(outpactl)
    
def wakeup():
    # Wait for server to start pactl access to Hub
    launch_Hub("pactl info > /dev/null")
    
def Kill_Hub():
    COMMAND=ExecuteHTTP+' killall obs'
    client.send_server(COMMAND)
    print("Out of kill obs : "+ str(client.get_OK()))

    COMMAND_DISPLAY=ExecuteHTTP+" bash -c \"' pulseaudio -k '\"" 
    client.send_server(COMMAND_DISPLAY)
    print("Out of reinitialize pulseaudio on HTTP_Frontend : "+ str(client.get_OK()))
    
    COMMAND=LaunchTSHUB+' ./dockerStop.sh '+NOM_FICHIER_ETUDIANT_GENERE+' '+GPU_FILE
    print("\nCommand stop Hub : "+COMMAND)
    client.send_server(COMMAND)

    print("Out of stop Hub : "+ str(client.get_OK()))


REF_CAS=str(NUM_STUDENTS)+" "+DATE+" "+DOCKERSPACE_DIR+" "+DOCKER_NAME

COMMANDStop=os.path.join(TILEDOCKERS_path,"stop_dockers")+" "+REF_CAS+" "+os.path.join(JOBPath,GPU_FILE)
print("\n"+COMMANDStop)
sys.stdout.flush()

nethost="VM"

OPTIONS=OPTIONS+" -e ID_CLASSROOM="+IdClassroom+" --device=/dev/video"+VideoDeviceNumber

def Run_Vm():
    # Launch containers HERE
    COMMAND=os.path.join(TILEDOCKERS_path,"launch_dockers")+" "+REF_CAS+" "+GPU_FILE+" "+CLIENT+\
             " "+network+" "+nethost+" "+domain+" "+init_IP+" TileSetPort "+UserFront+"@"+Frontend+" "+OPTIONS
    print("\nCommand RunVm : "+COMMAND)
    client.send_server(LaunchTS+' '+COMMAND)
    print("Out of launch Vm : "+ str(client.get_OK()))
    sys.stdout.flush()

Run_Vm()
sys.stdout.flush()
NUM_DOCKERS=NUM_STUDENTS

# Build nodes.json file from new dockers list
def build_nodes_file():
    print("Build nodes.json file from new dockers list.")

    COMMAND=LaunchTS+' TiledCourse/webrtcconnect/build_nodes_file '+CASE_config+' '+SITE_config+' '+TileSet
    print("\nCommand dockers : "+COMMAND)

    client.send_server(COMMAND)
    print("Out of build_nodes_file : "+ str(client.get_OK()))
    time.sleep(2)
    
build_nodes_file()
sys.stdout.flush()

time.sleep(2)
# Launch docker tools
def launch_resize(RESOL="1440x900"):
    client.send_server(ExecuteTS+' xrandr --fb '+RESOL)
    print("Out of xrandr : "+ str(client.get_OK()))

launch_resize()

def launch_tunnel():
    client.send_server(ExecuteTS+' /opt/tunnel_ssh '+HTTP_FRONTEND+' '+HTTP_LOGIN)
    print("Out of tunnel_ssh : "+ str(client.get_OK()))
    # Get back PORT
    for i in range(NUM_DOCKERS):
        i0="%0.3d" % (i+1)
        client.send_server(ExecuteTS+' Tiles=('+containerId(i+1)+') '+
                           'bash -c "scp  .vnc/port '+UserFront+'@'+Frontend+':'+JOBPath+'/port'+i0+'"')
        print("Out of change port %s : " % (i0) + str(client.get_OK()))

    COMMAND="find . -name \"port*\" -exec bash -c 'FILE={}; echo $FILE; i0=$( echo $FILE|sed -e \"sA./portAA\" ); echo $i0; "+\
        "port=$(cat $FILE); sed -e \"sBport="+SOCKETdomain+"${i0}Bport=${port}B\" -i ./nodes.json' \\; "
    print("\nCommand change ports  : "+COMMAND)
    client.send_server(LaunchTS+' '+COMMAND)
    print("Out of change ports : "+ str(client.get_OK()))

    sys.stdout.flush()
    launch_nodes_json()

launch_tunnel()

def launch_vnc():
    client.send_server(ExecuteTS+' /opt/vnccommand')
    print("Out of vnccommand : "+ str(client.get_OK()))

launch_vnc()

pactl_call=""
dev_source="alsa_input.pci-0000_00_1b.0.analog-stereo"
dev_sink="alsa_output.pci-0000_00_1b.0.analog-stereo"
sourceindex=-1
sinkindex=-1
sourcemodule=-1
sinkmodule=-1
sourceVMindex=[]
sinkVMindex=[]

def launch_sound():
    global pactl_call, dev_source, dev_sink, sourceindex, sinkdex
    
    # Get pulseaudio socket on HTTP_FRONTEND through DockerHub :
    COMMAND=ExecuteHTTP+' bash -c "\'/sbin/lsof -c pulseaudio  2>/dev/null |grep \\\"/native\\\" '+\
        '| tail -1 | sed -e \\\"s@.* \\\([a-zA-Z0-9_/]*/native\\\) .*@\\1@\\\" > tmp/out_native\'"'
    if (args.debug):
        print("COMMAND for socket native detection : "+ COMMAND)
        sys.stdout.flush()
    client.send_server(COMMAND)
    print("Out of socket native detection : "+ str(client.get_OK()))

    # TODO: This may not work if HTTP_FRONTEND and Frontend ssh keys are different.
    COMMAND=ExecuteTSHUB+' scp  '+HTTP+':\$HOME/tmp/out_native '+UserFront+'@'+Frontend+':'+JOBPath
    if (args.debug):
        print("COMMAND for scp out_native : "+ COMMAND)
        sys.stdout.flush()
    client.send_server(COMMAND)
    print("Out of scp out_native : " + str(client.get_OK()))

    get_file_client(client,TileSet,JOBPath,"out_native",".")
    with open("out_native","r") as native :
        pulsesocket=native.readline().replace('\n','')
        print("pulsesocket : "+pulsesocket)
        pulsedir=pulsesocket.replace("pulse/native","")
        print("pulsedir : "+pulsedir)
        
    pactl_call='XDG_RUNTIME_DIR='+pulsedir+' pactl'
    #pactl_call='pactl'
    
    # Add pulseaudio tunnel on Hub to HTTP_FRONTEND :
    client.send_server(ExecuteTSHUB+' /opt/launch_sound.sh '+pulsesocket+' '+HTTP_IP+' '+HTTP_LOGIN)
    print("Out of launch_sound HUB : "+ str(client.get_OK()))

    COMMAND=' scp  \''+HTTP+':\$HOME/.config/pulse/cookie\' .config/pulse/'
    launch_Hub(COMMAND)
    
    # detect default source/sink
    launch_Hub('pactl info |grep Default > .vnc/out_default')

    client.send_server(ExecuteTSHUB+'scp .vnc/out_default '+UserFront+'@'+Frontend+':'+JOBPath)
    print("Out of scp out_default : " + str(client.get_OK()))
    
    get_file_client(client,TileSet,JOBPath,"out_default",".")
    
    with open("out_default","r") as fdefault :
        for line in fdefault:
            line=line.replace('\n','')
            if (re.search('Default Sink:',line)):
                dev_sink=line.replace("Default Sink: ","")
            if (re.search('Default Source:',line)):
                dev_source=line.replace("Default Source: ","")

    # Pulse VM :
    COMMAND_Pulse="ssh -4 -fNT -i .ssh/id_rsa_hub -L4000:localhost:4000 "+IP_Hub+" &"
    CommandTS=ExecuteTS+" "+COMMAND_Pulse
    client.send_server(CommandTS)
    print("Out of ssh Hub : "+ str(client.get_OK()))

    # All pulseaudio in container listen to 4000
    client.send_server(ExecuteTS+' /opt/launch_sound.sh')
    print("Out of launch_sound VM : "+ str(client.get_OK()))
    # client.send_server(ExecuteTS+' nohup bash -c "killall pulseaudio" </dev/null > /dev/null 2>&1 &')
    # print("Out of kill pulseaudio VM : "+ str(client.get_OK()))
    sys.stdout.flush()
    
    COMMAND_cookie='bash -c "scp -i .ssh/id_rsa_hub \''+IP_Hub+':$HOME/.config/pulse/cookie\' .config/pulse/"'
    if (args.debug):
        print("COMMAND for scp VM cookie : "+ COMMAND_cookie)
        sys.stdout.flush()
    client.send_server(ExecuteTS+COMMAND_cookie)
    print("Out of scp VM cookie : " + str(client.get_OK()))
    

    # Add sound modules on pulseaudio of HTTP_FRONTEND :
    launch_Hub('pactl load-module module-null-sink sink_name=stu_sink'+
                     ' sink_properties=device.description=\"GlobalSink\" > .vnc/index_stu_sink')
    launch_Hub('pactl list short sinks |grep stu_sink >> .vnc/index_stu_sink')

    launch_Hub('pactl load-module module-null-sink sink_name=stu_source'+
                     ' sink_properties=device.description=\"GlobalSource\" > .vnc/index_stu_source')
    launch_Hub('pactl list short sinks |grep stu_source >> .vnc/index_stu_source')

    COMMAND=ExecuteTSHUB+'scp .vnc/index_stu_* '+UserFront+'@'+Frontend+':'+JOBPath
    if (args.debug):
        print("COMMAND for scp index_stu_sink/source : "+ COMMAND)
        sys.stdout.flush()
    client.send_server(COMMAND)
    print("Out of scp index_stu_sink/source : " + str(client.get_OK()))

    get_file_client(client,TileSet,JOBPath,"index_stu_sink",".")
    get_file_client(client,TileSet,JOBPath,"index_stu_source",".")

    with open("index_stu_source","r") as fsource :
        sourcemodule=fsource.readline().replace('\n','')
        print("sourcemodule : "+sourcemodule)
        sourcemodule=int(sourcemodule)
        sourceindex=re.sub('\t.*','',fsource.readline().replace('\n',''))
        print("sourceindex : "+sourceindex)
        sourceindex=int(sourceindex)
        fsource.close()
    
    with open("index_stu_sink","r") as fsink :
        sinkmodule=fsink.readline().replace('\n','')
        print("sinkmodule : "+sinkmodule)
        sinkmodule=int(sinkmodule)
        sinkindex=re.sub('\t.*','',fsink.readline().replace('\n',''))
        print("sinkindex : "+sinkindex)
        sinkindex=int(sinkindex)
        fsink.close()

    time.sleep(2)
    # Le son des étudiants sort sur les haut-parleurs du prof
    launch_Hub('pactl load-module module-loopback source=stu_sink.monitor sink='+dev_sink)
    # Son du micro du prof va dans les inputs des étudiants
    launch_Hub('pactl load-module module-loopback source='+dev_source+' sink=stu_source')
    
    # Le son des étudiants va dans les inputs des étudiants
    launch_Hub('pactl load-module module-loopback source=stu_sink.monitor sink=stu_source')
    
    # Un seul étudiant parle à la fois comme ça son son ne peut pas re-rentrer. 
    #launch_Hub('pactl set-default-sink stu_sink')

    # TODO : considering local docker network is safe, one can only connect from VM to HUB with socat and open 4000 port. 
    # only HUB to HTTP_FRONTEND may be encrypted.    
    wakeup()
    for i in range(NUM_DOCKERS):
        VM=containerId(i+1)
        launch_Hub('pactl load-module module-null-sink sink_name=fake_source'+VM+
                         ' sink_properties=device.description=fake_source'+VM)
        launch_Hub('pactl load-module module-remap-source master=fake_source'+VM+'.monitor '+
                         ' source_name=stu_source'+VM+' source_properties=device.description=Virtual_Mic'+VM+
                         ' > .vnc/index_source'+VM)
        launch_Hub('pactl load-module module-null-sink sink_name=stu_sink'+VM+
                         ' sink_properties=device.description=sink'+VM+' > .vnc/index_sink'+VM)

        COMMAND=ExecuteTSHUB+'scp .vnc/index_s*'+VM+' '+UserFront+'@'+Frontend+':'+JOBPath
        if (args.debug):
            print("COMMAND for scp index_sink/source_%s : %s" % (VM,COMMAND))
            sys.stdout.flush()
        client.send_server(COMMAND)
        print("Out of scp index_sink/source_%s : %s" % (VM,str(client.get_OK())))
        
        get_file_client(client,TileSet,JOBPath,"index_sink"+VM,".")
        get_file_client(client,TileSet,JOBPath,"index_source"+VM,".")

        with open("index_source"+VM,"r") as fsource :
            soindex=fsource.readline().replace('\n','')
            print("sourceindex%s : %s" % (VM,soindex))
            sourceVMindex.append(int(soindex))
            fsource.close()
    
        with open("index_sink"+VM,"r") as fsink :
            siindex=fsink.readline().replace('\n','')
            print("sinkindex%s : %s" % (VM,siindex))
            sinkVMindex.append(int(siindex))
            fsink.close()

        # Connect to global sound
        launch_Hub('pactl load-module module-loopback source=stu_sink'+VM+'.monitor sink=stu_sink')
        launch_Hub('pactl load-module module-loopback source=stu_source.monitor sink=fake_source'+VM)

        
# Launch OBS on the frontend
def launch_OBS():

    COMMAND_DISPLAY=ExecuteHTTP+" bash -c \"' cd tmp; ./get_DISPLAY.sh; ls -la out_DISPLAY '\"" 
    client.send_server(COMMAND_DISPLAY)
    print("Out of get DISPLAY for user : "+ str(client.get_OK()))

    # client.send_server(ExecuteTSHUB+
    #                    'bash -c "scp out_DISPLAY '+UserFront+'@'+Frontend+':'+JOBPath+'/"')
    # print("Out of scp out_DISPLAY : " + str(client.get_OK()))
    #get_file_client(client,TileSet,JOBPath,"out_DISPLAY",".")

    COMMAND_OBS=ExecuteHTTP+" bash -c \"' cd tmp; ./launch_obs.sh "+HTTP_FRONTEND+" "+RTMPPORT+" "+IdClassroom+" & '\"" 
    client.send_server(COMMAND_OBS)
    print("Out of execute OBS for user : "+ str(client.get_OK()))

    time.sleep(3)

    #TODO : how to force only one ffmpeg by node (cf mageiawebrtc/command_ffmpeg)
    COMMAND_ffmpeg=" /opt/command_ffmpeg "+IdClassroom+" "+VideoDeviceNumber+" "+IP_Hub+" &"
    with open(FILEPATH) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=';')
        count_lines=0
        for row in csv_reader:
            count_lines=count_lines+1
            TilesStr=' Tiles=('+containerId(count_lines)+') '
            client.send_server(ExecuteTS+TilesStr+COMMAND_ffmpeg)
            print("Out of ffmpeg : "+ str(client.get_OK()))
            time.sleep(2)
    sys.stdout.flush()


# Launch google-chrome
def launch_chrome():
    COMMAND_CHROME="/opt/command_chrome "+' '+SERVER_JITSI+' '+TeacherFirstname+'_'+TeacherLastname+' '+TeacherEmail
    client.send_server(ExecuteTSHUB+' bash -c "pactl list > .vnc/out_sound_0 "')
    #nohup ... </dev/null > /dev/null 2>&1  &
    client.get_OK()

    time.sleep(0.5)
    with open(FILEPATH) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=';')
        count_lines=0
        for row in csv_reader:
            print(", ".join(row))
            i=count_lines
            count_lines=count_lines+1
            #UserName=row[0]
            #mail=row[1]
            roomName=row[2]
            VM=containerId(count_lines)
            VM_NAME=DOCKER_NAME+"_"+DATE+"_"+VM
            
            wakeup()
            launch_Hub('pactl set-default-sink stu_sink'+VM)
            launch_Hub('pactl set-default-source stu_source'+VM)
            time.sleep(1)

            TilesStr=' Tiles=('+VM+') '
            COMMAND_CHROMEi=COMMAND_CHROME+' '+roomName+' stu_sink'+VM+' stu_source'+VM
            print("%d Chrome command : %s" % (count_lines,COMMAND_CHROMEi))
            CommandTS=ExecuteTS+TilesStr+COMMAND_CHROMEi
            client.send_server(CommandTS)
            client.get_OK()
            
            time.sleep(5)
            wakeup()
            COMMAND='id=$(pactl list sink-inputs  |grep -i -B23 \"'+VM_NAME+'\" '+\
                '|head -1 |sed -e \"s/Sink Input #//\"); echo \$id; '+\
                'pactl move-sink-input \$id stu_sink'+VM+' >> .vnc/out_move_sink'+VM+' 2>&1'
            launch_Hub(COMMAND)

            wakeup()
            COMMAND='id=$(pactl list source-outputs  |grep -i -B23 \"'+VM_NAME+'\" '+\
                '|head -1 |sed -e \"s/Source Output #//\"); echo \$id; '+\
                'pactl move-source-output \$id stu_source'+VM+' >> .vnc/out_move_source'+VM+' 2>&1'
            launch_Hub(COMMAND)

            mute(VM)

            client.send_server(ExecuteTSHUB+' bash -c "pactl list > .vnc/out_sound_'+str(count_lines)+'"')
            #nohup ... </dev/null > /dev/null 2>&1  &
            client.get_OK()
            
            sys.stdout.flush()

# Launch google-chrome
def place_chrome_sound():
    for i in range(NUM_DOCKERS):
        VM=containerId(i+1)
        VM_NAME=DOCKER_NAME+"_"+DATE+"_"+VM

        COMMAND='id=$(pactl list sink-inputs  |grep -i -B23 \"'+VM_NAME+'\" '+\
            '|head -1 |sed -e \"s/Sink Input #//\"); echo \$id; '+\
            'pactl move-sink-input \$id stu_sink'+VM+' >> .vnc/out_move_sink'+VM+' 2>&1'
        launch_Hub(COMMAND)

        COMMAND='id=$(pactl list source-outputs  |grep -i -B23 \"'+VM_NAME+'\" '+\
            '|head -1 |sed -e \"s/Source Output #//\"); echo \$id; '+\
            'pactl move-source-output \$id stu_source'+VM+' >> .vnc/out_move_source'+VM+' 2>&1'
        launch_Hub(COMMAND)

            
Volume_Out=[0]*NUM_DOCKERS
Volume_In=[100]*NUM_DOCKERS

def get_volume_out(tileNum=-1,tileId='001'):
    if ( tileNum > -1 ):
        i=tileNum
    else:
        i=tileId-1
    VM=containerId(i+1)
    VM_NAME=DOCKER_NAME+"_"+DATE+"_"+VM
    COMMAND='volume_out=$(pactl list sinks |grep -i -B8 -A3 stu_sink'+VM+')'+\
        'echo \$volume_out; '+\
        ' > .vnc/out_volume_out'+VM+' 2>&1'
    launch_Hub(COMMAND)

def open_sound(tileNum=-1,tileId='001'):
    if ( tileNum > -1 ):
        i=tileNum
    else:
        i=tileId-1
    VM=containerId(i+1)
    Volume_Out[i]=100
    launch_Hub('pactl set-sink-volume stu_sink'+VM+' 100%%')

def mute(tileNum=-1,tileId='001'):
    if ( tileNum > -1 ):
        i=tileNum
    else:
        i=tileId-1
    VM=containerId(i+1)
    Volume_Out[i]=0
    launch_Hub('pactl set-sink-volume stu_sink'+VM+' %d%%' % Volume_Out[i])
    
def increase_volume(tileNum=-1,tileId='001'):
    if ( tileNum > -1 ):
        i=tileNum
    else:
        i=tileId-1
    VM=containerId(i+1)
    Volume_Out[i]=Volume_Out[i]+10
    launch_Hub('pactl set-sink-volume stu_sink'+VM+' %d%%' % Volume_Out[i])
    
def decrease_volume(tileNum=-1,tileId='001'):
    if ( tileNum > -1 ):
        i=tileNum
    else:
        i=tileId-1
    VM=containerId(i+1)
    Volume_Out[i]=Volume_Out[i]-10
    launch_Hub('pactl set-sink-volume stu_sink'+VM+' %d%%' % Volume_Out[i])
    

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
#             CommandTS=ExecuteTS+TilesStr+COMMAND
#             client.send_server(CommandTS)
#             client.get_OK()
            
            
def kill_all_containers():
    
    client.send_server(ExecuteTS+' killall Xvnc')
    print("Out of killall command : "+ str(client.get_OK()))
    client.send_server(LaunchTS+" "+COMMANDStop)

    Kill_Hub()

    client.close()
    

launch_actions_and_interact()
        
kill_all_containers()
    
sys.exit(0)
