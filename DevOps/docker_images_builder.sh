#!/bin/bash

echo "starting builds: " ; date

echo "push mode: $2"

cd apps/ged_handler

cp Dockerfile ../../../Code/

commit_hash=$(git log -1 --format=format:"%H")

echo hash:"$commit_hash"

cd ../../../Code/
echo "building ged_handler image tag: $commit_hash and latest$1"

./docker_images_builder_cross_build.sh ged_handler "$commit_hash" "$2"

EXIT_BUILD=$?
if [ $EXIT_BUILD -eq 0 ]
then
    echo "building ged_handler image tag: $commit_hash  OK"
else
     echo "building ged_handler image tag: $commit_hash ERROR"
     exit $EXIT_BUILD
fi

./docker_images_builder_cross_build.sh ged_handler latest"$1" "$2"

EXIT_BUILD=$?
if [ $EXIT_BUILD -eq 0 ]
then
    echo "building ged_handler image tag: latest$1 OK"
else
     echo "building ged_handler image tag: latest$1 ERROR"
     exit $EXIT_BUILD
fi

echo "end of all builds"; date
exit 0
