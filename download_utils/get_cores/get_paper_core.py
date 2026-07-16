from get_cores.papermc import get_papermc_core


async def get_paper_core(version: str):
	await get_papermc_core("paper", version)


if __name__ == '__main__':
	import asyncio
	asyncio.run(get_paper_core('1.21.8'))
