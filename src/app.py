import asyncio

from aiogram import Bot
from aiogram import Dispatcher
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.filters import CommandStart
from aiogram import F
from aiogram.enums import ParseMode


from db.utils import register_message
from service.aiogram_service import transcribe_file
from service.aiogram_service import send_long_message
from config import Config

from service.whisper_service import WhisperAPI


print("Loading model...")


bot = Bot(token=Config.WHISPER_MIBOT_TOKEN)
dp = Dispatcher()
dp["whisper"] = WhisperAPI(transcribe_url=Config.WHISPER_BACKEND_URL)

print("bot started")


@dp.message(CommandStart())
async def command_start(message: Message):
    await message.reply(f"start command. Chat id: {message.chat.id}")


@dp.message(Command("id"))
@register_message
async def command_id(message: Message):
    print(f"{message.chat.id = }")
    await message.reply(
        f"Chat id: {message.chat.id}\n"
        + f"user_id: {message.from_user.id if message.from_user else None}"
    )


@dp.message(Command("help"))
@register_message
async def help_command(message: Message):
    await message.reply("Бот для получения текста из аудио")


@dp.message(F.text)
@register_message
async def get_text(message: Message):
    await message.reply(
        f"Не понимаю: {message.text}\n"
        f"Наберите команду `\\help` для справки",
        parse_mode=ParseMode.MARKDOWN_V2,
    )


@dp.message(F.audio)
@dp.message(F.voice)
@dp.message(F.video)
@dp.message(F.video_note)
@dp.message(F.document)
@register_message
async def get_processing_entity(message: Message, whisper: WhisperAPI):
    entity = message.video or message.video_note or message.document
    if entity is None:
        await message.reply("Не удалось найти данные")
        return

    mess = await bot.send_message(
        chat_id=message.chat.id,
        text="Работаю...",
        reply_to_message_id=message.message_id,
    )
    transcribed_text = None
    try:
        transcribed_text = await transcribe_file(
            file_id=entity.file_id, bot=bot, whisper=whisper
        )
    except Exception:
        pass
    if transcribed_text is None:
        await mess.edit_text(text="Не удалось распознать аудио")
        return
    mess.delete()
    await send_long_message(text=transcribed_text, message=message)


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
