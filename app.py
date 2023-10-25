import asyncio
import os
import pathlib

from aiogram import Bot
from aiogram import Dispatcher
from aiogram import types
from aiogram.filters.command import Command
from aiogram import F

import torch
import gc
import whisper

from config import Config

voice_dir = Config.dirs.get("voice") or "./voice"
audio_dir = Config.dirs.get("audio") or "./audio"
models_dir = Config.dirs.get("models") or "./models"
for dir in [voice_dir, audio_dir, models_dir]:
    pathlib.Path(dir).mkdir(parents=True, exist_ok=True)

device = 'cuda' if torch.cuda.is_available() else 'cpu'
print("Loading model...")

model = whisper.load_model(Config.model, device=device, download_root=models_dir)
print(
    f"{'Multilingual' if model.is_multilingual else 'English '}model loaded."
)

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
        f"chat id: {message.chat.id}\n"
        f"user_id: {message.from_user.id}"
    )


@dp.message(Command("help"))
async def help_command(message: types.Message):
    await message.reply(
        "Бот для получения текста из аудио"
    )


@dp.message(F.text)
async def get_text(message: types.Message):
    await message.reply(
        f"Не понимаю: {message.text}\n"
        f"Наберите команду `\\help` для справки"
    )


@dp.message(F.voice)
async def get_voice(message: types.Message):
    filename = os.path.join(voice_dir, f"{message.voice.file_unique_id}.ogg")
    print(f"{filename = }")
    await bot.download(
        message.voice,
        destination=filename
    )
    mess = await message.reply("Работаю")
    result = model.transcribe(filename)
    await mess.delete()
    try:
        os.remove(filename)
        print(f"file {filename} removed")
    except Exception as E:
        print(f"Cannot remove file {filename}:", E)
    print(f"{result['text'] = }")
    await message.reply(result['text'])


# Message(
#     message_id=24,
#     date=datetime.datetime(2023, 8, 18, 9, 0, 43, tzinfo=datetime.timezone.utc),
#     chat=Chat(
#         id=94658085,
#         type='private',
#         title=None,
#         username='fowdeqaqogji',
#         first_name='Mi Vi',
#         last_name=None,
#         is_forum=None,
#         photo=None,
#         active_usernames=None,
#         emoji_status_custom_emoji_id=None,
#         bio=None,
#         has_private_forwards=None,
#         has_restricted_voice_and_video_messages=None,
#         join_to_send_messages=None,
#         join_by_request=None,
#         description=None,
#         invite_link=None,
#         pinned_message=None,
#         permissions=None,
#         slow_mode_delay=None,
#         message_auto_delete_time=None,
#         has_aggressive_anti_spam_enabled=None,
#         has_hidden_members=None,
#         has_protected_content=None,
#         sticker_set_name=None,
#         can_set_sticker_set=None,
#         linked_chat_id=None,
#         location=None
#     ),
#     message_thread_id=None,
#     from_user=User(
#         id=94658085,
#         is_bot=False,
#         first_name='Mi Vi',
#         last_name=None,
#         username='fowdeqaqogji',
#         language_code='en',
#         is_premium=None,
#         added_to_attachment_menu=None,
#         can_join_groups=None,
#         can_read_all_group_messages=None,
#         supports_inline_queries=None
#     ),
#     sender_chat=None,
#     forward_from=None,
#     forward_from_chat=None,
#     forward_from_message_id=None,
#     forward_signature=None,
#     forward_sender_name=None,
#     forward_date=None,
#     is_topic_message=None,
#     is_automatic_forward=None,
#     reply_to_message=None,
#     via_bot=None,
#     edit_date=None,
#     has_protected_content=None,
#     media_group_id=None,
#     author_signature=None,
#     text=None,
#     entities=None,
#     animation=None,
#     audio=None,
#     document=None,
#     photo=None,
#     sticker=None,
#     video=None,
#     video_note=None,
#     voice=Voice(
#         file_id='AwACAgIAAxkBAAMYZN8zOzHwb8PA_OOt0y0rgDJLPdwAAmgxAAK8hflKKM-tj0EdA7MwBA',
#         file_unique_id='AgADaDEAAryF-Uo',
#         duration=1,
#         mime_type='audio/ogg',
#         file_size=391
#     ),
#     caption=None,
#     caption_entities=None,
#     has_media_spoiler=None,
#     contact=None,
#     dice=None,
#     game=None,
#     poll=None,
#     venue=None,
#     location=None,
#     new_chat_members=None,
#     left_chat_member=None,
#     new_chat_title=None,
#     new_chat_photo=None,
#     delete_chat_photo=None,
#     group_chat_created=None,
#     supergroup_chat_created=None,
#     channel_chat_created=None,
#     message_auto_delete_timer_changed=None,
#     migrate_to_chat_id=None,
#     migrate_from_chat_id=None,
#     pinned_message=None,
#     invoice=None,
#     successful_payment=None,
#     user_shared=None,
#     chat_shared=None,
#     connected_website=None,
#     write_access_allowed=None,
#     passport_data=None,
#     proximity_alert_triggered=None,
#     forum_topic_created=None,
#     forum_topic_edited=None,
#     forum_topic_closed=None,
#     forum_topic_reopened=None,
#     general_forum_topic_hidden=None,
#     general_forum_topic_unhidden=None,
#     video_chat_scheduled=None,
#     video_chat_started=None,
#     video_chat_ended=None,
#     video_chat_participants_invited=None,
#     web_app_data=None,
#     reply_markup=None
# )


@dp.message(F.audio)
async def get_audio(message: types.Message):
    file_extension = pathlib.Path(message.audio.file_name).suffix
    filename = os.path.join(audio_dir, f"{message.audio.file_unique_id}{file_extension}")

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


# message = Message(
#     message_id=86,
#     date=datetime.datetime(2023, 8, 18, 11, 20, 55, tzinfo=datetime.timezone.utc),
#     chat=Chat(
#         id=94658085,
#         type='private',
#         title=None,
#         username='fowdeqaqogji',
#         first_name='Mi Vi',
#         last_name=None,
#         is_forum=None,
#         photo=None,
#         active_usernames=None,
#         emoji_status_custom_emoji_id=None,
#         bio=None,
#         has_private_forwards=None,
#         has_restricted_voice_and_video_messages=None,
#         join_to_send_messages=None,
#         join_by_request=None,
#         description=None,
#         invite_link=None,
#         pinned_message=None,
#         permissions=None,
#         slow_mode_delay=None,
#         message_auto_delete_time=None,
#         has_aggressive_anti_spam_enabled=None,
#         has_hidden_members=None,
#         has_protected_content=None,
#         sticker_set_name=None,
#         can_set_sticker_set=None,
#         linked_chat_id=None,
#         location=None
#     ),
#     message_thread_id=None,
#     from_user=User(
#         id=94658085,
#         is_bot=False,
#         first_name='Mi Vi',
#         last_name=None,
#         username='fowdeqaqogji',
#         language_code='en',
#         is_premium=None,
#         added_to_attachment_menu=None,
#         can_join_groups=None,
#         can_read_all_group_messages=None,
#         supports_inline_queries=None
#     ),
#     sender_chat=None,
#     forward_from=None,
#     forward_from_chat=None,
#     forward_from_message_id=None,
#     forward_signature=None,
#     forward_sender_name=None,
#     forward_date=None,
#     is_topic_message=None,
#     is_automatic_forward=None,
#     reply_to_message=None,
#     via_bot=None,
#     edit_date=None,
#     has_protected_content=None,
#     media_group_id=None,
#     author_signature=None,
#     text=None,
#     entities=None,
#     animation=None,
#     audio=Audio(
#         file_id='CQACAgIAAxkBAANWZN9UF7WMRQpRY_jIy1byQg69dWQAApUyAAK8hflKMfqlOrAdohUwBA',
#         file_unique_id='AgADlTIAAryF-Uo',
#         duration=296,
#         performer='Takumi Kato',
#         title='Tone 10',
#         file_name='Takumi Kato - Tone 10.mp3',
#         mime_type='audio/mpeg',
#         file_size=11868288,
#         thumb=None
#     ),
#     document=None,
#     photo=None,
#     sticker=None,
#     video=None,
#     video_note=None,
#     voice=None,
#     caption=None,
#     caption_entities=None,
#     has_media_spoiler=None,
#     contact=None,
#     dice=None,
#     game=None,
#     poll=None,
#     venue=None,
#     location=None,
#     new_chat_members=None,
#     left_chat_member=None,
#     new_chat_title=None,
#     new_chat_photo=None,
#     delete_chat_photo=None,
#     group_chat_created=None,
#     supergroup_chat_created=None,
#     channel_chat_created=None,
#     message_auto_delete_timer_changed=None,
#     migrate_to_chat_id=None,
#     migrate_from_chat_id=None,
#     pinned_message=None,
#     invoice=None,
#     successful_payment=None,
#     user_shared=None,
#     chat_shared=None,
#     connected_website=None,
#     write_access_allowed=None,
#     passport_data=None,
#     proximity_alert_triggered=None,
#     forum_topic_created=None,
#     forum_topic_edited=None,
#     forum_topic_closed=None,
#     forum_topic_reopened=None,
#     general_forum_topic_hidden=None,
#     general_forum_topic_unhidden=None,
#     video_chat_scheduled=None,
#     video_chat_started=None,
#     video_chat_ended=None,
#     video_chat_participants_invited=None,
#     web_app_data=None,
#     reply_markup=None
# )


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
