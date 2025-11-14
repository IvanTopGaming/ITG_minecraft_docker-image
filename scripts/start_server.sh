#!/bin/bash

/bin/download_utils
/bin/api &

if [ "$ENABLE_LOG4J_PATCH" = "true" ]; then
    exec java -javaagent:/bin/Log4jPatcher.jar ${JVM_OPTS} -jar ${CORE_JAR} ${POST_JVM_OPTS} nogui
else
    exec java ${JVM_OPTS} -jar ${CORE_JAR} ${POST_JVM_OPTS} nogui
fi