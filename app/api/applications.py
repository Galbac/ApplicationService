import logging
from math import ceil

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, Query, status, HTTPException

from app.core.config import settings
from app.database.repository import ApplicationRepository
from app.kafka.applications.publisher import KafkaPublisher
from app.schemas.applications.schemas import (
    ApplicationListResponse,
    ApplicationFilter,
    ApplicationResponse,
    ApplicationCreate,
    KafkaApplicationMessage,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/applications", tags=["applications"])


@router.get(
    "/",
    response_model=ApplicationListResponse,
    summary="ПОЛУЧИТЬ ВСЕ ЗАЯВКИ",
    description="""
                Возвращает список заявок с возможностью фильтрации по имени пользователя и пагинации.

                **Особенности:**
                - Поддерживает фильтрацию по `user_name`
                - Пагинация: `page` и `size` (максимум 100 записей на страницу)
                - Возвращает общее количество заявок, число страниц и текущую страницу

                **Пример ответа:**
                ```json
                {
                  "items": [
                    {
                      "id": 1,
                      "user_name": "ivanov",
                      "description": "Нужен доступ к тестовому окружению",
                      "created_at": "17-11-2025 10:30:00"
                    }
                  ],
                  "total": 42,
                  "page": 1,
                  "size": 10,
                  "pages": 5
                }
                ```
                """,
)
@inject
async def get_applications(
    app_repo: FromDishka[ApplicationRepository],
    user_name: str | None = Query(
        None,
        min_length=1,
        max_length=100,
        description="Фильтр по имени пользователя (частичное совпадение)",
        example="ivanov",
    ),
    page: int = Query(
        1,
        ge=1,
        description="Номер страницы (начинается с 1)",
        example=1,
    ),
    size: int = Query(
        10,
        ge=1,
        le=100,
        description="Количество записей на странице (максимум 100)",
        example=10,
    ),
):
    filters = ApplicationFilter(user_name=user_name, page=page, size=size)
    try:
        applications, total = await app_repo.get_applications(filters)
    except Exception:
        logger.exception("ОШИБКА ПРИ ПОЛУЧЕНИИ ЗАЯВОК")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="ОШИБКА ПРИ ПОЛУЧЕНИИ ЗАЯВОК",
        )

    pages = ceil(total / size)
    items = [ApplicationResponse.model_validate(app) for app in applications]
    logger.info(f"ПОЛУЧЕНО {len(items)} ЗАЯВОК (ВСЕГО={total}, СТРАНИЦА={page})")

    return ApplicationListResponse(
        items=items, total=total, pages=pages, size=size, page=page
    )


@router.post(
    "/",
    response_model=ApplicationResponse,
    status_code=201,
    summary="СОЗДАТЬ НОВУЮ ЗАЯВКУ",
    description="""
    Создаёт новую заявку и асинхронно публикует её в Kafka для дальнейшей обработки.

    **Важно:**
    - После успешного создания заявка отправляется в топик Kafka для аудита или внешней обработки
    - В случае ошибки публикации в Kafka — заявка всё равно сохраняется в БД, но в логах будет предупреждение

    **Пример запроса:**
    ```json
    {
      "user_name": "petrov",
      "description": "Нужен доступ к базе данных"
    }
    ```
    """,
)
@inject
async def create_application(
    application: ApplicationCreate,
    app_repo: FromDishka[ApplicationRepository],
    kafka_publisher: FromDishka[KafkaPublisher],
):
    new_application = await app_repo.create_application(
        user_name=application.user_name, description=application.description
    )

    kafka_message = KafkaApplicationMessage(
        id=new_application.id,
        user_name=new_application.user_name,
        description=new_application.description,
        created_at=new_application.created_at,
    )
    try:
        await kafka_publisher.publish(
            topic=settings.kafka_topic, kafka_message=kafka_message
        )
        logger.info(f"ЗАЯВКА {new_application.id} ОПУБЛИКОВАНА В KAFKA")
    except Exception as e:
        logger.error(
            f"НЕ УДАЛОСЬ ОПУБЛИКОВАТЬ ЗАЯВКУ {new_application.id} В KAFKA: {e}"
        )

    return ApplicationResponse.model_validate(new_application)
