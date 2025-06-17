import os
import sys
import asyncio
import logging

from get_cores.get_vanilla_core import get_vanilla_core
from get_cores.get_paper_core import get_paper_core
from get_cores.get_purpur_core import get_purpur_core
from get_cores.get_velocity_core import get_velocity_core
from get_cores.get_fabric_core import get_fabric_core

from patcher.patcher import download_log4j_patch, transfer_eula, patch_server_properties

logging.basicConfig(level=logging.INFO, filename="download_util.log", filemode="w")

SUPPORTED_CORES = ["vanilla", "paper", "purpur", "velocity", "fabric"]

game_verison = os.getenv("GAME_VERSION")
core_type = os.getenv("CORE_TYPE")
core_jar = os.getenv("CORE_JAR", "server.jar")

download_log4j_patch()

if game_verison == None or core_type == None:
	logging.info("No env's found, exiting...")
	sys.exit(-1)


if core_type in SUPPORTED_CORES and core_type != SUPPORTED_CORES[3]:
	transfer_eula()
	patch_server_properties()


if os.path.exists(f"/minecraft/{core_jar}"):
	logging.info(f"{core_jar} already exists, exiting...")
	sys.exit(-1)


if core_type == SUPPORTED_CORES[0]:
	asyncio.run(get_vanilla_core(game_verison))
elif core_type == SUPPORTED_CORES[1]:
	asyncio.run(get_paper_core(game_verison))
elif core_type == SUPPORTED_CORES[2]:
	asyncio.run(get_purpur_core(game_verison))
elif core_type == SUPPORTED_CORES[3]:
	asyncio.run(get_velocity_core(game_verison))
elif core_type == SUPPORTED_CORES[4]:
	asyncio.run(get_fabric_core(game_verison))
else:
	logging.error("Unknown core type, exiting...")
	sys.exit(-1)