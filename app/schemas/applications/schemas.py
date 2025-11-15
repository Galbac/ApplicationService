from datetime import datetime

from pydantic import BaseModel, Field


class ApplicationCreate(BaseModel):
    """
    Схема для создания новой заявки
    """

    user_name: str = Field(
        ..., min_length=1, max_length=100, description="Имя пользователя"
    )
    description: str = Field(
        ..., min_length=1, max_length=1000, description="Описание заявки"
    )


class ApplicationResponse(BaseModel):
    """
    Схема ответа для одной заявки
    """

    id: int = Field(..., description="ID заявки")
    user_name: str = Field(..., description="Имя пользователя")
    description: str = Field(..., description="Описание заявки")
    created_at: datetime = Field(..., description="Дата и время создания заявки")

    model_config = {
        "from_attributes": True,
        "json_encoders": {
            datetime: lambda v: v.strftime("%d-%m-%Y %H:%M:%S"),
        },
    }


class ApplicationListResponse(BaseModel):
    """
    Схема ответа для постраничного списка заявок
    """

    items: list[ApplicationResponse] = Field(
        ..., description="Список заявок на текущей странице"
    )
    total: int = Field(..., description="Общее количество заявок")
    page: int = Field(..., description="Текущая страница")
    size: int = Field(..., description="Количество заявок на странице")
    pages: int = Field(..., description="Общее количество страниц")

    model_config = {"from_attributes": True}


class ApplicationFilter(BaseModel):
    """
    Схема фильтрации заявок
    """

    user_name: str | None = Field(None, description="Фильтр по имени пользователя")
    page: int = Field(1, ge=1, description="Номер страницы")
    size: int = Field(10, ge=1, le=100, description="Количество элементов на странице")


class KafkaApplicationMessage(BaseModel):
    """
    Схема сообщения для Kafka
    """

    id: int = Field(..., description="ID заявки")
    user_name: str = Field(..., description="Имя пользователя")
    description: str = Field(..., description="Описание заявки")
    created_at: datetime = Field(..., description="Дата и время создания заявки")
