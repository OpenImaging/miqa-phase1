#!/bin/sh
set -e

girder serve --host 0.0.0.0 --database mongodb://"$1"/girder &
GIRDER_PID=$!

ansible-playbook -v --extra-vars "$2" /provision.yml

kill "$GIRDER_PID"
wait "$GIRDER_PID" || true

exec girder serve --host 0.0.0.0 --database mongodb://"$1"/girder
