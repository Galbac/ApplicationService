import logging
from collections.abc import Sequence

from sqlalchemy import select, func
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

        logger.info(f"Retrieved {len(applications)} applications (total: {total})")

        return applications, total
