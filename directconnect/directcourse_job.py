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
    HOMEstudents=config['SITE']['HOMEstudents']

    SOCKETdomain=config['SITE']['SOCKETdomain']

    config.read(CASE_config)

    CASE=config['CASE']['CASE_NAME']

    FILEPATH=config['CASE']['FILEPATH']

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

    # get TiledCourse package from Github
    os.system("git clone https://github.com/mmancip/TiledCourse.git")

    # Send CASE and SITE files
    try:
        send_file_server(client,TileSet,"TiledCourse/directconnect", "build_nodes_file", JOBPath)

        send_file_server(client,TileSet,".", CASE_config, JOBPath)
        CASE_config=os.path.join(JOBPath,os.path.basename(CASE_config))
        send_file_server(client,TileSet,".", SITE_config, JOBPath)
        SITE_config=os.path.join(JOBPath,os.path.basename(SITE_config))

        send_file_server(client,TileSet,".", FILEPATH, JOBPath)

    except:
        print("Error sending files !")
        traceback.print_exc(file=sys.stdout)
        try:
            code.interact(banner="Try sending files by yourself :",local=dict(globals(), **locals()))
        except SystemExit:
            pass

    # Build nodes.json file from new dockers list
    def build_nodes_file():
        print("Build nodes.json file from new dockers list.")
        COMMAND='launch TS='+TileSet+" "+JOBPath+' ./build_nodes_file '+CASE_config+' '+SITE_config+' '+TileSet
        print("\nCommand dockers : "+COMMAND)

        client.send_server(COMMAND)
        print("Out of build_nodes_file : "+ str(client.get_OK()))
        time.sleep(2)
        get_file_client(client,TileSet,JOBPath,"nodes.json",".")
        #os.system('rm -f ./nodes.json')

    build_nodes_file()

    def kill_all_containers():
        # client.send_server('execute TS='+TileSet+' killall Xvnc')
        # print("Out of killall command : "+ str(client.get_OK()))
        # client.send_server('launch TS='+TileSet+" "+JOBPath+" "+COMMANDStop)
        # client.close()
        print("Find a command to kill vnc fluxes.")
        

    launch_actions_and_interact()
            
    kill_all_containers()

    sys.exit(0)


