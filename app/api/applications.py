import logging
from math import ceil

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, Query, status, HTTPException

from app.database.repository import ApplicationRepository
from app.schemas.applications.schemas import (
    ApplicationListResponse,
    ApplicationFilter,
    ApplicationResponse,
    ApplicationCreate,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/applications", tags=["applications"])


@router.get("/", response_model=ApplicationListResponse, summary="Get all applications")
@inject
async def get_applications(
    app_repo: FromDishka[ApplicationRepository],
    user_name: str = Query(None, description="Filter by user name"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Page size"),
):
    filters = ApplicationFilter(user_name=user_name, page=page, size=size)
    try:
        applications, total = await app_repo.get_applications(filters)
    except Exception:
        logger.exception("Ошибка при получении заявок")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при получении заявок",
        )

    pages = ceil(total / size)
    items = [ApplicationResponse.model_validate(app) for app in applications]
    logger.info(f"Retrieved {len(items)} applications (total={total}, page={page})")

    return ApplicationListResponse(
        items=items, total=total, pages=pages, size=size, page=page
    )


@router.post(
    "/",
    response_model=ApplicationResponse,
    status_code=201,
    summary="Create new application",
)
@inject
async def create_application(
    application: ApplicationCreate,
    app_repo: FromDishka[ApplicationRepository],
):
    new_application = await app_repo.create_application(
        user_name=application.user_name, description=application.description
    )
    return ApplicationResponse.model_validate(new_application)
