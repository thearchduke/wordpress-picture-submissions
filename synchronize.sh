#!/bin/bash
if [ $# -eq 0 ]
  then
    echo "Please supply either to_staging or from_staging"
    exit
fi

if [ "$1" = "to_staging" ]; then
    rsync -chavzP --stats ~/bj/ tynan@test.balloon-juice.com:/home/tynan/on-the-road/ 
elif [ "$1" = "from_staging" ]; then
    rsync -chavzP --stats tynan@test.balloon-juice.com:/home/tynan/on-the-road/ ~/bj/
else
    echo "invalid argument supplied."
fi
