from faststream import Logger

from app.core.config import settings
from app.main import broker


@broker.subscriber(settings.kafka_topic, group_id="applications_service")
async def handle_new_application(message: dict, logger: Logger):
    logger.info(f"[📥 ПОЛУЧЕНО ИЗ KAFKA] НОВАЯ ЗАЯВКА ПОЛУЧЕНА: {message}")
