from datetime import datetime

from pydantic import BaseModel, Field


class ApplicationCreate(BaseModel):
    """
    Данные для создания новой заявки.
    """

    user_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Имя пользователя, создавшего заявку. Допускаются буквы, цифры, подчёркивания.",
        example="ivanov_2025",
    )
    description: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="Подробное описание сути заявки. Не более 1000 символов.",
        example="Нужен доступ к базе данных для тестирования нового модуля.",
    )


class ApplicationResponse(BaseModel):
    """
    Ответ с информацией о заявке.
    """

    id: int = Field(..., description="Уникальный идентификатор заявки в системе.")
    user_name: str = Field(..., description="Имя пользователя, создавшего заявку.")
    description: str = Field(..., description="Описание заявки.")
    created_at: datetime = Field(
        ...,
        description="Дата и время создания заявки в формате ISO 8601, отображается как DD-MM-YYYY HH:MM:SS.",
    )

    model_config = {
        "from_attributes": True,
        "json_encoders": {
            datetime: lambda v: v.strftime("%d-%m-%Y %H:%M:%S"),
        },
    }


class ApplicationListResponse(BaseModel):
    """
    Ответ со списком заявок и пагинацией.
    """

    items: list[ApplicationResponse] = Field(
        ...,
        description="Список заявок, соответствующих запросу на текущей странице.",
    )
    total: int = Field(..., description="Общее количество заявок в системе.")
    page: int = Field(..., description="Номер текущей страницы (начинается с 1).")
    size: int = Field(..., description="Количество заявок на одной странице.")
    pages: int = Field(
        ..., description="Общее количество страниц, доступных для просмотра."
    )

    model_config = {"from_attributes": True}


class ApplicationFilter(BaseModel):
    """
    Параметры фильтрации и пагинации для запроса списка заявок.
    """

    user_name: str | None = Field(
        None,
        description="Фильтр по имени пользователя (частичное совпадение). Необязательный параметр.",
        example="ivanov",
    )
    page: int = Field(
        1,
        ge=1,
        description="Номер страницы для пагинации. По умолчанию — 1.",
    )
    size: int = Field(
        10,
        ge=1,
        le=100,
        description="Количество элементов на странице. Максимум — 100.",
    )


class KafkaApplicationMessage(BaseModel):
    """
    Структура сообщения, отправляемого в Kafka при создании заявки.
    """

    id: int = Field(..., description="ID заявки из базы данных.")
    user_name: str = Field(..., description="Имя пользователя, создавшего заявку.")
    description: str = Field(..., description="Описание заявки.")
    created_at: datetime = Field(
        ..., description="Время создания заявки в формате ISO 8601."
    )
