from aiogram.types import Message
from aiogram import Bot
from service.whisper_service import WhisperAPI, WhisperException


async def send_long_message(
    message: "Message", text: str, max_symbols: int = 4000
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


async def transcribe_file(file_id: str, bot: "Bot", whisper: "WhisperAPI"):
    file_info = await bot.get_file(file_id=file_id)
    file_binaryio = await bot.download(file=file_info.file_id)
    if file_binaryio is None:
        raise WhisperException("File not found")
    file_bytes = file_binaryio.read()
    transcribed_text = await whisper.transcribe(audio=file_bytes)
    return transcribed_text
