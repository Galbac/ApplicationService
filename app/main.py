import logging
from contextlib import asynccontextmanager

from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI

from app.api.applications import router as router_applications
from app.di.container import container

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting application...")
    yield
    logger.info("Application shutdown complete")


app = FastAPI(
    title="Application Processing Service",
    description="Service for processing user requests",
    version="1.0.0",
    lifespan=lifespan,
)


app.include_router(router=router_applications)

container = setup_dishka(container, app=app)


@app.get("/")
async def root():
    return {"message": "Application Processing Service"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
