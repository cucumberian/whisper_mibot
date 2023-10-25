# Whisper Telegram bot
## Описание
Простой телеграм бот, который расшифровывает аудио речь в слова.
Сделано на основе модели whisper от openai: https://github.com/openai/whisper.

## Работа с ботом
Перетянуть или переслать боту аудио сообщение или аудио файл.
После его обработки бот в ответ отправит переведенный текст.

## Типы сообщений
Бот не может закачать файлы больше 20 МБ.
Бот работает с сообщениями содержащими:
- аудио файлы
- голосовые сообщения
- видео
- видео-записки
- документы

## Установка и запуск
### Зависимости
Для установки потребуется набор ffmpeg.
```shell
sudo apt install ffmpeg
```
И установка зависимостей пайтона:
```shell
pip3 install -r requirements.txt
```
### Переменные окружения
Бот использует переменную окружения `WHISPER_MIBOT_TOKEN`,
которая задаёт токен для бота, полученный от @BotFather в телеграмме.

Задать данную переменную окружения можно любым удобным способом,
например, вписав её значение напрямую в конфиг `config.py`.

### Запуск
```shell
python3 app.py
```

## Дополнительно
### Настройки модели
В файле `config.py` можно выбрать модель, которая будет использоваться для распознавания речи.
Чем более качественная модель будет выбрана, тем медленнее она будет работать.
[Примерная таблица моделей](https://github.com/openai/whisper/blob/main/README.md#available-models-and-languages):
|  Size  | Parameters | English-only model | Multilingual model | Required VRAM | Relative speed |
|:------:|:----------:|:------------------:|:------------------:|:-------------:|:--------------:|
|  tiny  |    39 M    |     `tiny.en`      |       `tiny`       |     ~1 GB     |      ~32x      |
|  base  |    74 M    |     `base.en`      |       `base`       |     ~1 GB     |      ~16x      |
| small  |   244 M    |     `small.en`     |      `small`       |     ~2 GB     |      ~6x       |
| medium |   769 M    |    `medium.en`     |      `medium`      |     ~5 GB     |      ~2x       |
| large  |   1550 M   |        N/A         |      `large`       |    ~10 GB     |       1x       |

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
Параметр `EnvironmentFile` указывает путь до файла `.env`, в котором записана переменная окружения `WHISPER_MIBOT_TOKEN`.
Пример файла `.env`:
```env
WHISPER_MIBOT_TOKEN=<bot_token>
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