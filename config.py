import os


class Config:
    WHISPER_MIBOT_TOKEN = os.environ.get("WHISPER_MIBOT_TOKEN") or 'bot_token'

    # name | params | vram
    # :- | -- | --
    # large | 1550M | 10GB VRAM
    # medium | 769M | 5GB VRAM
    # small | 244M | 2GB VRAM
    # base | 74M | 1GB VRAM
    # tiny | 39M | 1GB VRAM
    model = "small"

    dirs = {
        'models': "./models",
        'audio': "./audio",
        'voice': "./voice",
    }
