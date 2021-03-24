#!/bin/bash

padID=$1
ethHost=$2

if [! -n $ethHost ]; then
    ethHost=localhost
fi
export APIKey=$(docker exec -t etherpad cat /opt/etherpad-lite/APIKEY.txt)
curl "http://$ethHost:8001/api/1/getText?apikey=$APIKey&padID=$padID&jsonp=?"
