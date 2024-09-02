from django.shortcuts import render
from django.http import HttpResponse
from .yandex_disk_service import YandexDiskService
import os
import asyncio

def index(request):
    files = []
    error_message = None
    public_key = request.GET.get('public_key')

    if public_key:
        service = YandexDiskService(public_key)
        files, error_message = asyncio.run(service.get_files_list())

    context = {
        'files': files,
        'public_key': public_key,
        'error_message': error_message
    }

    return render(request, 'disk/index.html', context)

def download(request):
    file_url = request.GET.get('file_url')
    file_name = request.GET.get('file_name')

    service = YandexDiskService('')
    save_path = os.path.join('downloads', file_name)

    asyncio.run(service.download_file(file_url, save_path))

    with open(save_path, 'rb') as f:
        response = HttpResponse(f.read(), content_type='application/octet-stream')
        response['Content-Disposition'] = f'attachment; filename={file_name}'
        return response