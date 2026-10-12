#!/usr/bin/bash

INTERFACE="asgi"
APP_MODULE="main:app"
HOST="0.0.0.0"
PORT="8080"
LOOP="auto"
WORKERS="1"

exec granian \
  --interface $INTERFACE \
  $APP_MODULE \
  --host $HOST \
  --port $PORT \
  --loop $LOOP \
  --workers $WORKERS
