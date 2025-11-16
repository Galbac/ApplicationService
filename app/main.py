import logging
from contextlib import asynccontextmanager

from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI

from app.api.applications import router as router_applications
from app.di.container import container
from app.kafka.applications.fs_broker import broker

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("ЗАПУСК ПРИЛОЖЕНИЯ...")
    await broker.start()
    logger.info("ЗАПУСК FASTSTREAM KAFKA БРОКЕРА...")
    yield
    await broker.stop()
    logger.info("ВЫХОД FASTSTREAM KAFKA БРОКЕРА...")


app = FastAPI(
    title="СЕРВИС ОБРАБОТКИ ЗАЯВОК",
    description="СЕРВИС ДЛЯ ОБРАБОТКИ ЗАПРОСОВ ПОЛЬЗОВАТЕЛЕЙ",
    version="1.0.0",
    lifespan=lifespan,
    openapi_tags=[
        {
            "name": "Заявки",
            "description": "Операции, связанные с заявками пользователей: создание, получение списка.",
        }
    ],
)

app.include_router(router=router_applications)

setup_dishka(container, app=app)


@app.get("/")
async def root():
    return {"message": "СЕРВИС ОБРАБОТКИ ЗАЯВОК"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
