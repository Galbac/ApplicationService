import logging

from faststream.kafka import KafkaBroker

from app.schemas.applications.schemas import KafkaApplicationMessage


class KafkaPublisher:
    def __init__(self, broker: KafkaBroker):
        self.broker = broker
        self.logger = logging.getLogger(self.__class__.__name__)

    async def publish(self, topic: str, kafka_message: KafkaApplicationMessage):
        # await self.broker.connect()
        publisher = self.broker.publisher(topic)
        try:
            await publisher.publish(kafka_message.model_dump(mode="json"))
            self.logger.info(
                f"ОПУБЛИКОВАНО СООБЩЕНИЕ ID={kafka_message.id} В ТЕМУ KAFKA '{topic}'"
            )
        except Exception as e:
            self.logger.error(
                f"НЕ УДАЛОСЬ ОПУБЛИКОВАТЬ СООБЩЕНИЕ ID={kafka_message.id} В ТЕМУ '{topic}': {e}"
            )
            raise
