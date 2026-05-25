import pytest
from rest_framework.test import APIClient

from gymApp.models import WorkoutItem


@pytest.mark.django_db
def test_workout_day_log_patch_marks_day_completed(
    authenticated_api_client: APIClient, client_profile, make_workout_set_log
):
    set_log = make_workout_set_log(client_profile)
    day_log = set_log.workout_item_log.workout_day_log

    response = authenticated_api_client.patch(
        f"/api/me/workout_day_log/{day_log.pk}/",
        {"completed": True},
        format="json",
    )

    day_log.refresh_from_db()

    assert response.status_code == 200
    assert day_log.completed is True


@pytest.mark.django_db
def test_workout_item_log_patch_marks_item_completed(
    authenticated_api_client: APIClient, client_profile, make_workout_set_log
):
    set_log = make_workout_set_log(client_profile)
    item_log = set_log.workout_item_log

    response = authenticated_api_client.patch(
        f"/api/me/workout_item_log/{item_log.pk}/",
        {"completed": True},
        format="json",
    )

    item_log.refresh_from_db()

    assert response.status_code == 200
    assert item_log.completed is True


@pytest.mark.django_db
def test_workout_set_log_patch_updates_actual_amount(
    authenticated_api_client: APIClient, client_profile, make_workout_set_log
):
    set_log = make_workout_set_log(client_profile)

    response = authenticated_api_client.patch(
        f"/api/me/set_log/{set_log.pk}/",
        {"actual_amount": 12},
        format="json",
    )

    set_log.refresh_from_db()

    assert response.status_code == 200
    assert set_log.actual_amount == 12


@pytest.mark.django_db
def test_workout_plan_run_patch_finishes_active_run(
    authenticated_api_client: APIClient, client_profile, make_workout_set_log
):
    set_log = make_workout_set_log(client_profile)
    run = set_log.workout_item_log.workout_day_log.workout_plan_run
    client_profile.active_workout_plan = run.workout_plan
    client_profile.save(update_fields=["active_workout_plan"])

    response = authenticated_api_client.patch(
        "/api/me/workout_plan_run/",
        {"is_active": False},
        format="json",
    )

    run.refresh_from_db()
    client_profile.refresh_from_db()

    assert response.status_code == 200
    assert run.is_active is False
    assert run.finished_at is not None
    assert client_profile.active_workout_plan is None


@pytest.mark.django_db
def test_workout_plan_list_returns_paginated_results(
    authenticated_api_client: APIClient, client_profile, make_subscription_exercise
):
    exercise = make_subscription_exercise(client_profile.subscription_plan)
    workout_plan = WorkoutItem.objects.get(exercise=exercise).workout_day.workout_plan

    response = authenticated_api_client.get("/api/workout_plans/")

    payload = response.json()

    assert response.status_code == 200
    assert payload["count"] == 1
    assert [item["id"] for item in payload["results"]] == [workout_plan.pk]


@pytest.mark.django_db
def test_workout_plan_run_get_returns_404_without_active_run(
    authenticated_api_client: APIClient,
):
    response = authenticated_api_client.get("/api/me/workout_plan_run/")

    assert response.status_code == 404
    assert response.json() == {"detail": "No active workout plan run."}


@pytest.mark.django_db
def test_workout_set_log_patch_returns_detail_for_invalid_payload(
    authenticated_api_client: APIClient, client_profile, make_workout_set_log
):
    set_log = make_workout_set_log(client_profile)

    response = authenticated_api_client.patch(
        f"/api/me/set_log/{set_log.pk}/",
        {},
        format="json",
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid data."}
