import httpx
import hashlib
import os
import sys
import logging

from tqdm import tqdm
from typing import Optional, List, Dict, Any

logging.basicConfig(level=logging.INFO)

core_jar = os.getenv("CORE_JAR", "server.jar")
HEADERS = {
	"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
	"User-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"
}


def get_file_hash(algorithm: str):
	if algorithm == 'sha256':
		hash = hashlib.sha256()
	elif algorithm == 'md5':
		hash = hashlib.md5()
	elif algorithm == 'sha1':
		hash = hashlib.sha1()
	else:
		logging.error("Unknown hash algorithm")
		sys.exit(-1)

	with open(core_jar,"rb") as f:
		for byte_block in iter(lambda: f.read(4096),b""):
			hash.update(byte_block)
		
	return hash.hexdigest()


async def compare_hash(true_hash: str, file_hash: str):
	if true_hash == file_hash:
		return True


async def get_versions():
	async with httpx.AsyncClient() as client:
		url = f"https://piston-meta.mojang.com/mc/game/version_manifest_v2.json"
		try:
			response = await client.get(url=url, headers=HEADERS)
			if response.status_code == 200:
				return response.json()['versions']
		except httpx.RequestError as exc:
			logging.error(f"An error occurred while requesting {exc.request.url!r}: {exc}")
		
		return None



def get_version_url(version: str, versions: List[Dict[str, Any]]) -> Optional[str]:
	for version_instance in versions:
		if version_instance['id'] == version:
			return version_instance['url']
	 
	return None


async def get_core_url(version_url: str):
	async with httpx.AsyncClient() as client:
		try:
			response = await client.get(url=version_url, headers=HEADERS)
			if response.status_code == 200:
				return response.json()['downloads']['server']
		except httpx.RequestError as exc:
			logging.error(f"An error occurred while requesting {exc.request.url!r}: {exc}")
		
		return None


async def download_build(core_url: Dict[str, Any]):
	async with httpx.AsyncClient() as client:
		async with client.stream("GET", core_url['url']) as response:
			response.raise_for_status()
			total = int(response.headers.get("Content-Length", 0))
			with open(core_jar, "wb") as file, tqdm(
				total=total,
				unit="iB",
				unit_scale=True,
				unit_divisor=1024,
				desc=core_jar
			) as progress:
				num_bytes_downloaded = 0
				async for chunk in response.aiter_bytes():
					file.write(chunk)
					num_bytes_downloaded += len(chunk)
					progress.update(len(chunk))

	algorithm = "sha1"
	file_hash = get_file_hash(algorithm)

	if await compare_hash(core_url[algorithm], file_hash):
		logging.info("Hashes match")
	else:
		logging.error("Hashes do not match")
		sys.exit(-1)


async def get_vanilla_core(version: str):
	versions = await get_versions()

	if versions is None:
		logging.error("Failed to get versions")
		sys.exit(-1)

	version_url = get_version_url(version, versions)
	
	if version_url is None:
		logging.error("Could not find version URL for the specified version.")
		sys.exit(-1)
	
	core_url = await get_core_url(version_url)
	
	if core_url is None:
		logging.error("Could not get core URL.")
		sys.exit(-1)

	await download_build(core_url)


if __name__ == '__main__':
	import asyncio
	asyncio.run(get_vanilla_core('1.21.4'))