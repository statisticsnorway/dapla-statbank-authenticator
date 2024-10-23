#!/usr/bin/env sh

APPNAME=$1
docker build . --platform linux/amd64 -t "$APPNAME"
docker run --platform linux/amd64 -p 8080:8080 "$APPNAME" -e CIPHER_KEY="$2"
