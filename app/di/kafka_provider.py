import logging

from dishka import Provider, provide, Scope
from faststream.kafka import KafkaBroker

from app.core.config import settings
from app.kafka.applications.publisher import KafkaPublisher

logger = logging.getLogger(__name__)


class KafkaProvider(Provider):
    @provide(scope=Scope.APP)
    async def get_kafka_broker(self) -> KafkaBroker:
        if not settings.kafka_bootstrap_servers:
            logger.warning("СЕРВЕРЫ KAFKA BOOTSTRAP НЕ НАСТРОЕНЫ")
            raise ValueError("СЕРВЕРЫ KAFKA BOOTSTRAP НЕ НАСТРОЕНЫ")
        broker = KafkaBroker(settings.kafka_bootstrap_servers)
        logger.info(f"КАФКА БУСТРАП СЕРВЕР = {settings.kafka_bootstrap_servers}")
        return broker


class KafkaPublisherProvider(Provider):
    @provide(scope=Scope.APP)
    def provide_kafka_publisher(self, broker: KafkaBroker) -> KafkaPublisher:
        logger.info("КАФКА ПУБЛИЩЕР ПРОВАЙДЕР")
        return KafkaPublisher(broker)
