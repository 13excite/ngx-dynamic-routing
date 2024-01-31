#!/bin/bash

APP2_RSP_FILE="app2_rsp.html"
APP1_RSP_FILE="app1_rsp.html"

EXPECTED_MD5_APP2="3205e4bf631f4078af066cab61985a34"
EXPECTED_MD5_APP1="45032b3c5930032b139adbdb95ecc3bc"

curl -L -o $APP2_RSP_FILE 127.0.0.1:8080/?app=2 2>/dev/null
curl -L -o $APP1_RSP_FILE 127.0.0.1:8080/?app=1 2>/dev/null


md5sum -c - <<<"${EXPECTED_MD5_APP2} ${APP2_RSP_FILE}"
md5sum -c - <<<"${EXPECTED_MD5_APP1} ${APP1_RSP_FILE}"

# clear
rm -f $APP2_RSP_FILE
rm -f $APP1_RSP_FILE
