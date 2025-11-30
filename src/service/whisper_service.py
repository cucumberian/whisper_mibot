import httpx


class WhisperAPI:
    def __init__(self, transcribe_url: str):
        self.transcribe_url = transcribe_url

    async def transcribe(self, audio: bytes, timeout: int = 300) -> str | None:
        """Отправляет запрос на перевод внешнему апи"""
        url = f"{self.transcribe_url}"
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url=url, files={"audio": audio}, timeout=timeout
            )

            if response.status_code != 200:
                return None
            return response.text
