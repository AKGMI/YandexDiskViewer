from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.core.cache import cache
from .yandex_disk_service import YandexDiskService
from urllib.parse import urlparse, parse_qs, unquote
import os
import zipfile
import asyncio
import mimetypes
import hashlib

def index(request):
    files = []
    error_message = None
    public_key = request.GET.get('public_key')
    file_type_filter = request.GET.get('file_type')

    if public_key:
        cache_key = f"files_{hashlib.md5(public_key.encode()).hexdigest()}"
        files = cache.get(cache_key)

        if not files:
            service = YandexDiskService(public_key)
            files, error_message = asyncio.run(service.get_files_list())

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

def download(request):
    file_url = unquote(request.GET.get('file_url'))

    parsed_url = urlparse(file_url)
    query_params = parse_qs(parsed_url.query)
    file_name = query_params.get('filename')[0]

    download_dir = 'downloads'
    save_path = os.path.join(download_dir, file_name)

    service = YandexDiskService('')
    asyncio.run(service.download_file(file_url, save_path))

    with open(save_path, 'rb') as f:
        response = HttpResponse(f.read(), content_type='application/octet-stream')
        response['Content-Disposition'] = f'attachment; filename={file_name}'
        cleanup_downloads(download_dir)
        return response

    return HttpResponseRedirect('/')

def download_selected(request):
    if request.method == 'POST':
        selected_files = request.POST.getlist('selected_files')
        zip_filename = "selected_files.zip"
        download_dir = 'downloads'

        if not os.path.exists(download_dir):
            os.makedirs(download_dir)

        with zipfile.ZipFile(zip_filename, 'w') as zipf:
            for file_url in selected_files:
                service = YandexDiskService('')
                saved_file_path = asyncio.run(service.download_file(file_url, download_dir))
                if saved_file_path:
                    zipf.write(saved_file_path, os.path.basename(saved_file_path))

        with open(zip_filename, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/zip')
            response['Content-Disposition'] = f'attachment; filename=' + zip_filename
            cleanup_downloads(download_dir)
            return response

    return HttpResponseRedirect('/')

def cleanup_downloads(directory):
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                os.rmdir(file_path)
        except Exception as e:
            print(f'Не удалось удалить {file_path}. Причина: {e}')