from pydantic import BaseModel, HttpUrl


class ErrorResponse(BaseModel):
    type: HttpUrl
    title: str
    status: int
    detail: str
    instance: HttpUrl


class PaginationParams(BaseModel):
    cursor: str | None = None
    limit: int = 20


class MessageResponse(BaseModel):
    message: str
