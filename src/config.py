import os


class Config:
    WHISPER_MIBOT_TOKEN = os.environ["WHISPER_MIBOT_TOKEN"]
    WHISPER_BACKEND_URL = os.environ["WHISPER_BACKEND_URL"]
    
    MongoDB_string = os.environ.get("MONGO_STRING")
    MongoDB_db_name = "whisper_mibot"
