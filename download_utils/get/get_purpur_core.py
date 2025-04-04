import httpx
import hashlib
import sys
import logging


logging.basicConfig(level=logging.INFO)

HEADERS = {
	"Accept": "*/*",
	"User-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"
}


def get_file_hash(algorithm):
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


async def compare_hash(version, build, file_hash, algorithm):
	async with httpx.AsyncClient() as client:
		url = f'https://api.purpurmc.org/v2/purpur/{version}/{build}/'
		
		response = await client.get(url=url, headers=HEADERS)
		
		if response.status_code == 200:
			true_hash = response.json()[algorithm]

		if true_hash == file_hash:
			return True


async def get_latest_build(version: str):
	async with httpx.AsyncClient() as client:
		url = f"https://api.purpurmc.org/v2/purpur/{version}/"
		
		response = await client.get(url=url, headers=HEADERS)
		
		if response.status_code == 200:
			return response.json()['builds']['latest']

		logging.error("Failed to get latest build")
		return None


async def download_build(version: str, build: str):
	url = f'https://api.purpurmc.org/v2/purpur/{version}/{build}/download/'

	async with httpx.AsyncClient() as client:
		async with client.stream("GET", url, headers=HEADERS) as response:
			if response.status_code == 200:
				with open("server.jar", "wb") as file:
					async for chunk in response.aiter_bytes():
						file.write(chunk)

	algorithm = "md5"
	file_hash = get_file_hash(algorithm)

	if await compare_hash(version, build, file_hash, algorithm):
		logging.info("Hashes match")
	else:
		logging.error("Hashes do not match")
		sys.exit(-1)

async def get_purpur_core(version):
	latest_build = await get_latest_build(version)

	await download_build(version, latest_build)