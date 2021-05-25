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
    EtherpadURL=config['SITE']['ETHERPAD'].replace('"','')
    APIKey=config['SITE']['APIKey']
    etherpadhost=config['SITE']['etherpad']
    
    config.read(CASE_config)

    CASE=config['CASE']['CASE_NAME']

    MAIL=config['CASE']['MAIL']
    
    VNCPORT=config['CASE']['VNCPORT']

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
    
    #CreateTS='create TS='+TileSet+' Nb='+str(NUM_STUDENTS)
    #client.send_server(CreateTS)

    # get TiledCourse package from Github
    os.system("git clone https://github.com/mmancip/TiledCourse.git")

    # Send CASE and SITE files
    #try:
    #    send_file_server(client,TileSet,"TiledCourse/directconnect", "build_nodes_file", JOBPath)

    #    send_file_server(client,TileSet,".", CASE_config, JOBPath)
    #    CASE_config=os.path.join(JOBPath,os.path.basename(CASE_config))
    #    send_file_server(client,TileSet,".", SITE_config, JOBPath)
    #    SITE_config=os.path.join(JOBPath,os.path.basename(SITE_config))

    #    send_file_server(client,TileSet,".", FILEPATH, JOBPath)
    #    send_file_server(client,TileSet,".", "list_password", JOBPath)

    #except:
    #    print("Error sending files !")
    #    traceback.print_exc(file=sys.stdout)
    #    try:
    #        code.interact(banner="Try sending files by yourself :",local=dict(globals(), **locals()))
    #    except SystemExit:
    #        pass

    # Call Etherpad and wait for result
    def launch_etherpad():
        #etherpad build to the teacher by mail ? or give the key by text (but no copy/past ?)
        #etherpadscript="TiledCourse/etherpad/etherpad.py"
        
        os.system("wget https://files.pythonhosted.org/packages/13/6c/2079dac77d480fd49862d12465ed3369360ad9b8c9bb0e3fb79f1e7b650e/etherpad_lite-0.5.tar.gz")
        os.system("tar xfz etherpad_lite-0.5.tar.gz")
        sys.path.append(os.path.realpath('etherpad_lite-0.5'))
        sys.path.append(os.path.realpath('TiledCourse/'))
        from etherpad import etherpad
        
        # options for etherpad script :
        #argList=sys.argv[1:]
        #os.system('python another/location/test2.py %s'%(argList))
        
        #saveargv=sys.argv
        #sys.argv=[etherpadscript,"--host="+etherpadhost,"-p","9001","-u",TVuser,"-a",APIKey]
        etherport="8081"
        print("host=%s ,port=%s ,user=%s ,apikey=%s " % (etherpadhost, etherport, TVuser, APIKey))
        
        # Call etherpad script :
        try:
            #exec(compile(open(etherpadscript, "rb").read(), etherpadscript, 'exec'), globals(), locals())
            etherpad.etherpad(host=etherpadhost,port=etherport,user=TVuser,apikey=APIKey,mail=MAIL,filestud=FILEPATH,etherpadurl=EtherpadURL)
        except Exception as err:
            traceback.print_exc(file=sys.stderr)
            logging.error("Error calling %s : %s" % ( etherpadscript, err ))
            return
        #sys.argv=saveargv
        #send_file_server(client,TileSet,".", "directconnection.csv", JOBPath)

    launch_etherpad()
    
    # Build nodes.json file from new dockers list
    def build_nodes_file():
        print("Build nodes.json file from new dockers list.")
        COMMAND='TiledCourse/directconnect/build_nodes_file '+CASE_config+' '+SITE_config+' '+TileSet

        #COMMAND='launch TS='+TileSet+" "+JOBPath+' ./build_nodes_file '+CASE_config+' '+SITE_config+' '+TileSet
        print("\nCommand build_nodes_files : "+COMMAND)
        os.system(COMMAND)
        #client.send_server(COMMAND)
        #print("Out of build_nodes_file : "+ str(client.get_OK()))
        #time.sleep(2)
        #get_file_client(client,TileSet,JOBPath,"nodes.json",".")
        ##os.system('rm -f ./nodes.json')

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


