### Minecraft Server Docker Image

This Docker image provides a ready-to-use Minecraft server, configured for easy deployment and customization. It supports both GraalVM and Zulu JDK for different performance and compatibility needs.

#### Features:
- **Customizable Server Properties**: Easily configure server settings via environment variables.
- **GraalVM and Zulu JDK Support**: Choose between GraalVM for performance or Zulu JDK for lightweight and compatibility with older Minecraft versions.
- **Automatic Restart**: The server automatically restarts unless explicitly stopped.
- **Persistent Data**: Server data is stored in a volume for persistence.

#### How to Deploy:

1. **Create a `docker-compose.yml` file**:
   ```yaml
   version: '3.8'
   services:
     minecraft:
       image: ivantopgaming/minecraft_server:latest
       container_name: survival
       ports:
         - "25565:25565"
       volumes:
         - ./server:/minecraft
       environment:
         - JVM_OPTS=-Xmx8G -Xms8G
         - CORE_JAR=server.jar
         - DIFFICULTY=hard
         - ALLOW_NETHER=false
         - MOTD=Waiting for players...
         - ONLINE_MODE=false
       restart: unless-stopped
       stop_grace_period: 120s
       stdin_open: true
       tty: true
   ```

2. **Start the server**:
   ```bash
   docker-compose up -d
   ```

#### Customization:
- **Environment Variables**: Modify server properties by setting environment variables in the `docker-compose.yml` file. For example, to change the difficulty, set `DIFFICULTY=hard`.
- **Volume Mounting**: The server data is stored in the `./server` directory on your host machine. Ensure this directory exists before starting the container.

#### Using Zulu JDK:
For lighter images or compatibility with older Minecraft versions, use the Zulu JDK-based images:
- **Zulu 11**: `docker.io/ivantopgaming/minecraft_server:zulu-11`
- **Zulu (Latest)**: `docker.io/ivantopgaming/minecraft_server:zulu-23`

#### Reporting Issues:
If you encounter any bugs or issues, please contact **zjarc0@mail.ru**.

#### Notes:
- Ensure you have Docker and Docker Compose installed.
- Adjust `JVM_OPTS` based on your server's memory requirements.
- The server will automatically restart unless manually stopped, ensuring minimal downtime.

This image is designed for ease of use and flexibility, making it suitable for both casual and advanced Minecraft server administrators.
