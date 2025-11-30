import httpx


class WhisperException(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class WhisperAPI:
    def __init__(self, transcribe_url: str):
        self.transcribe_url = transcribe_url

    async def transcribe(self, audio: bytes, timeout: int = 300) -> str:
        """Отправляет запрос на перевод внешнему апи"""
        url = f"{self.transcribe_url}"
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url=url, files={"audio": audio}, timeout=timeout
            )
            if not response.is_success:
                json_data = response.json()
                detail = json_data.get("detail", "Unknown error")
                raise WhisperException(detail)
            return response.text
