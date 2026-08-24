from typing import Any, Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ErrorResponse(BaseModel):
    success: bool = False
    message: str
    detail: Any | None = None


class APIResponse(BaseModel, Generic[T]):
    success: bool = True
    message: str
    data: T | None = None
