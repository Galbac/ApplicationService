import logging

from faststream.kafka import KafkaRouter
from email.message import EmailMessage
from app.core.config import settings
import aiosmtplib

router = KafkaRouter()
logger = logging.getLogger(__name__)


async def send_email(to_email: str, subject: str, body: str):
    message = EmailMessage()
    message["From"] = "test@example.com"
    message["To"] = to_email
    message["Subject"] = subject
    message.set_content(body)

    await aiosmtplib.send(message, hostname="maildev", port=1025)


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

    subject = f"Новая заявка #{message['id']}"
    body = f"""
      Пользователь: {message['user_name']}
      Описание: {message['description']}
      Дата создания: {message['created_at']}
      """
    try:
        await send_email("recipient@example.com", subject, body)
        logger.info(f"Письмо отправлено для заявки {message['id']}")
    except Exception as e:
        logger.error(f"Не удалось отправить письмо для заявки {message['id']}: {e}")
