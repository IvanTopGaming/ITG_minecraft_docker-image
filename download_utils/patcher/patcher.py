import logging
import os
import subprocess

logging.basicConfig(level=logging.INFO)

MINECRAFT_DIR = "/minecraft"
TMP_DIR = "/tmp"
EULA_SRC = os.path.join(TMP_DIR, "eula.txt")
EULA_DEST = os.path.join(MINECRAFT_DIR, "eula.txt")
PROPERTIES_SRC = os.path.join(TMP_DIR, "server.properties")
PROPERTIES_DEST = os.path.join(MINECRAFT_DIR, "server.properties")
PATCHER_DIR = os.getenv("PATCHER_DIR", "/opt/minecraft")
LOG4J_PATCHER_DEST = os.path.join(PATCHER_DIR, "Log4jPatcher.jar")


def mapping_generator():
	with open(PROPERTIES_DEST, "r") as f:
		for line in f:
			b = line.split("=")[0]
			a = b.upper().replace("-", "_")

			yield a, b


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

	mappings = mapping_generator()

	for env_var, prop_key in mappings:
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
		
		os.environ["ENABLE_LOG4J_PATCH"] = "False"
		logging.error("ENABLE_LOG4J_PATCH set to False due to download failure.")
	except Exception as e:
		logging.error(f"An unexpected error occurred during Log4jPatcher download: {e}")
		
		os.environ["ENABLE_LOG4J_PATCH"] = "False"
		logging.error("ENABLE_LOG4J_PATCH set to False due to download failure.")
