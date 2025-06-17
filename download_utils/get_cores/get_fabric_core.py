import httpx
import sys
import logging

from tqdm import tqdm

logging.basicConfig(level=logging.INFO)

HEADERS = {
	"Accept": "*/*",
	"User-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"
}


async def check_version(version: str):
	async with httpx.AsyncClient() as client:
		url = f"https://meta.fabricmc.net/v2/versions/game"
		try:
			response = await client.get(url=url, headers=HEADERS)
			if response.status_code == 200:
				return any(item['version'] == version for item in response.json())
		except httpx.RequestError as exc:
			logging.error(f"An error occurred while requesting {exc.request.url!r}: {exc}")

		return None


async def get_latest_loader():
	async with httpx.AsyncClient() as client:
		url = f"https://meta.fabricmc.net/v2/versions/loader"
		try:
			response = await client.get(url=url, headers=HEADERS)
			if response.status_code == 200:
				return response.json()[0]['version']
		except httpx.RequestError as exc:
			logging.error(f"An error occurred while requesting {exc.request.url!r}: {exc}")

		return None


async def get_latest_installer():
	async with httpx.AsyncClient() as client:
		url = f"https://meta.fabricmc.net/v2/versions/installer"
		try:
			response = await client.get(url=url, headers=HEADERS)
			if response.status_code == 200:
				return response.json()[0]['version']
		except httpx.RequestError as exc:
			logging.error(f"An error occurred while requesting {exc.request.url!r}: {exc}")
			
		return None


async def download_installer(version: str, loader: str, installer: str):
	url = f'https://meta.fabricmc.net/v2/versions/loader/{version}/{loader}/{installer}/server/jar'

	async with httpx.AsyncClient() as client:
		async with client.stream("GET", url) as response:
			response.raise_for_status()
			total = int(response.headers.get("Content-Length", 0))
			with open('server.jar', "wb") as file, tqdm(
				total=total,
				unit="iB",
				unit_scale=True,
				unit_divisor=1024,
				desc='server.jar'
			) as progress:
				num_bytes_downloaded = 0
				async for chunk in response.aiter_bytes():
					file.write(chunk)
					num_bytes_downloaded += len(chunk)
					progress.update(len(chunk))


async def get_fabric_core(version: str):
	if not await check_version(version):
		logging.error("Version not found")
		sys.exit(-1)

	loader = await get_latest_loader()

	if loader is None:
		logging.error("Failed to fetch loader version.")
		sys.exit(-1)

	installer = await get_latest_installer()

	if installer is None:
		logging.error("Failed to fetch installer version.")
		sys.exit(-1)

	await download_installer(version, loader, installer)


if __name__ == '__main__':
	import asyncio
	asyncio.run(get_fabric_core('1.21.4'))