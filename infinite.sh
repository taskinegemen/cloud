#!/bin/bash
#DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
DIR="$(dirname "$(readlink -f "$0")")"
PATHOFFILE=`echo $DIR/CloudServer.py`  
#trap "echo Booh!" SIGINT SIGTERM
while :
do
        cd $DIR;
	python CloudServer.py
        sleep 1
done

