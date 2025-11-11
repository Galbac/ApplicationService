import logging
from collections.abc import AsyncIterable

from dishka import Provider, Scope, provide, make_async_container
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncEngine,
    AsyncSession,
)

from app.core.config import settings
from app.database.repository import ApplicationRepository

logger = logging.getLogger(__name__)


class DatabaseProvider(Provider):
    @provide(scope=Scope.APP)
    def engine(self) -> AsyncEngine:
        engine = create_async_engine(
            settings.async_database_url, echo=False, pool_pre_ping=True
        )
        logger.info(f"Database engine created: {engine}")
        return engine

    @provide(scope=Scope.APP)
    def session_maker(self, engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
        session = async_sessionmaker(engine, expire_on_commit=False)
        logger.info(f"Session created: {session}")
        return session

    @provide(scope=Scope.REQUEST)
    async def session(
        self, session_maker: async_sessionmaker[AsyncSession]
    ) -> AsyncIterable[AsyncSession]:
        async with session_maker() as session:
            yield session


class RepositoryProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def provide_application_repo(self, session: AsyncSession) -> ApplicationRepository:
        return ApplicationRepository(session)


container = make_async_container(
    DatabaseProvider(),
    RepositoryProvider(),
)
