import logging

from dishka import Provider, provide, Scope

from app.kafka.applications.fs_broker import broker
from app.kafka.applications.publisher import KafkaPublisher

logger = logging.getLogger(__name__)


class KafkaPublisherProvider(Provider):
    @provide(scope=Scope.APP)
    def provide_kafka_publisher(self) -> KafkaPublisher:
        logger.info("КАФКА ПУБЛИЩЕР ПРОВАЙДЕР")
        return KafkaPublisher(broker)
