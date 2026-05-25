from unittest.mock import patch

import pytest
from rest_framework.test import APIClient


@pytest.mark.django_db
@patch("gymApi.views._send_verification_email")
def test_register_creates_user_and_sends_verification(mock_send_email, api_client: APIClient):
    response = api_client.post(
        "/api/register/",
        {
            "username": "newclient",
            "email": "newclient@example.com",
            "password": "securepass123",
            "first_name": "New",
            "last_name": "Client",
        },
        format="json",
    )

    assert response.status_code == 201
    assert response.json()["email"] == "newclient@example.com"
    mock_send_email.assert_called_once()
