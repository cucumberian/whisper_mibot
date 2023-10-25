import asyncio
import os
import pathlib

import ffmpeg

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
video_dir = Config.dirs.get("video") or "./video"


device = "cuda" if torch.cuda.is_available() else "cpu"
print("Loading model...")

model = whisper.load_model(Config.model, device=device, download_root=models_dir)
print(
    f"{'Multilingual ' if model.is_multilingual else 'English '}{Config.model} model loaded."
)

bot = Bot(token=Config.WHISPER_MIBOT_TOKEN)

dp = Dispatcher()

print("bot started")


@dp.message(Command("start"))
async def command_start(message: types.Message):
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
@dp.message(F.audio)
async def get_audio(message: types.Message):
    voice_object = message.voice or message.audio
    pathlib.Path(audio_dir).mkdir(parents=True, exist_ok=True)
    filename = os.path.join(audio_dir, f"{voice_object.file_unique_id}")

    mess = await message.reply("Downloading file...")
    try:
        await bot.download(
            voice_object,
            destination=filename,
        )
    except Exception as E:
        await message.reply(f"Error: Cannot download file.\n{E}")
        raise E
    finally:
        await mess.delete()

    mess = await message.reply("Processing audio to text...")
    try:
        text = get_translate(filename)
    except Exception as E:
        await message.reply("Error: Cannot extract text.")
        raise E
    finally:
        await mess.delete()
    await send_long_message(message, text)


async def send_long_message(
    message: types.Message, text: str, max_symbols: int = 4000
) -> None:
    """
    Send some messages if initial message longer then max_symbols
    """
    if len(text) < max_symbols:
        await message.reply(text or "-")
    else:
        for i in range(0, len(text), max_symbols):
            t = text[i : i + 4000]
            await message.answer(text=t)


def video_decoding(video_filename: str, ogg_audio_filename: str) -> None:
    """
    :param video_filename: input video filename
    :type video_filename: str
    :param ogg_audio_filename: output ogg-encoded audio filename
    :type ogg_audio_filename: str
    :return:
    """
    try:
        ffmpeg.input(video_filename).output(
            ogg_audio_filename,
            format="ogg",
            acodec="libvorbis",
            ab="64k",
        ).overwrite_output().run()
    except Exception as E:
        raise E
        os.remove(ogg_audio_filename)
    finally:
        os.remove(video_filename)


@dp.message(F.video)
@dp.message(F.video_note)
@dp.message(F.document)
async def get_video_like(message: types.Message):
    pathlib.Path(video_dir).mkdir(parents=True, exist_ok=True)
    object = message.video or message.video_note or message.document

    filename = os.path.join(
        video_dir,
        f"{object.file_unique_id}",
    )

    mess = await message.reply("Downloading file...")
    try:
        await bot.download(
            object,
            destination=filename,
        )
    except Exception as E:
        await message.reply(f"Error: Cannot download file.\n{E}")
        raise E
    finally:
        await mess.delete()

    output_filename = filename
    if message.document:
        mess = await message.reply("Extracting audio...")
        output_filename = os.path.join(
            video_dir,
            f"{object.file_unique_id}.ogg",
        )
        try:
            video_decoding(filename, output_filename)
        except Exception as E:
            await message.reply(f"Error: Cannot extract audio.\n{E}")
            raise E
        finally:
            await mess.delete()

    mess = await message.reply("Processing audio to text...")
    try:
        text = get_translate(output_filename)
    except Exception as E:
        await message.reply("Error: Cannot extract text.")
        raise E
    finally:
        await mess.delete()
    await send_long_message(message, text)


def get_translate(filename: str) -> str:
    try:
        result = model.transcribe(filename)
        return result["text"]
    except Exception as E:
        raise E
    finally:
        os.remove(filename)
    


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
