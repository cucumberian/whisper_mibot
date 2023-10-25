import asyncio
import os
import pathlib

from aiogram import Bot
from aiogram import Dispatcher
from aiogram import types
from aiogram.filters.command import Command
from aiogram import F

import torch
import whisper

from config import Config

voice_dir = Config.dirs.get("voice") or "./voice"
audio_dir = Config.dirs.get("audio") or "./audio"
models_dir = Config.dirs.get("models") or "./models"
for dir in [voice_dir, audio_dir, models_dir]:
    pathlib.Path(dir).mkdir(parents=True, exist_ok=True)

device = "cuda" if torch.cuda.is_available() else "cpu"
print("Loading model...")

model = whisper.load_model(Config.model, device=device, download_root=models_dir)
print(f"{'Multilingual' if model.is_multilingual else 'English '}model loaded.")

bot = Bot(token=Config.WHISPER_MIBOT_TOKEN)

dp = Dispatcher()

print("bot started")


@dp.message(Command("start"))
async def command_start(message: types.Message):
    print(f"{message = }")
    await message.answer(f"start command. Chat id: {message.chat.id}")


@dp.message(Command("id"))
async def command_id(message: types.Message):
    await message.reply(
        f"chat id: {message.chat.id}\n" f"user_id: {message.from_user.id}"
    )


@dp.message(Command("help"))
async def help_command(message: types.Message):
    await message.reply("Бот для получения текста из аудио")


@dp.message(F.text)
async def get_text(message: types.Message):
    await message.reply(
        f"Не понимаю: {message.text}\n" f"Наберите команду `\\help` для справки"
    )


@dp.message(F.voice)
async def get_voice(message: types.Message):
    filename = os.path.join(voice_dir, f"{message.voice.file_unique_id}.ogg")
    print(f"{filename = }")
    await bot.download(message.voice, destination=filename)
    mess = await message.reply("Работаю")
    result = model.transcribe(filename)
    await mess.delete()
    try:
        os.remove(filename)
        print(f"file {filename} removed")
    except Exception as E:
        print(f"Cannot remove file {filename}:", E)
    print(f"{result['text'] = }")
    await message.reply(result["text"])


@dp.message(F.audio)
async def get_audio(message: types.Message):
    file_extension = pathlib.Path(message.audio.file_name).suffix
    filename = os.path.join(
        audio_dir, f"{message.audio.file_unique_id}{file_extension}"
    )

    await bot.download(
        message.audio,
        destination=filename,
    )
    print(f"{filename = }")
    mess = await message.reply("Got audio. Working...")

    text = get_translate(filename)
    await mess.delete()
    await message.reply(text)


def get_translate(filename: str) -> str:
    result = model.transcribe(filename)
    try:
        os.remove(filename)
        print(f" file {filename} removed")
    except Exception as E:
        print(f"Cannot remove file {filename}:", E)
    print(f"{result['text'] = }")

    return result["text"]


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
