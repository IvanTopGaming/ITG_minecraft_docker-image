#!/bin/bash
set -e

PUID=${PUID:-1000}
PGID=${PGID:-1000}

if [ "$(id -u)" = "0" ] && [ "$PUID" != "0" ]; then
    if ! getent group "$PGID" >/dev/null; then
        groupadd -g "$PGID" minecraft
    fi

    if ! getent passwd "$PUID" >/dev/null; then
        useradd -u "$PUID" -g "$PGID" -d /minecraft -s /usr/sbin/nologin minecraft
    fi

    chown "$PUID:$PGID" /minecraft "$PATCHER_DIR"

    exec setpriv --reuid="$PUID" --regid="$PGID" --init-groups --inh-caps=-all "$0" "$@"
fi

export HOME=/minecraft

/bin/download_utils || true

if [ ! -s "/minecraft/${CORE_JAR}" ]; then
    echo "[entrypoint] /minecraft/${CORE_JAR} is missing — core download failed, or set GAME_VERSION and CORE_TYPE to fetch one." >&2
    exit 1
fi

if [ "$ENABLE_LOG4J_PATCH" = "true" ] && [ -s "$PATCHER_DIR/Log4jPatcher.jar" ]; then
    exec java -javaagent:"$PATCHER_DIR/Log4jPatcher.jar" ${JVM_OPTS} -jar ${CORE_JAR} ${POST_JVM_OPTS} nogui
else
    exec java ${JVM_OPTS} -jar ${CORE_JAR} ${POST_JVM_OPTS} nogui
fi
