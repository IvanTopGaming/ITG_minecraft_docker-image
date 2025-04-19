#!/bin/bash

/bin/main

if [ "$ENABLE_LOG4J_PATCH" = "true" ]; then
    exec java -javaagent:/bin/Log4jPatcher.jar ${JVM_OPTS} -jar ${CORE_JAR} nogui
else
    exec java ${JVM_OPTS} -jar ${CORE_JAR} nogui
fi