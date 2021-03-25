#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import docker
import re,traceback
import sys,os,stat
import argparse

import time,datetime
import traceback
import re

import random


# Args default
DockerName='etherpad'

def parse_args(argv):
    nonlocal DockerName
    parser = argparse.ArgumentParser(
        'From a connection Id in PostgreSQL DB get connection parameters from TiledViz database.')
    parser.add_argument('-n', '--name', default=DockerName,
                        help='Etherpad name (default: '+DockerName+')')
    parser.add_argument('--debug', action='store_true',
                        help='Debug switch.',default=False)

    args = parser.parse_args(argv[1:])
    return args

if __name__ == '__main__':
    args = parse_args(sys.argv)

    dockerclient = docker.from_env()
    if (args.debug):
        print(str(dockerclient.containers.list()))
        print("etherpad container : "+str(dockerclient.containers.list(filters={"name":args.name})))

    contether=dockerclient.containers.list(filters={"name":args.name})[0]
    try:
        APIK=contether.exec_run(cmd="cat /opt/etherpad-lite/APIKEY.txt")
        APIKEY=APIK.output

        c = docker.APIClient()
        IP=c.inspect_container(contether.id)['NetworkSettings']['Networks']['bridge']['IPAddress']
        print('APIKEY: '+str(APIKEY)+' IP: '+IP)
    except Exception as err:
        traceback.print_exc(file=sys.stderr)
        print("Error APIKEY or IP : %s" % ( err ))
    
