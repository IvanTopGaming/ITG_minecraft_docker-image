import httpx
import re
import hashlib
import sys


HEADERS = {
	"Accept": "application/json",
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
		print("Unknown hash algorithm")
		sys.exit(-1)

	with open('server.jar',"rb") as f:
		for byte_block in iter(lambda: f.read(4096),b""):
			hash.update(byte_block)
		
	return hash.hexdigest()


async def compare_hash(version, file_hash, algorithm):
	async with httpx.AsyncClient() as client:
		url = f'https://api.papermc.io/v2/projects/paper/versions/{version}/builds/'
		
		response = await client.get(url=url, headers=HEADERS)
		
		if response.status_code == 200:
			true_hash = response.json()['builds'][-1]['downloads']['application'][algorithm]

		if true_hash == file_hash:
			return True


async def get_latest_build_name(version: str):
	async with httpx.AsyncClient() as client:
		url = f"https://api.papermc.io/v2/projects/paper/versions/{version}/builds/"
		
		response = await client.get(url=url, headers=HEADERS)
		
		if response.status_code == 200:
			return response.json()['builds'][-1]['downloads']['application']['name']

		print("Failed to get latest build name")
		return None


def fetch_version_and_build(filename: str):
	pattern = r"paper-(\d+\.\d+\.\d+)-(\d+)\.jar"

	match = re.search(pattern, filename)

	if match:
		version = match.group(1)
		number = match.group(2)
	
		return version, number

	print("Failed to fetch version and build")
	return None 


async def download_build(version: str, build: str):
	url = f'https://api.papermc.io/v2/projects/paper/versions/{version}/builds/{build}/downloads/paper-{version}-{build}.jar'

	async with httpx.AsyncClient() as client:
		async with client.stream("GET", url, headers=HEADERS) as response:
			if response.status_code == 200:
				with open("server.jar", "wb") as file:
					async for chunk in response.aiter_bytes():
						file.write(chunk)
	
	algorithm = "sha256"
	file_hash = get_file_hash(algorithm)

	if await compare_hash(version, file_hash, algorithm):
		print("Hashes match")
	else:
		print("Hashes do not match")
		sys.exit(-1)


async def get_paper_core(version: str):
	latest_build_name = await get_latest_build_name(version)
	version, build = fetch_version_and_build(latest_build_name)

	await download_build(version, build)