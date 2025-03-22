#!/bin/bash

/utils/download_utils/dist/main

if ! unzip -l "/minecraft/server.jar" | awk '{print $4}' | grep -qx "default-velocity.toml"; then
	echo "Copying config files"
    cp /tmp/eula.txt /minecraft/eula.txt
    /utils/setup_properties.sh
fi

exec /utils/start_server.sh