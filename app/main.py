import asyncio
import logging
from contextlib import asynccontextmanager

from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
from faststream import FastStream
from faststream.kafka import KafkaBroker

from app.api.applications import router as router_applications
from app.core.config import settings
from app.di.container import container

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

logger = logging.getLogger(__name__)

broker = KafkaBroker(settings.kafka_bootstrap_servers)
stream = FastStream(broker)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("ЗАПУСК ПРИЛОЖЕНИЯ...")
    await broker.connect()
    task = asyncio.create_task(stream.run())
    await asyncio.sleep(10)
    logger.info("ЗАПУСК FASTSTREAM KAFKA БРОКЕРА...")
    yield
    task.cancel()
    await broker.stop()


app = FastAPI(
    title="СЕРВИС ОБРАБОТКИ ЗАЯВОК",
    description="СЕРВИС ДЛЯ ОБРАБОТКИ ЗАПРОСОВ ПОЛЬЗОВАТЕЛЕЙ",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(router=router_applications)

setup_dishka(container, app=app)


@app.get("/")
async def root():
    return {"message": "СЕРВИС ОБРАБОТКИ ЗАЯВОК"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
