# Minecraft Server Docker Image

[![Build and publish](https://github.com/IvanTopGaming/ITG_minecraft_docker-image/actions/workflows/docker-image.yml/badge.svg)](https://github.com/IvanTopGaming/ITG_minecraft_docker-image/actions/workflows/docker-image.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

A ready-to-use Minecraft server image. Point it at a version and a core type — it downloads the
server jar itself, writes `eula.txt` and `server.properties`, and starts the server.

## Features

- **Automatic core download** — latest build of Vanilla, Paper, Purpur, Fabric, Velocity or Leaf,
  with checksum verification.
- **Configuration via environment** — every key in `server.properties` is settable as an env var.
- **GraalVM or Zulu** — GraalVM for throughput, Zulu for older Minecraft versions.
- **Log4Shell patch** — [Log4jPatcher](https://github.com/CreeperHost/Log4jPatcher) applied as a
  java agent, on by default.
- **Persistent data** — everything lives in `/minecraft`, mount it and keep it.

## Images

Published to GHCR on every push to `main` and rebuilt monthly for upstream security patches.

| Tag | Java | Base image |
| --- | --- | --- |
| `graalvm-25`, `latest` | 25 | [`mini_graalvm:25`](https://github.com/IvanTopGaming/ITG_MiniDocker_GraalVM) |
| `graalvm-24` | 24 | `mini_graalvm:24` |
| `graalvm-21` | 21 | `mini_graalvm:21` |
| `zulu-24` | 24 | `azul/zulu-openjdk:24` |
| `zulu-21` | 21 | `azul/zulu-openjdk:21` |
| `zulu-17` | 17 | `azul/zulu-openjdk:17` |
| `zulu-11` | 11 | `azul/zulu-openjdk:11` |

```bash
docker pull ghcr.io/ivantopgaming/minecraft_server:latest
```

The GraalVM variants run on [ITG_MiniDocker_GraalVM](https://github.com/IvanTopGaming/ITG_MiniDocker_GraalVM):
GraalVM CE built from source with the Graal JIT, at roughly half the size of the official image.
Use a Zulu variant for Minecraft versions that predate the Java you want.

## Quick start

```yaml
services:
  minecraft:
    image: ghcr.io/ivantopgaming/minecraft_server:graalvm-25
    container_name: survival
    ports:
      - "25565:25565"
    volumes:
      - ./server:/minecraft
    environment:
      - JVM_OPTS=-Xmx4G -Xms4G
      - GAME_VERSION=1.21.8
      - CORE_TYPE=leaf
      - DIFFICULTY=hard
      - MOTD=Waiting for players...
      - ONLINE_MODE=false
    restart: unless-stopped
    stop_grace_period: 120s
    stdin_open: true
    tty: true
```

```bash
docker compose up -d
```

The `./server` directory is created on first start and holds the world, configs and the core jar.

## Configuration

### Image variables

| Variable | Default | Description |
| --- | --- | --- |
| `GAME_VERSION` | — | Minecraft version, e.g. `1.21.8`. Required to download a core. |
| `CORE_TYPE` | — | `vanilla`, `paper`, `purpur`, `fabric`, `velocity` or `leaf`. Required to download a core. |
| `CORE_JAR` | `server.jar` | Jar to download into and run. If it already exists, the download is skipped. |
| `JVM_OPTS` | `-Xmx4G -Xms4G` | Flags passed before `-jar`. |
| `POST_JVM_OPTS` | — | Flags passed after `-jar`, i.e. to the server itself (e.g. `--safeMode`). |
| `ENABLE_LOG4J_PATCH` | `true` | Run the server under the Log4jPatcher agent. |

Drop `GAME_VERSION` and `CORE_TYPE` to manage the jar yourself — the downloader exits and the
server starts from whatever `CORE_JAR` points at.

### Server properties

Any key in `server.properties` maps to an env var: uppercase it and turn dashes into underscores.
`difficulty` → `DIFFICULTY`, `allow-nether` → `ALLOW_NETHER`, `view-distance` → `VIEW_DISTANCE`,
and so on. Keys are applied on every start, so changing a variable and recreating the container is
enough — no need to edit the file by hand.

`velocity` skips this step: as a proxy it uses its own config rather than `server.properties`.

## Building locally

One `Dockerfile` covers every variant; the runtime is chosen with `BASE_IMAGE`:

```bash
docker build -t minecraft_server:graalvm-25 .
docker build -t minecraft_server:zulu-21 --build-arg BASE_IMAGE=azul/zulu-openjdk:21 .
```

Any Debian- or Ubuntu-based JDK image works as a base.

## EULA

The image ships an `eula.txt` with `eula=true`. Running it means you accept the
[Minecraft EULA](https://aka.ms/MinecraftEULA).

## Issues

Bugs and questions: [zjarc0@mail.ru](mailto:zjarc0@mail.ru) or the
[issue tracker](https://github.com/IvanTopGaming/ITG_minecraft_docker-image/issues).

## License

MIT © IvanTopGaming — see [LICENSE](LICENSE). Minecraft, the server cores and GraalVM are covered
by their own licenses.
