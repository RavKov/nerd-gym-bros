import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient

from gymApp.models import ClientProfile, SubscriptionPlan


@pytest.mark.django_db
def test_exercise_list_returns_paginated_empty_results_without_subscription_plan(
    api_client: APIClient,
):
    user = User.objects.create_user(username="user_no_plan", password="pass12345")
    ClientProfile.objects.create(user=user)

    api_client.force_authenticate(user=user)
    response = api_client.get("/api/exercises/")

    payload = response.json()

    assert response.status_code == 200
    assert payload["count"] == 0
    assert payload["results"] == []


@pytest.mark.django_db
def test_exercise_list_returns_exercises_for_subscription_plan(
    api_client: APIClient, make_subscription_exercise
):
    plan_a = SubscriptionPlan.objects.create(name="Plan A", price=0, features="A")
    exercise = make_subscription_exercise(plan_a)

    user_a = User.objects.create_user(username="user_a", password="pass12345")
    ClientProfile.objects.create(user=user_a, subscription_plan=plan_a)

    api_client.force_authenticate(user=user_a)
    response = api_client.get("/api/exercises/")

    payload = response.json()

    assert response.status_code == 200
    assert payload["count"] == 1
    assert [item["id"] for item in payload["results"]] == [exercise.pk]


@pytest.mark.django_db
def test_exercise_detail_returns_404_for_exercise_outside_subscription_plan(
    api_client: APIClient, make_subscription_exercise
):
    plan_a = SubscriptionPlan.objects.create(name="Plan A", price=0, features="A")
    plan_b = SubscriptionPlan.objects.create(name="Plan B", price=0, features="B")
    exercise = make_subscription_exercise(plan_b)

    user_a = User.objects.create_user(username="user_detail", password="pass12345")
    ClientProfile.objects.create(user=user_a, subscription_plan=plan_a)

    api_client.force_authenticate(user=user_a)
    response = api_client.get(f"/api/exercises/{exercise.pk}/")

    assert response.status_code == 404
