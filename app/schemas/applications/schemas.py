from datetime import datetime

from pydantic import BaseModel


class ApplicationCreate(BaseModel):
    user_name: str
    description: str


class ApplicationResponse(BaseModel):
    id: int
    user_name: str
    description: str
    created_at: datetime

    class Config:
        from_attributes = True


class ApplicationListResponse(BaseModel):
    items: list[ApplicationResponse]
    total: int
    page: int
    size: int
    pages: int


class KafkaApplicationMessage(BaseModel):
    id: int
    user_name: str
    description: str
    created_at: datetime
