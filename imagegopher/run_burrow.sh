#!/bin/bash

export PYTHONPATH=$(pwd):$(pwd)/burrow

# Python Quart environment variables
export QUART_APP=burrow
export QUART_DEBUG=true
export GOPHER_BURROW_SVC_LISTEN_PORT=3002

quart run -p $GOPHER_BURROW_SVC_LISTEN_PORT  -h 0.0.0.0
