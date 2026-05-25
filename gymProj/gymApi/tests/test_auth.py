import pytest
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken


@pytest.mark.django_db
def test_token_obtain_returns_access_and_refresh(user, api_client: APIClient):
    response = api_client.post(
        "/api/auth/token/",
        {"username": user.username, "password": "pass12345"},
        format="json",
    )

    assert response.status_code == 200
    assert "access" in response.json()
    assert "refresh" in response.json()


@pytest.mark.django_db
def test_token_refresh_returns_new_access(user, api_client: APIClient):
    refresh = str(RefreshToken.for_user(user))

    response = api_client.post(
        "/api/auth/token/refresh/",
        {"refresh": refresh},
        format="json",
    )

    assert response.status_code == 200
    assert "access" in response.json()
