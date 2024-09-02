from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, HttpRequest
from django.core.cache import cache
from django.contrib import messages
from .yandex_disk_service import YandexDiskService
from urllib.parse import urlparse, parse_qs, unquote
import os
import zipfile
import asyncio
import hashlib
from typing import List, Optional, Dict


def index(request: HttpRequest) -> HttpResponse:
    """
    Представление для отображения списка файлов и директорий с Яндекс.Диска.

    :param request: Объект запроса Django, содержащий параметры запроса.
    :return: HttpResponse с рендерингом страницы, отображающей файлы и директории.
    """
    files: List[Dict] = []
    error_message: Optional[str] = None
    public_key: Optional[str] = request.GET.get('public_key')
    file_type_filter: Optional[str] = request.GET.get('file_type')
    path: str = request.GET.get('path', '/')

    if public_key:
        cache_key: str = f"files_{hashlib.md5((public_key + path).encode()).hexdigest()}"
        files = cache.get(cache_key)

        if not files:
            service = YandexDiskService(public_key)
            files, error_message = asyncio.run(service.get_files_list(path))

            if files:
                cache.set(cache_key, files, timeout=600)

        if files and file_type_filter:
            files = [file for file in files if file['mime_type'].startswith(file_type_filter)]

    context = {
        'files': files,
        'public_key': public_key,
        'error_message': error_message,
        'file_type_filter': file_type_filter,
    }

    return render(request, 'disk/index.html', context)

def download(request: HttpRequest) -> HttpResponse:
    """
    Представление для загрузки отдельного файла с Яндекс.Диска.

    :param request: Объект запроса Django, содержащий параметры запроса, включая URL файла.
    :return: HttpResponse с файлом для скачивания или перенаправление в случае ошибки.
    """
    file_url: str = unquote(request.GET.get('file_url', ''))

    parsed_url = urlparse(file_url)
    query_params = parse_qs(parsed_url.query)
    file_name: str = query_params.get('filename', [''])[0]

    download_dir: str = 'downloads'
    save_path: str = os.path.join(download_dir, file_name)

    service = YandexDiskService('')

    try:
        asyncio.run(service.download_file(file_url, save_path))

        with open(save_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/octet-stream')
            response['Content-Disposition'] = f'attachment; filename={file_name}'
            cleanup_downloads(download_dir)
            return response

    except Exception as e:
        messages.error(request, f'Ошибка при загрузке файла: {str(e)}')
        return HttpResponseRedirect('/')

def download_selected(request: HttpRequest) -> HttpResponse:
    """
    Представление для скачивания выбранных файлов в виде ZIP-архива.

    :param request: Объект запроса Django, содержащий список выбранных файлов.
    :return: HttpResponse с ZIP-архивом для скачивания или перенаправление в случае ошибки.
    """
    if request.method == 'POST':
        selected_files: List[str] = request.POST.getlist('selected_files')
        zip_filename: str = "selected_files.zip"
        download_dir: str = 'downloads'

        if not os.path.exists(download_dir):
            os.makedirs(download_dir)

        try:
            with zipfile.ZipFile(zip_filename, 'w') as zipf:
                for file_url in selected_files:
                    parsed_url = urlparse(file_url)
                    query_params = parse_qs(parsed_url.query)
                    file_name: str = query_params.get('filename')[0]

                    service = YandexDiskService('')
                    saved_file_path: Optional[str] = asyncio.run(service.download_file(file_url, f'{download_dir}/{file_name}'))
                    if saved_file_path:
                        zipf.write(saved_file_path, os.path.basename(saved_file_path))

            with open(zip_filename, 'rb') as f:
                response = HttpResponse(f.read(), content_type='application/zip')
                response['Content-Disposition'] = f'attachment; filename=' + zip_filename
                cleanup_downloads(download_dir)
                return response

        except Exception as e:
            messages.error(request, f'Ошибка при создании ZIP-архива: {str(e)}')
            return HttpResponseRedirect('/')

    return HttpResponseRedirect('/')

def cleanup_downloads(directory: str) -> None:
    """
    Удаляет все файлы и директории в указанной директории.

    :param directory: Путь к директории, которую нужно очистить.
    """
    for filename in os.listdir(directory):
        file_path: str = os.path.join(directory, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                os.rmdir(file_path)
        except Exception as e:
            print(f'Не удалось удалить {file_path}. Причина: {e}')