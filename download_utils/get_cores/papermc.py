import httpx
import hashlib
import os
import sys
import logging

from tqdm import tqdm

logging.basicConfig(level=logging.INFO)

core_jar = os.getenv("CORE_JAR", "server.jar")
API_BASE = "https://fill.papermc.io/v3"
HEADERS = {
	"Accept": "application/json",
	"User-agent": "ITG_minecraft_docker-image (+https://github.com/IvanTopGaming/ITG_minecraft_docker-image)"
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


async def get_latest_download(project: str, version: str):
	url = f"{API_BASE}/projects/{project}/versions/{version}/builds/latest"

	async with httpx.AsyncClient() as client:
		try:
			response = await client.get(url=url, headers=HEADERS, follow_redirects=True)
			response.raise_for_status()
		except httpx.HTTPStatusError as exc:
			logging.error(f"{project} {version}: API returned {exc.response.status_code} for {exc.request.url!r}")
			return None
		except httpx.RequestError as exc:
			logging.error(f"An error occurred while requesting {exc.request.url!r}: {exc}")
			return None

	try:
		download = response.json()['downloads']['server:default']
		return download['url'], download['checksums']['sha256']
	except (KeyError, ValueError) as exc:
		logging.error(f"Unexpected API response for {project} {version}: {exc}")
		return None


async def download_build(url: str, true_hash: str):
	async with httpx.AsyncClient() as client:
		async with client.stream("GET", url, headers=HEADERS, follow_redirects=True) as response:
			response.raise_for_status()
			total = int(response.headers.get("Content-Length", 0))
			with open(core_jar, "wb") as file, tqdm(
				total=total,
				unit="iB",
				unit_scale=True,
				unit_divisor=1024,
				desc=core_jar
			) as progress:
				async for chunk in response.aiter_bytes():
					file.write(chunk)
					progress.update(len(chunk))

	if get_file_hash("sha256") == true_hash:
		logging.info("Hashes match")
	else:
		logging.error("Hashes do not match")
		sys.exit(-1)


async def get_papermc_core(project: str, version: str):
	result = await get_latest_download(project, version)

	if result is None:
		logging.error("Could not retrieve the latest build.")
		sys.exit(-1)

	url, true_hash = result

	await download_build(url, true_hash)
