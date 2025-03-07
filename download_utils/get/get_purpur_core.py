
import httpx

HEADERS = {
	"Accept": "*/*",
	"User-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"
}


async def get_latest_build(version: str):
	async with httpx.AsyncClient() as client:
		url = f"https://api.purpurmc.org/v2/purpur/{version}/"
		
		response = await client.get(url=url, headers=HEADERS)
		
		if response.status_code == 200:
			return response.json()['builds']['latest']

		print("Failed to get latest build")
		return None


async def download_build(version: str, build: str):
	url = f'https://api.purpurmc.org/v2/purpur/{version}/{build}/download/'

	async with httpx.AsyncClient() as client:
		async with client.stream("GET", url, headers=HEADERS) as response:
			if response.status_code == 200:
				with open("server.jar", "wb") as file:
					async for chunk in response.aiter_bytes():
						file.write(chunk)


async def get_purpur_core(version):
	latest_build = await get_latest_build(version)

	await download_build(version, latest_build)