import os
import sys
import asyncio
import logging

from get.get_vanilla_core import get_vanilla_core
from get.get_paper_core import get_paper_core
from get.get_purpur_core import get_purpur_core
from get.get_velocity_core import get_velocity_core

logging.basicConfig(level=logging.INFO, filename="download_util.log", filemode="w")

def get_env_value(name: str):
	return os.getenv(name)
	
game_verison = get_env_value("GAME_VERSION")
core_type = get_env_value("CORE_TYPE")

if os.path.exists("/minecraft/server.jar"):
	logging.info("Server.jar already exists, exiting...")
	sys.exit(-1)

if game_verison == None and core_type == None:
	logging.info("No env's found, exiting...")
	sys.exit(-1)


if core_type == "vanilla":
	asyncio.run(get_vanilla_core(game_verison))
elif core_type == "paper":
	asyncio.run(get_paper_core(game_verison))
elif core_type == "purpur":
	asyncio.run(get_purpur_core(game_verison))
elif core_type == "velocity":
	asyncio.run(get_velocity_core(game_verison))
else:
	logging.error("Unknown core type, exiting...")
	sys.exit(-1)