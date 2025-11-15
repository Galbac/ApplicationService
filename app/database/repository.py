import logging
from collections.abc import Sequence

from sqlalchemy import select, func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.applications.models import Application
from app.schemas.applications.schemas import ApplicationFilter

logger = logging.getLogger(__name__)


class ApplicationRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_applications(
        self, filters: ApplicationFilter
    ) -> tuple[Sequence[Application], int]:
        conditions = []

        if filters.user_name:
            conditions.append(Application.user_name.ilike(f"%{filters.user_name}%"))

        count_query = select(func.count()).select_from(Application).filter(*conditions)
        total = (await self.session.execute(count_query)).scalar()

        offset = (filters.page - 1) * filters.size
        query = (
            select(Application)
            .filter(*conditions)
            .order_by(Application.created_at.desc())
            .offset(offset)
            .limit(filters.size)
        )

        result = await self.session.execute(query)
        applications = result.scalars().all()

        logger.info(f"ПОЛУЧЕНО {len(applications)} ЗАЯВОК (ВСЕГО: {total})")

        return applications, total

    async def create_application(self, user_name: str, description: str) -> Application:
        try:
            async with self.session.begin():
                application = Application(user_name=user_name, description=description)
                self.session.add(application)
                await self.session.flush()
                await self.session.refresh(application)
            logger.info(f"ЗАЯВКА СОЗДАНА С ID: {application.id}")
            return application

        except SQLAlchemyError:
            logger.exception("ОШИБКА БАЗЫ ДАННЫХ ПРИ СОЗДАНИИ ЗАЯВКИ")
            raise
        except Exception:
            logger.exception("НЕОЖИДАННАЯ ОШИБКА ПРИ СОЗДАНИИ ЗАЯВКИ")
            raise
