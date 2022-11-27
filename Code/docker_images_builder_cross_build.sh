#!/bin/bash

echo "building $1 tag : $2"

docker buildx build  --no-cache --platform linux/amd64 -t $1:$2 .

EXIT_BUILD=$?

if [ $EXIT_BUILD -eq 0 ]
then
    if [ "$3" == "dry-run" ]
    then
        echo "dry-run"
        exit 0
    else
        echo "pushing $1 tag : $2"
        docker push $1:$2
        EXIT_PUSH=$?

        if [ $EXIT_PUSH -eq 0 ]
        then
            exit 0
        else
            echo "ERROR on pushing $1:$2"

            exit $EXIT_BUILD
        fi
    fi

else
    echo "ERROR on building $1:$2"
    exit $EXIT_BUILD
fi



