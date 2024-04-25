#!/bin/bash

export PYTHONPATH=$(pwd):$(pwd)/web_portal

export GOPHER_WEB_PORTAL_CONFIG=../sample_configs/web_portal/config.ini
export GOPHER_GATHERER_CONFIG_REQUIRED=YES

# Python Quart environment variables
export QUART_APP=web_portal
export QUART_DEBUG=true
export GOPHER_WEB_PORTAL_SVC_LISTEN_PORT=8080

quart run -p $GOPHER_WEB_PORTAL_SVC_LISTEN_PORT  -h 0.0.0.0
