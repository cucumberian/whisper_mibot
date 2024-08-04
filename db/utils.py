from typing import Any
from datetime import datetime
from functools import wraps
import hashlib

from aiogram.types import Message
from aiogram.types import User

from .db import MongoDB
from config import Config


def register_message(func):
    """
    Decorator for registering message in database
    """

    @wraps(func)
    async def inner(
        message: Message, *args: list[Any], **kwargs: dict[Any, Any]
    ):
        try:
            return await func(message, *args, **kwargs)
        finally:
            if Config.MongoDB_string is None:
                return
            event_hash = get_userhash(message.from_user)
            now_time = datetime.now()
            try:
                with MongoDB() as db:
                    db.add_event_to_db(
                        event_hash=event_hash, event_date=now_time
                    )
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


def get_userhash(user: User) -> str:
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
