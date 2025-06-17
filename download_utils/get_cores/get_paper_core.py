import httpx
import re
import hashlib
import sys
import logging

from tqdm import tqdm

logging.basicConfig(level=logging.INFO)

HEADERS = {
	"Accept": "application/json",
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

	with open('server.jar',"rb") as f:
		for byte_block in iter(lambda: f.read(4096),b""):
			hash.update(byte_block)
		
	return hash.hexdigest()


async def compare_hash(version: str, file_hash: str, algorithm: str):
	async with httpx.AsyncClient() as client:
		url = f'https://api.papermc.io/v2/projects/paper/versions/{version}/builds/'
		try:
			response = await client.get(url=url, headers=HEADERS)
			if response.status_code == 200:
				true_hash = response.json()['builds'][-1]['downloads']['application'][algorithm]
				if true_hash == file_hash:
					return True
		except httpx.RequestError as exc:
			logging.error(f"An error occurred while requesting {exc.request.url!r}: {exc}")

		return False


async def get_latest_build_name(version: str):
	async with httpx.AsyncClient() as client:
		url = f"https://api.papermc.io/v2/projects/paper/versions/{version}/builds/"
		try:
			response = await client.get(url=url, headers=HEADERS)
			if response.status_code == 200:
				return response.json()['builds'][-1]['downloads']['application']['name']
		except httpx.RequestError as exc:
			logging.error(f"An error occurred while requesting {exc.request.url!r}: {exc}")
			
		return None


def fetch_version_and_build(filename: str):
	pattern = r"paper-(\d+\.\d+\.\d+)-(\d+)\.jar"

	match = re.search(pattern, filename)

	if match:
		version = match.group(1)
		number = match.group(2)
	
		return version, number

	return None 


async def download_build(version: str, build: str):
	url = f'https://api.papermc.io/v2/projects/paper/versions/{version}/builds/{build}/downloads/paper-{version}-{build}.jar'

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

	algorithm = "sha256"
	file_hash = get_file_hash(algorithm)

	if await compare_hash(version, file_hash, algorithm):
		logging.info("Hashes match")
	else:
		logging.error("Hashes do not match")
		sys.exit(-1)


async def get_paper_core(version: str):
	latest_build_name = await get_latest_build_name(version)

	if latest_build_name is None:
		logging.error("Could not retrieve the latest build name.")
		sys.exit(-1)

	result = fetch_version_and_build(latest_build_name)
	
	if result is None:
		logging.error("Could not fetch version and build from build name.")
		sys.exit(-1)

	version, build = result

	await download_build(version, build)


if __name__ == '__main__':
	import asyncio
	asyncio.run(get_paper_core('1.21.5'))