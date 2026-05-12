import datetime
import json
import secrets
import ssl
from enum import Enum
from typing import Any, AsyncGenerator, Optional

import httpx
from aiogram.client.session.base import BaseSession
from aiogram.methods import TelegramMethod
from aiogram.types import TelegramObject, InputFile
from aiogram.client.default import Default
from aiogram.exceptions import TelegramNetworkError


class HttpxSession(BaseSession):
    def __init__(self, proxy: Optional[str] = None, **kwargs):
        super().__init__(**kwargs)
        self.proxy = proxy
        self._client: Optional[httpx.AsyncClient] = None

    async def create_client(self) -> httpx.AsyncClient:
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        if self.proxy:
            return httpx.AsyncClient(
                proxies=self.proxy, 
                timeout=60.0, 
                verify=ssl_context
            )
        return httpx.AsyncClient(
            timeout=60.0, 
            verify=ssl_context
        )

    async def close(self):
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    def prepare_value(
        self,
        value: Any,
        bot,
        files: dict[str, Any],
        _dumps_json: bool = True,
    ) -> Any:
        """
        Prepare value before send (copied from AiohttpSession)
        """
        if value is None:
            return None
        if isinstance(value, str):
            return value
        if isinstance(value, Default):
            default_value = bot.default[value.name]
            return self.prepare_value(default_value, bot=bot, files=files, _dumps_json=_dumps_json)
        if isinstance(value, InputFile):
            key = secrets.token_urlsafe(10)
            files[key] = value
            return f"attach://{key}"
        if isinstance(value, dict):
            value = {
                key: prepared_item
                for key, item in value.items()
                if (
                    prepared_item := self.prepare_value(
                        item,
                        bot=bot,
                        files=files,
                        _dumps_json=False,
                    )
                )
                is not None
            }
            if _dumps_json:
                return json.dumps(value)
            return value
        if isinstance(value, list):
            value = [
                prepared_item
                for item in value
                if (
                    prepared_item := self.prepare_value(
                        item,
                        bot=bot,
                        files=files,
                        _dumps_json=False,
                    )
                )
                is not None
            ]
            if _dumps_json:
                return json.dumps(value)
            return value
        if isinstance(value, datetime.timedelta):
            now = datetime.datetime.now()
            return str(round((now + value).timestamp()))
        if isinstance(value, datetime.datetime):
            return str(round(value.timestamp()))
        if isinstance(value, Enum):
            return self.prepare_value(value.value, bot=bot, files=files)
        if isinstance(value, TelegramObject):
            return self.prepare_value(
                value.model_dump(warnings=False),
                bot=bot,
                files=files,
                _dumps_json=_dumps_json,
            )
        if _dumps_json:
            return json.dumps(value)
        return value

    def build_request_data(self, bot, method: TelegramMethod[TelegramObject]) -> tuple[dict, dict]:
        """
        Build request data and files
        """
        data = {}
        files = {}
        for key, value in method.model_dump(warnings=False).items():
            value = self.prepare_value(value, bot=bot, files=files)
            if value is not None:
                data[key] = value
        return data, files

    async def make_request(
        self,
        bot,
        method: TelegramMethod[TelegramObject],
        timeout: Optional[int] = None,
    ) -> TelegramObject:
        if self._client is None:
            self._client = await self.create_client()

        url = self.api.api_url(bot.token, method.__api_method__)
        request_timeout = timeout or 60
        
        try:
            data, files = self.build_request_data(bot, method)
            
            if files:
                # Multipart request for file uploads
                files_data = {}
                for key, value in files.items():
                    files_data[key] = (key, await value.read(bot), value.filename or key)
                
                response = await self._client.post(
                    url=url,
                    data=data,
                    files=files_data,
                    timeout=request_timeout,
                )
            else:
                # JSON request for simple methods
                response = await self._client.post(
                    url=url,
                    json=data,
                    timeout=request_timeout,
                )
            
            response_data = response.json()
            
            if not response_data.get("ok"):
                raise TelegramNetworkError(
                    method=method.__api_method__,
                    message=f"Telegram API error: {response_data}"
                )
            
            result = response_data.get("result")
            
            # Deserialize response
            if isinstance(result, list):
                return_type = method.__returning__
                if hasattr(return_type, '__origin__') and return_type.__origin__ is list:
                    item_type = return_type.__args__[0]
                    return [item_type(**item) if isinstance(item, dict) else item for item in result]
                else:
                    return result
            elif isinstance(result, dict):
                return method.__returning__(**result)
            else:
                return result
                
        except httpx.TimeoutException as e:
            raise TelegramNetworkError(
                method=method.__api_method__,
                message="Request timeout error"
            ) from e
        except TelegramNetworkError:
            raise
        except Exception as e:
            raise TelegramNetworkError(
                method=method.__api_method__,
                message=f"HTTP Client says - {str(e)}"
            ) from e

    async def stream_content(
        self,
        url: str,
        timeout: int,
        chunk_size: int,
        raise_for_status: bool,
    ) -> AsyncGenerator[bytes, None]:
        if self._client is None:
            self._client = await self.create_client()
        
        async with self._client.stream("GET", url, timeout=timeout) as response:
            if raise_for_status:
                response.raise_for_status()
            async for chunk in response.aiter_bytes(chunk_size):
                yield chunk
