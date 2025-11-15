import logging

from faststream.kafka import KafkaRouter

from app.core.config import settings

router = KafkaRouter()
logger = logging.getLogger(__name__)


@router.subscriber(settings.kafka_topic, group_id="new_application_subscribers")
async def handle_new_application(message: dict):
    """
    Обработчик события получения новой заявки из Kafka.

    Parameters
    ----------
    message : dict
        Словарь с данными новой заявки. Ожидаемая структура:
        {
            "id": int,               # уникальный идентификатор заявки
            "user_name": str,        # имя пользователя, создавшего заявку
            "description": str,      # описание заявки
            "created_at": str        # дата и время создания заявки в ISO формате
        }
    """
    logger.info(f"[📥 ПОЛУЧЕНО ИЗ KAFKA] НОВАЯ ЗАЯВКА ПОЛУЧЕНА: {message}")
