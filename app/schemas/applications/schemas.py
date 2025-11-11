from datetime import datetime

from pydantic import BaseModel, Field


class ApplicationCreate(BaseModel):
    """
    Scheme for creating new projects
    """

    user_name: str = Field(..., min_length=1, max_length=100, description="Username")
    description: str = Field(
        ..., min_length=1, max_length=1000, description="Application Description"
    )


class ApplicationResponse(BaseModel):
    """
    Response scheme for one request
    """

    id: int = Field(..., description="Application ID")
    user_name: str = Field(..., description="Username")
    description: str = Field(..., description="Application Description")
    created_at: datetime = Field(
        ..., description="Date and time of application creation"
    )

    model_config = {"from_attributes": True}


class ApplicationListResponse(BaseModel):
    """
    Response schema for a paginated ticket list
    """

    items: list[ApplicationResponse] = Field(
        ..., description="List of applications on the current page"
    )
    total: int = Field(..., description="Total number of applications")
    page: int = Field(..., description="Current page")
    size: int = Field(..., description="Number of applications per page")
    pages: int = Field(..., description="Total number of pages")

    model_config = {"from_attributes": True}


class ApplicationFilter(BaseModel):
    """
    Application filtering scheme
    """

    user_name: str | None = Field(None, description="Filter by username")
    page: int = Field(1, ge=1, description="Page number")
    size: int = Field(10, ge=1, le=100, description="Number of elements per page")


class KafkaApplicationMessage(BaseModel):
    """
    Схема сообщения для Kafka
    """

    id: int = Field(..., description="Application ID")
    user_name: str = Field(..., description="Username")
    description: str = Field(..., description="Application Description")
    created_at: datetime = Field(
        ..., description="Date and time of application creation"
    )
