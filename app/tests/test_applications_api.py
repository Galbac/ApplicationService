from datetime import datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import status
from httpx import AsyncClient, ASGITransport

from app.main import app


@pytest.mark.asyncio
async def test_get_applications_success():
    mock_applications = [
        {
            "id": 1,
            "user_name": "ivanov",
            "description": "Test description",
            "created_at": datetime(2025, 11, 17, 10, 30, 0),
        }
    ]
    total = 1

    with patch(
        "app.database.repository.ApplicationRepository.get_applications",
        new_callable=AsyncMock,
    ) as mock_get:
        mock_get.return_value = (mock_applications, total)

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as ac:
            response = await ac.get("/applications/?page=1&size=10")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == total
        assert data["page"] == 1
        assert data["size"] == 10
        assert data["items"][0]["user_name"] == "ivanov"


@pytest.mark.asyncio
async def test_get_applications_error():
    with patch(
        "app.database.repository.ApplicationRepository.get_applications",
        new_callable=AsyncMock,
    ) as mock_get:
        mock_get.side_effect = Exception("DB error")

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as ac:
            response = await ac.get("/applications/")

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "ОШИБКА ПРИ ПОЛУЧЕНИИ ЗАЯВОК" in response.json()["detail"]


@pytest.mark.asyncio
async def test_create_application_success():
    new_app = SimpleNamespace(
        id=2,
        user_name="petrov",
        description="Нужен доступ к базе данных",
        created_at=datetime(2025, 11, 17, 12, 0, 0),
    )

    with patch(
        "app.database.repository.ApplicationRepository.create_application",
        new_callable=AsyncMock,
    ) as mock_create, patch(
        "app.kafka.applications.publisher.KafkaPublisher.publish",
        new_callable=AsyncMock,
    ) as mock_publish:
        mock_create.return_value = new_app
        mock_publish.return_value = None

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as ac:
            response = await ac.post(
                "/applications/",
                json={
                    "user_name": "petrov",
                    "description": "Нужен доступ к базе данных",
                },
            )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["user_name"] == "petrov"
        assert data["description"] == "Нужен доступ к базе данных"


@pytest.mark.asyncio
async def test_create_application_kafka_failure():
    from types import SimpleNamespace
    from datetime import datetime

    new_app = SimpleNamespace(
        id=3,
        user_name="sidorov",
        description="Тестовая заявка",
        created_at=datetime(2025, 11, 17, 12, 0, 0),
    )

    with patch(
        "app.database.repository.ApplicationRepository.create_application",
        new_callable=AsyncMock,
    ) as mock_create, patch(
        "app.kafka.applications.publisher.KafkaPublisher.publish",
        new_callable=AsyncMock,
    ) as mock_publish:
        mock_create.return_value = new_app
        mock_publish.side_effect = Exception("Kafka error")

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as ac:
            response = await ac.post(
                "/applications/",
                json={"user_name": "sidorov", "description": "Тестовая заявка"},
            )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["user_name"] == "sidorov"
        assert data["description"] == "Тестовая заявка"
