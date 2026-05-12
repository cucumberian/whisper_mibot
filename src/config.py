import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    WHISPER_MIBOT_TOKEN = os.environ["WHISPER_MIBOT_TOKEN"]
    STT_API_URL = os.environ.get("STT_API_URL", "http://host.docker.internal:8000")
    TELEGRAM_API_URL = os.environ.get("TELEGRAM_API_URL", "https://api.telegram.org")
    
    MONGO_STRING = os.environ.get("MONGO_STRING")
    MongoDB_db_name = "whisper_mibot"
