docker build -t docker.io/ivantopgaming/minecraft_server:zulu-24 -f Dockerfile.zulu-24 .
docker build -t docker.io/ivantopgaming/minecraft_server:zulu-21 -f Dockerfile.zulu-21 .
docker build -t docker.io/ivantopgaming/minecraft_server:zulu-17 -f Dockerfile.zulu-17 .
docker build -t docker.io/ivantopgaming/minecraft_server:zulu-11 -f Dockerfile.zulu-11 .

docker build -t docker.io/ivantopgaming/minecraft_server:graalvm-17 -f Dockerfile.graalvm-17 .
docker build -t docker.io/ivantopgaming/minecraft_server:graalvm-21 -f Dockerfile.graalvm-21 .
docker build -t docker.io/ivantopgaming/minecraft_server:latest .


docker push docker.io/ivantopgaming/minecraft_server:zulu-24
docker push docker.io/ivantopgaming/minecraft_server:zulu-21
docker push docker.io/ivantopgaming/minecraft_server:zulu-17
docker push docker.io/ivantopgaming/minecraft_server:zulu-11

docker push docker.io/ivantopgaming/minecraft_server:graalvm-17
docker push docker.io/ivantopgaming/minecraft_server:graalvm-21
docker push docker.io/ivantopgaming/minecraft_server:latest