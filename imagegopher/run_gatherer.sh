#!/bin/bash

export PYTHONPATH=$(pwd):$(pwd)/gatherer

export GOPHER_GATHERER_CONFIG=../sample_configs/gatherer/config.ini
export GOPHER_GATHERER_CONFIG_REQUIRED=YES

# Python Quart environment variables
export QUART_APP=gatherer
export QUART_DEBUG=true
export GOPHER_GATHERER_SVC_LISTEN_PORT=3001

quart run -p $GOPHER_GATHERER_SVC_LISTEN_PORT  -h 0.0.0.0
