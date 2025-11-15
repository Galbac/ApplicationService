import logging

from faststream import FastStream

from app.kafka.applications.fs_broker import broker
from app.kafka.applications.fs_subs.consumers import router as app_router

app = FastStream(broker)

broker.include_router(app_router)


@app.after_startup
async def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )
