from typing import Literal
from pydantic import BaseModel


class WhisperServiceResponse(BaseModel):
    response: str
    status: Literal["ok", "error"] = "ok"