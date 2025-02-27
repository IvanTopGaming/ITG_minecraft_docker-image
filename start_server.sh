#!/bin/bash

exec java -javaagent:/utils/Log4jPatcher.jar ${JVM_OPTS} -jar ${CORE_JAR} nogui