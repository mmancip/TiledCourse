#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import docker
from etherpad_lite import EtherpadLiteClient
from bs4 import BeautifulSoup
import requests

import re,traceback
import sys,os,stat
import argparse

import time,datetime
import traceback
import re

import random

#call:
#etherpad.py  --host 172.17.0.3 --port 9001 --name etherpad --user mmartial
#etherpad.py  --host localhost --port 8001 --name etherpad --user mmartial

initText="Please register your hostname and login name\nmachine IP  ,  login\n"

# Args default
HOST="172.17.0.3"
PORT="9001"
DockerName='etherpad'
User='ddurandi'

def parse_args(argv):
    parser = argparse.ArgumentParser(
        'From a connection Id in PostgreSQL DB get connection parameters from TiledViz database.')
    parser.add_argument('--host', default=HOST,
                        help='Etherpad host (default: '+HOST+')')
    parser.add_argument('-p', '--port', default=PORT,
                        help='Etherpad port (default: '+PORT+')')
    parser.add_argument('-n', '--name', default=DockerName,
                        help='Etherpad name (default: '+DockerName+')')
    parser.add_argument('-u', '--user', default=User,
                        help='User name for test (default: '+User+')')
    # parser.add_argument('-c', '--connectionId', 
    #                     help='Connection Id in DB.')
    parser.add_argument('--debug', action='store_true',
                        help='Debug switch for new job.',default=False)

    args = parser.parse_args(argv[1:])
    return args

def passrandom(nbchar):
    ALPHABET = "B6P8VbhZoGp9JYd0uLCsAT4DXF1xqIUSyQMniNgje53crvlHR7W2fkEtmazwKO"
    mystring=''.join(random.choice(ALPHABET) for i in range(nbchar)).encode('utf-8')
    return mystring

if __name__ == '__main__':
    args = parse_args(sys.argv)

    dockerclient = docker.from_env()
    print(str(dockerclient.containers.list()))
    print("etherpad container : "+str(dockerclient.containers.list(filters={"name":args.name})))

    contether=dockerclient.containers.list(filters={"name":args.name})[0]
    try:
        APIK=contether.exec_run(cmd="cat /opt/etherpad-lite/APIKEY.txt")
        APIKEY=APIK.output
        #print('APIKEY: '+str(APIKEY))
    except Exception as err:
        traceback.print_exc(file=sys.stderr)
        print("Error APIKEY : %s" % ( err ))

    URL="http://"+args.host+":"+args.port+"/api"
    #print("URL ="+URL)
    sys.stdout.flush()

    #time.sleep(2)
    try:
        client=EtherpadLiteClient(base_url=URL,base_params={"apikey":APIKEY},api_version="1",timeout=7000)
    except Exception as err:
        traceback.print_exc(file=sys.stderr)
        print("Error client : %s" % ( err ))
        exit(1)

    #time.sleep(1)
    padID=passrandom(20)
    print("Plese send PADID to all students :"+str(padID))
    sys.stdout.flush()


    try:
        myauth=client.createAuthor(name=args.user)
        pad=client.createPad(padID=padID,text=initText)
    except Exception as err:
        traceback.print_exc(file=sys.stderr)
        print("Error create_pad : %s" % ( err ))
        exit(2)
    
    # help(pad)

    # COMMAND=URL+"/1/setText?apikey="+str(APIKEY)+"&padID="+str(padID)+"&text='"+initText+"'"
    # os.system("curl "+COMMAND)
    

    # Wait for students
    print("Wait 60s (or more) for students and teacher must finish by 'END' string.")
    time.sleep(60)

    while True:
        try:
            Out=client.getText(padID=padID)
        except Exception as err:
            traceback.print_exc(file=sys.stderr)
            print("Error get_text : %s" % ( err ))
            exit(2)

        # COMMAND=URL+"/1/getText?apikey="+str(APIKEY)+"&padID="+str(padID)+"&jsonp=?"
        # os.system("curl "+COMMAND)
    
        # Build node file.
        #print(Out)
        print(Out["text"])
        List=Out["text"].replace(initText,"").split("\n")
        print(List)
        sys.stdout.flush()
        
        if ("END" in List):
            iEnd=List.index("END")
            List=List[:iEnd]
            break
        else:
            time.sleep(2)
            
    # Créé le tableau des élèves connectés en direct.
    studfile="./directconnection.csv"
    with open(studfile,'w+') as f:
        for stud in List:
            f.write(stud+"\n")
        f.close()
    os.system("ls -la "+studfile)
    
