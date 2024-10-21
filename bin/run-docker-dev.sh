#!/usr/bin/env sh

APPNAME=$1
docker build . -t $APPNAME
docker run -p 8080:8080 $APPNAME -e CIPHER_KEY=$2
