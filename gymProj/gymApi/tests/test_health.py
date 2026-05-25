from unittest.mock import patch

import pytest
from django.db import connection
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_health_check_returns_ok(api_client: APIClient):
    response = api_client.get("/api/health/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["database"] == "ok"


@pytest.mark.django_db
def test_health_check_returns_degraded_when_db_unavailable(api_client: APIClient):
    with patch.object(connection, "ensure_connection", side_effect=Exception("db down")):
        response = api_client.get("/api/health/")

    assert response.status_code == 503
    assert response.json()["status"] == "degraded"
    assert response.json()["database"] == "unavailable"
