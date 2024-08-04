import requests
from schema.whisper_schema import WhisperServiceResponse


class WhisperAPI:
    def __init__(self, transcribe_url: str):
        self.transcribe_url = transcribe_url

    async def transcribe(self, audio: bytes, timeout: int = 300) -> str | None:
        url = f"{self.transcribe_url}"
        response = requests.post(
            url=url, files={"audio": audio}, timeout=timeout
        )

        if not response.ok:
            return None
        whisper_response = WhisperServiceResponse(**response.json())

        if whisper_response.status == "error":
            return None
        return whisper_response.response
