# Yandex Disk Viewer

## Описание

Yandex Disk Viewer — это веб-приложение на Django, которое позволяет просматривать файлы на Яндекс.Диске по публичной ссылке и загружать их на свой компьютер.

## Функциональность

- Просмотр файлов и папок на Яндекс.Диске по публичной ссылке.
- Фильтрация файлов по типу.
- Загрузка отдельных файлов.
- Создание и скачивание ZIP-архивов с выбранными файлами.

## Установка

1. Склонируйте репозиторий:
```bash
git clone https://github.com/username/yandex-disk-viewer.git
cd yandex-disk-viewer
```

2. Создайте и активируйте виртуальное окружение:
```bash
python -m venv venv
source venv/bin/activate  # Для Windows: venv\Scripts\activate
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

4. Выполните миграции:
```bash
python manage.py migrate
```

5. Запустите сервер разработки:
```bash
python manage.py runserver
```

## Использование
- Откройте браузер и перейдите по адресу http://127.0.0.1:8000/.
- Введите публичную ссылку на Яндекс.Диск и просматривайте доступные файлы.