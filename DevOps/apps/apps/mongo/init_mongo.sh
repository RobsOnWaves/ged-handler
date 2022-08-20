#!/bin/bash

STR=$(</mongo_ged.js)

mongosh --port 27017 --authenticationDatabase "admin" -u $MONGO_INITDB_ROOT_USERNAME -p $MONGO_INITDB_ROOT_PASSWORD << END_SCRIPT
$STR

END_SCRIPT
echo $STR
