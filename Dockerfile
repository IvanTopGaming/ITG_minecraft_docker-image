FROM container-registry.oracle.com/os/oraclelinux:9-slim AS builder

WORKDIR /download_utils

COPY download_utils .

RUN microdnf install python3
RUN microdnf install python3-pip
RUN microdnf install binutils

RUN pip install -r requirements.txt

RUN pyinstaller -F main.py

FROM ghcr.io/graalvm/jdk-community:latest

WORKDIR /minecraft

COPY server.properties /tmp/server.properties

COPY --from=builder /download_utils/dist/main /utils/download_utils/dist/main

COPY entrypoint.sh /utils/entrypoint.sh
COPY setup_properties.sh /utils/setup_properties.sh
COPY start_server.sh /utils/start_server.sh
COPY Log4jPatcher-1.0.1.jar /utils/Log4jPatcher.jar

RUN chmod +x /utils/entrypoint.sh /utils/setup_properties.sh /utils/start_server.sh /utils/download_utils/dist/main

ENV JVM_OPTS="-Xmx4098M -Xms4098M"

ENTRYPOINT ["/utils/entrypoint.sh"]