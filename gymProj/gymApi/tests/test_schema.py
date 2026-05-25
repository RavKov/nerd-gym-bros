from rest_framework.test import APIClient


def test_openapi_schema_endpoint_is_available_in_debug(api_client: APIClient):
    response = api_client.get("/api/schema/?format=json")

    assert response.status_code == 200
    assert response.json()["openapi"].startswith("3.")
