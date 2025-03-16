#!/bin/bash

cp /tmp/eula.txt /minecraft/eula.txt

/utils/setup_properties.sh
/utils/download_utils/dist/main

exec /utils/start_server.sh