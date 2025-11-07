import httpx
import hashlib
import os
import sys
import logging

from tqdm import tqdm

logging.basicConfig(level=logging.INFO)

core_jar = os.getenv("CORE_JAR", "server.jar")
HEADERS = {
	"Accept": "*/*",
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


async def compare_hash(version: str, build: str, file_hash: str, algorithm: str):
	async with httpx.AsyncClient() as client:
		url = f'https://api.leafmc.one/v2/projects/leaf/versions/{version}/builds/{build}'
		try:
			response = await client.get(url=url, headers=HEADERS)
			if response.status_code == 200:
				true_hash = response.json()['downloads']['primary'][algorithm]
				if true_hash == file_hash:
					return True
		except httpx.RequestError as exc:
			logging.error(f"An error occurred while requesting {exc.request.url!r}: {exc}")

		return False


async def get_latest_build(version: str):
	async with httpx.AsyncClient() as client:
		url = f"https://api.leafmc.one/v2/projects/leaf/versions/{version}"
		try:
			response = await client.get(url=url, headers=HEADERS)
			if response.status_code == 200:
				return response.json()['builds'][-1]
		except httpx.RequestError as exc:
			logging.error(f"An error occurred while requesting {exc.request.url!r}: {exc}")
			
		return None


async def download_build(version: str, build: str):
	url = f'https://api.leafmc.one/v2/projects/leaf/versions/{version}/builds/{build}/downloads/leaf-{version}-{build}.jar'

	async with httpx.AsyncClient() as client:
		async with client.stream("GET", url) as response:
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

	algorithm = "sha256"
	file_hash = get_file_hash(algorithm)

	if await compare_hash(version, build, file_hash, algorithm):
		logging.info("Hashes match")
	else:
		logging.error("Hashes do not match")
		sys.exit(-1)

async def get_leaf_core(version: str):
	latest_build = await get_latest_build(version)

	if latest_build is None:
		logging.error("Could not retrieve the latest build.")
		sys.exit(-1)

	await download_build(version, latest_build)


if __name__ == '__main__':
	import asyncio
	asyncio.run(get_leaf_core('1.21.8'))