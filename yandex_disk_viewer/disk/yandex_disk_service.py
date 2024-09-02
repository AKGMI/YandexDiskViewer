import aiohttp
import asyncio
from typing import Optional, Tuple, List, Dict


class YandexDiskService:
    def __init__(self, public_key: str):
        """
        Инициализация сервиса для работы с Яндекс.Диском.

        :param public_key: Публичный ключ для доступа к ресурсам Яндекс.Диска.
        """
        self.base_url = "https://cloud-api.yandex.net/v1/disk/public/resources"
        self.public_key = public_key

    async def get_files_list(self, path: str = '/') -> Tuple[Optional[List[Dict]], Optional[str]]:
        """
        Получает список файлов и папок по заданному пути на Яндекс.Диске.

        :param path: Путь внутри публичной директории Яндекс.Диска (по умолчанию '/').
        :return: Кортеж (список элементов, сообщение об ошибке).
        """
        params = {
            'public_key': self.public_key,
            'path': path
        }
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(self.base_url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data['_embedded']['items'], None
                    elif response.status == 404:
                        return None, "Путь не найден или публичная ссылка неверная."
                    else:
                        return None, f"Ошибка: {response.status}"
            except aiohttp.ClientError as e:
                return None, f"Ошибка соединения: {str(e)}"

    async def download_file(self, file_url: str, save_path: str) -> Optional[str]:
        """
        Скачивает файл по заданному URL и сохраняет его по указанному пути.

        :param file_url: Прямая ссылка на файл.
        :param save_path: Локальный путь для сохранения файла.
        :return: Путь к сохраненному файлу или None в случае ошибки.
        """
        async with aiohttp.ClientSession() as session:
            async with session.get(file_url) as response:
                if response.status == 200:
                    with open(save_path, 'wb') as f:
                        f.write(await response.read())
                    return save_path
                return None
