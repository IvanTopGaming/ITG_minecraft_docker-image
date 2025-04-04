#!/bin/bash

if [ "$ENABLE_LOG4J_PATCH" = "true" ]; then
    exec java -javaagent:/utils/Log4jPatcher.jar ${JVM_OPTS} -jar ${CORE_JAR} nogui
else
    exec java ${JVM_OPTS} -jar ${CORE_JAR} nogui
fi