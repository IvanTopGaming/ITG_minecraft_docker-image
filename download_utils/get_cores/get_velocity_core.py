from get_cores.papermc import get_papermc_core


async def get_velocity_core(version: str):
	await get_papermc_core("velocity", version)


if __name__ == '__main__':
	import asyncio
	asyncio.run(get_velocity_core('3.4.0-SNAPSHOT'))
