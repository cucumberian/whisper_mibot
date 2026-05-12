import httpx


class STTException(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class STTAPI:
    def __init__(self, api_url: str):
        self.api_url = api_url.rstrip("/")

    async def transcribe(self, audio: bytes, filename: str = "audio.ogg", timeout: int = 300) -> str:
        """Отправляет аудио на распознавание во внешнее API"""
        url = f"{self.api_url}/audio/transcriptions"
        
        files = {"file": (filename, audio, "application/octet-stream")}
        data = {"model": "gigaam-v3", "response_format": "json"}
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url=url, files=files, data=data, timeout=timeout
            )
            if not response.is_success:
                try:
                    json_data = response.json()
                    detail = json_data.get("detail", "Unknown error")
                    if isinstance(detail, list):
                        detail = "; ".join([str(d) for d in detail])
                except Exception:
                    detail = response.text or "Unknown error"
                raise STTException(detail)
            
            try:
                result = response.json()
                if isinstance(result, dict):
                    return result.get("text", str(result))
                return str(result)
            except Exception:
                return response.text
