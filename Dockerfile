FROM debian:bookworm-slim AS builder

WORKDIR /download_utils

COPY download_utils .

RUN apt update && \ 
	apt install -y \
    binutils \
    python3 \
    python3-pip && \
	rm -rf /var/lib/apt/lists/*

RUN pip3 install --no-cache-dir --break-system-packages -r requirements.txt

RUN pyinstaller -F main.py

FROM ivantopgaming/mini_graalvm:latest

RUN apt update && \
    apt install -y curl fontconfig && \
	rm -rf /var/lib/apt/lists/*

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