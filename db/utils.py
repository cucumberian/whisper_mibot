import os
from functools import wraps
from datetime import datetime
import hashlib
from aiogram import types
import ffmpeg
from .db import MongoDB
from config import Config

def register_message(func):
    """
    Decorator for registering message in database
    """

    @wraps(func)
    async def inner(message: types.Message, *args, **kwargs):
        try:
            return await func(message, *args, **kwargs)
        finally:
            if Config.MongoDB_string is None:
                return
            event_hash = get_userhash(message.from_user)
            now_time = datetime.now()
            try:
                with MongoDB() as db:
                    db.add_event_to_db(event_hash=event_hash, event_date=now_time)
            except Exception as E:
                print(f"Error: {E}")

    return inner


def get_hash(string: str) -> str:
    """
    Return sha256 hash from string
    :param string: string to hash
    :type string: str
    :return: sha256 hash
    :rtype: str
    """
    return hashlib.shake_128(string.encode()).hexdigest(5)


def get_userhash(user: types.user) -> str:
    """
    Return sha256 hash from user credentials
    :param user: user object
    :type user: types.user
    :return: user hash
    :rtype: str
    """

    user_id = user.id
    user_full_name = f"{user.first_name}{user.last_name}"
    username = user.username
    user_str = f"{user_id}.{user_full_name}.{username}"
    return get_hash(user_str)


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


def get_translate(model, filename: str) -> str:
    try:
        result = model.transcribe(filename)
        return result["text"]
    except Exception as E:
        raise E
    finally:
        os.remove(filename)
