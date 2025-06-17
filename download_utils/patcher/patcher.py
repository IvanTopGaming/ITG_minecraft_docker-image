import logging
import os
import subprocess

logging.basicConfig(level=logging.INFO)

ENV_MAPPING = {
    "ACCEPTS_TRANSFERS": "accepts-transfers",
    "ALLOW_FLIGHT": "allow-flight",
    "ALLOW_NETHER": "allow-nether",
    "BROADCAST_CONSOLE_TO_OPS": "broadcast-console-to-ops",
    "BROADCAST_RCON_TO_OPS": "broadcast-rcon-to-ops",
    "BUG_REPORT_LINK": "bug-report-link",
    "DEBUG": "debug",
    "DIFFICULTY": "difficulty",
    "ENABLE_COMMAND_BLOCK": "enable-command-block",
    "ENABLE_JMX_MONITORING": "enable-jmx-monitoring",
    "ENABLE_QUERY": "enable-query",
    "ENABLE_RCON": "enable-rcon",
    "ENABLE_STATUS": "enable-status",
    "ENFORCE_SECURE_PROFILE": "enforce-secure-profile",
    "ENFORCE_WHITELIST": "enforce-whitelist",
    "ENTITY_BROADCAST_RANGE": "entity-broadcast-range-percentage",
    "FORCE_GAMEMODE": "force-gamemode",
    "FUNCTION_PERMISSION_LEVEL": "function-permission-level",
    "GAMEMODE": "gamemode",
    "GENERATE_STRUCTURES": "generate-structures",
    "GENERATOR_SETTINGS": "generator-settings",
    "HARDCORE": "hardcore",
    "HIDE_ONLINE_PLAYERS": "hide-online-players",
    "INITIAL_DISABLED_PACKS": "initial-disabled-packs",
    "INITIAL_ENABLED_PACKS": "initial-enabled-packs",
    "LEVEL_NAME": "level-name",
    "LEVEL_SEED": "level-seed",
    "LEVEL_TYPE": "level-type",
    "LOG_IPS": "log-ips",
    "MAX_CHAINED_UPDATES": "max-chained-neighbor-updates",
    "MAX_PLAYERS": "max-players",
    "MAX_TICK_TIME": "max-tick-time",
    "MAX_WORLD_SIZE": "max-world-size",
    "MOTD": "motd",
    "NETWORK_COMPRESSION": "network-compression-threshold",
    "ONLINE_MODE": "online-mode",
    "OP_PERMISSION_LEVEL": "op-permission-level",
    "PAUSE_WHEN_EMPTY": "pause-when-empty-seconds",
    "PLAYER_IDLE_TIMEOUT": "player-idle-timeout",
    "PREVENT_PROXY_CONNECTIONS": "prevent-proxy-connections",
    "PVP": "pvp",
    "QUERY_PORT": "query.port",
    "RATE_LIMIT": "rate-limit",
    "RCON_PASSWORD": "rcon.password",
    "RCON_PORT": "rcon.port",
    "REGION_COMPRESSION": "region-file-compression",
    "REQUIRE_RESOURCE_PACK": "require-resource-pack",
    "RESOURCE_PACK": "resource-pack",
    "RESOURCE_PACK_ID": "resource-pack-id",
    "RESOURCE_PACK_PROMPT": "resource-pack-prompt",
    "RESOURCE_PACK_SHA1": "resource-pack-sha1",
    "SERVER_IP": "server-ip",
    "SERVER_NAME": "server-name",
    "SERVER_PORT": "server-port",
    "SIMULATION_DISTANCE": "simulation-distance",
    "SPAWN_MONSTERS": "spawn-monsters",
    "SPAWN_PROTECTION": "spawn-protection",
    "SYNC_CHUNK_WRITES": "sync-chunk-writes",
    "TEXT_FILTERING_CONFIG": "text-filtering-config",
    "TEXT_FILTERING_VERSION": "text-filtering-version",
    "USE_NATIVE_TRANSPORT": "use-native-transport",
    "VIEW_DISTANCE": "view-distance",
    "WHITE_LIST": "white-list",
}

MINECRAFT_DIR = "/minecraft"
TMP_DIR = "/tmp"
EULA_SRC = os.path.join(TMP_DIR, "eula.txt")
EULA_DEST = os.path.join(MINECRAFT_DIR, "eula.txt")
PROPERTIES_SRC = os.path.join(TMP_DIR, "server.properties")
PROPERTIES_DEST = os.path.join(MINECRAFT_DIR, "server.properties")
LOG4J_PATCHER_DEST = "/bin/Log4jPatcher.jar"


def transfer_eula():
    try:
        os.makedirs(os.path.dirname(EULA_DEST), exist_ok=True)
        subprocess.run(["cp", EULA_SRC, EULA_DEST], check=True, capture_output=True)
        logging.info(f"Successfully transferred {EULA_SRC} to {EULA_DEST}")
    except FileNotFoundError:
        logging.error(f"Source file not found: {EULA_SRC}")
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to transfer eula.txt: {e}")
        logging.error(f"Stderr: {e.stderr.decode()}")
    except Exception as e:
        logging.error(f"An unexpected error occurred during eula transfer: {e}")


def check_server_properties(func):
    def wrapper(*args, **kwargs):
        if not os.path.exists(PROPERTIES_DEST):
            logging.info(
                f"{PROPERTIES_DEST} not found. Copying from {PROPERTIES_SRC}..."
            )
            try:
                os.makedirs(os.path.dirname(PROPERTIES_DEST), exist_ok=True)
                subprocess.run(
                    ["cp", PROPERTIES_SRC, PROPERTIES_DEST],
                    check=True,
                    capture_output=True,
                )
                logging.info(
                    f"Successfully transferred {PROPERTIES_SRC} to {PROPERTIES_DEST}"
                )
            except FileNotFoundError:
                logging.error(
                    f"Source file not found: {PROPERTIES_SRC}. Cannot proceed with patching."
                )
                return
            except subprocess.CalledProcessError as e:
                logging.error(f"Failed to copy server.properties: {e}")
                logging.error(f"Stderr: {e.stderr.decode()}")
                return
            except Exception as e:
                logging.error(
                    f"An unexpected error occurred during properties copy: {e}"
                )
                return

        return func(*args, **kwargs)
    return wrapper


@check_server_properties
def patch_server_properties():
    logging.info(f"Starting patching process for {PROPERTIES_DEST}")

    lines = []
    properties_to_update = {}
    updated_keys_in_file: set[str] = set()
    updated_count = 0

    for env_var, prop_key in ENV_MAPPING.items():
        env_value = os.getenv(env_var)
        
        if env_value is not None:
            properties_to_update[prop_key] = env_value
            logging.debug(
                f"Found environment variable {env_var}='{env_value}' mapped to property '{prop_key}'"
            )

    if not properties_to_update:
        logging.info(
            "No relevant environment variables set for patching. Skipping file modification."
        )
        return

    try:
        with open(PROPERTIES_DEST, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except Exception as e:
        logging.error(f"Failed to read {PROPERTIES_DEST}: {e}")
        return 

    new_lines: list[str] = []
    processed_keys: set[str] = set()

    for line in lines:
        stripped_line = line.strip()

        if not stripped_line or stripped_line.startswith("#"):
            new_lines.append(line)
            continue

        parts = stripped_line.split("=", 1)
        if len(parts) == 2:
            current_key = parts[0]
            original_value = parts[1]
            processed_keys.add(current_key)

            if current_key in properties_to_update:
                new_value = properties_to_update[current_key]
                if original_value != new_value:
                    new_lines.append(f"{current_key}={new_value}\n")
                    logging.info(
                        f"Updated property '{current_key}' from '{original_value}' to '{new_value}'"
                    )
                    updated_count += 1
                else:
                    new_lines.append(line)
                updated_keys_in_file.add(
                    current_key
                ) 
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)

    added_count = 0
    for prop_key, env_value in properties_to_update.items():
        if prop_key not in processed_keys:
            logging.warning(
                f"Property '{prop_key}' from environment variable was not found in {PROPERTIES_DEST}. Adding it."
            )
            new_lines.append(f"{prop_key}={env_value}\n")
            added_count += 1

    if updated_count > 0 or added_count > 0:
        try:
            with open(PROPERTIES_DEST, "w", encoding="utf-8") as f:
                f.writelines(new_lines)
            logging.info(
                f"Finished patching {PROPERTIES_DEST}. Updated: {updated_count}, Added: {added_count}."
            )
        except Exception as e:
            logging.error(f"Failed to write updated {PROPERTIES_DEST}: {e}")
    else:
        logging.info(f"No properties needed updating or adding in {PROPERTIES_DEST}.")


def download_log4j_patch():
    url = "https://github.com/CreeperHost/Log4jPatcher/releases/download/v1.0.1/Log4jPatcher-1.0.1.jar"
    logging.info(f"Downloading Log4jPatcher from {url}...")
    try:
        os.makedirs(os.path.dirname(LOG4J_PATCHER_DEST), exist_ok=True)
        subprocess.run(
            ["curl", "-fsSL", "-o", LOG4J_PATCHER_DEST, url],
            check=True,
            capture_output=True,
        )
        logging.info(
            f"Successfully downloaded Log4jPatcher.jar to {LOG4J_PATCHER_DEST}"
        )
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to download Log4jPatcher.jar: {e}")
        logging.error(f"Stderr: {e.stderr.decode()}")
    except Exception as e:
        logging.error(f"An unexpected error occurred during Log4jPatcher download: {e}")
