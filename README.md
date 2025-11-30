# Whisper Telegram bot

## Описание

Простой телеграм бот, который извлекает из аудио слова.

Работает с бэкэндом [faster-whisper-fastapi](https://github.com/cucumberian/faster-whisper-fastapi/tree/main), который и занимается обработкой аудио.
Бэкэнд сделан на основе модели whisper от openai: https://github.com/openai/whisper.

## Работа с ботом

Перетянуть или переслать боту аудио сообщение или аудио файл.
После его обработки бот в ответ отправит переведенный текст.

## Типы сообщений

Бот работает с файлами ___меньше 20 МБ__.
Бот работает с сообщениями содержащими:

- аудио файлы
- голосовые сообщения
- видео
- видео-записки
- документы

## Установка и запуск

### Напрямую

1. __Переменные окружения__
    Бот использует переменную окружения `WHISPER_MIBOT_TOKEN` и `WHISPER_BACKEND_URL`.
    Первая задаёт токен для бота, полученный от `@BotFather` в телеграмме.
    Вторая определяет адрес сервиса для извлечения текста из речи.

    Задать данные переменные окружения можно _любым удобным способом_,
    например, вписав их значения напрямую в конфиг `config.py`.

2. __Установка зависимостей и запуск__
    Переходим в каталог с программой и устанавливаем зависимости для python 3.9+

  ```shell
  cd src
  pip3 install -r requirements.txt
  python app.py
  ```

### docker-compose

1. Создаете файл `.env` рядом с `docker-compose.yml` c переменными окружения.

  ```shell
  WHISPER_MIBOT_TOKEN="<bot_token>"
  WHISPER_BACKEND_URL="<http://127.0.0.1:8000/transcribe>"
  ```

2. Запускаете

  ```shell
  docker-compose up -d
  ```

### Запуск как сервиса в Linux

Создать файл `/etc/systemd/system/whisper-mibot.service` со следующим содержимым:

```conf
[Unit]
Description=Telegram bot whisper-mibot
After=syslog.target
After=network.target

[Service]
Type=simple
User=<username>
Group=<usergroup>
WorkingDirectory=/home/<username>/whisper_mibot
ExecStart=/home/<username>/whisper_mibot/.venv/bin/python3 /home/<username>/whisper_mibot/app.py
RestartSec=30
Restart=always
KillMode=control-group
EnvironmentFile=/home/<username>/whisper_mibot/.env

[Install]
WantedBy=multi-user.target
```

, в котором вместо `<username>` и `<usergroup>` подставить имя пользователя и группу пользователя, от имени которого будет запускаться сервис.
Важно указать в параметре `ExecStart` правильный путь до интерпретатора python и путь до файла программы `app.py`.
Параметр `EnvironmentFile` указывает путь до файла `.env`, в котором записана переменная окружения `WHISPER_MIBOT_TOKEN` и `WHISPER_BACKEND_URL`.
Пример файла `.env`:

```env
WHISPER_MIBOT_TOKEN="<bot_token>"
WHISPER_BACKEND_URL="<http://127.0.0.1:8000/transcribe>"
```

Далее включить и запустить сервис командами:

```shell
sudo systemctl enable whisper-mibot.service
sudo systemctl start whisper-mibot.service
```

## Логирование

Имеется возможность логирования событий в базу данных MongoDB.
При логировании записывается __хеш__ (_получаемый из имени и телеграм ид пользователя_) и __время обращения__ к боту. Если переменная со строкой подключения с MongoDB будет не определена, то запись событий не происходит.
Настройки MongoDB Находятся в файле `consfig.py` и определяются двумя параметрами:

- `MongoDB_string` - строка подключения к монго
- `MongoDB_db_name` - имя базы данных
