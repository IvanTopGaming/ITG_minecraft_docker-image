ARG BUILDER_IMAGE=ubuntu:jammy
ARG BASE_IMAGE=ghcr.io/ivantopgaming/mini_graalvm:25

# ===== 1. Build the core downloader into a standalone binary =====
FROM ${BUILDER_IMAGE} AS builder

WORKDIR /app/download_utils

RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y \
       binutils \
       python3 \
       python3-pip \
    && rm -rf /var/lib/apt/lists/*

COPY download_utils/requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt

COPY download_utils ./
RUN pyinstaller -F main.py

# ===== 2. Runtime =====
FROM ${BASE_IMAGE}

LABEL org.opencontainers.image.source="https://github.com/IvanTopGaming/ITG_minecraft_docker-image"
LABEL org.opencontainers.image.description="Minecraft server image with automatic core download (Vanilla, Paper, Purpur, Fabric, Velocity, Leaf)"
LABEL org.opencontainers.image.licenses="MIT"

RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
       ca-certificates \
       curl \
       fontconfig \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /minecraft

RUN mkdir -p /opt/minecraft

COPY resources/eula.txt /tmp/eula.txt
COPY resources/server.properties /tmp/server.properties
COPY --from=builder /app/download_utils/dist/main /bin/download_utils
COPY scripts/start_server.sh /scripts/start_server.sh

RUN chmod +x /scripts/start_server.sh /bin/download_utils

ENV ENABLE_LOG4J_PATCH=true
ENV JVM_OPTS="-Xmx4G -Xms4G"
ENV CORE_JAR=server.jar
ENV PATCHER_DIR=/opt/minecraft
ENV PUID=1000
ENV PGID=1000

EXPOSE 25565

HEALTHCHECK --interval=30s --timeout=5s --start-period=180s --retries=3 \
    CMD bash -c 'exec 3<>/dev/tcp/127.0.0.1/${SERVER_PORT:-25565}' || exit 1

ENTRYPOINT ["/scripts/start_server.sh"]
