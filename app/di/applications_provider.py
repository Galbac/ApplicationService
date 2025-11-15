from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from app.database.repository import ApplicationRepository


class RepositoryProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def provide_application_repo(self, session: AsyncSession) -> ApplicationRepository:
        return ApplicationRepository(session)
