FROM container-registry.oracle.com/os/oraclelinux:9-slim AS builder

WORKDIR /download_utils

COPY download_utils .

RUN microdnf install -y \
    binutils \
    python3 \
    python3-pip && \
    microdnf clean all && \
    rm -rf /var/cache/dnf

RUN pip install --no-cache-dir -r requirements.txt

RUN pyinstaller -F main.py

FROM ghcr.io/graalvm/jdk-community:latest

RUN microdnf update --nodocs && \
    microdnf install -y fontconfig && \
    microdnf clean all && \
    rm -rf /var/cache/dnf

WORKDIR /minecraft

COPY resources/eula.txt /tmp/eula.txt
COPY resources/server.properties /tmp/server.properties

COPY --from=builder /download_utils/dist/main /bin/main

COPY /scripts /scripts

RUN chmod +x \
    /scripts/start_server.sh \
    /bin/main

ENV ENABLE_LOG4J_PATCH=true
ENV JVM_OPTS="-Xmx4098M -Xms4098M"

ENTRYPOINT ["/scripts/start_server.sh"]