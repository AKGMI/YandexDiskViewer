import aiohttp
import asyncio

class YandexDiskService:
    def __init__(self, public_key: str):
        self.base_url = "https://cloud-api.yandex.net/v1/disk/public/resources"
        self.public_key = public_key

    async def get_files_list(self, path='/'):
        params = {
            'public_key': self.public_key,
            'path': path
        }
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(self.base_url, params=params) as response:
                    print(response)
                    if response.status == 200:
                        data = await response.json()
                        return data['_embedded']['items'], None
                    elif response.status == 404:
                        return None, "Путь не найден или публичная ссылка неверная."
                    else:
                        return None, f"Ошибка: {response.status}"
            except aiohttp.ClientError as e:
                return None, f"Ошибка соединения: {str(e)}"

    async def download_file(self, file_url: str, save_path: str):
        async with aiohttp.ClientSession() as session:
            async with session.get(file_url) as response:
                if response.status == 200:
                    with open(save_path, 'wb') as f:
                        f.write(await response.read())
                    return True
                return False
