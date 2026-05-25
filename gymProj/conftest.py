"""Shared pytest fixtures for the Django project."""

from __future__ import annotations

from collections.abc import Callable

import pytest
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient

from gymApp.models import (
    ClientProfile,
    DifficultyLevel,
    Exercise,
    ExerciseType,
    SubscriptionPlan,
    WorkoutDay,
    WorkoutDayLog,
    WorkoutItem,
    WorkoutItemLog,
    WorkoutPlan,
    WorkoutPlanRun,
    WorkoutSetLog,
)


@pytest.fixture
def api_client() -> APIClient:
    return APIClient()


@pytest.fixture
def user(db) -> User:
    return User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="pass12345",
    )


@pytest.fixture
def subscription_plan(db) -> SubscriptionPlan:
    return SubscriptionPlan.objects.create(
        name="Test Plan",
        price=0,
        features="Test features",
    )


@pytest.fixture
def client_profile(db, user, subscription_plan) -> ClientProfile:
    return ClientProfile.objects.create(user=user, subscription_plan=subscription_plan)


@pytest.fixture
def authenticated_api_client(api_client: APIClient, user: User) -> APIClient:
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def make_workout_set_log(db) -> Callable[[ClientProfile], WorkoutSetLog]:
    """Build a minimal workout log chain for the given client."""

    def _create(client: ClientProfile) -> WorkoutSetLog:
        difficulty = DifficultyLevel.objects.create(name="Easy")
        exercise_type = ExerciseType.objects.create(name="Strength")
        exercise = Exercise.objects.create(
            name="Test exercise",
            description="desc",
            metabolic_equivalent=1.0,
            video=SimpleUploadedFile("v.mp4", b"video"),
            thumbnail=SimpleUploadedFile("t.jpg", b"thumb"),
            difficulty_level=difficulty,
            amount_unit="reps",
            exercise_type=exercise_type,
        )
        plan = WorkoutPlan.objects.create(
            name="Test plan",
            description="desc",
            difficulty_level=difficulty,
        )
        day = WorkoutDay.objects.create(workout_plan=plan, day_number=1)
        item = WorkoutItem.objects.create(
            workout_day=day,
            exercise=exercise,
            amount=10,
            sets=3,
            order=1,
        )
        run = WorkoutPlanRun.objects.create(client=client, workout_plan=plan)
        day_log = WorkoutDayLog.objects.create(workout_plan_run=run, workout_day=day)
        item_log = WorkoutItemLog.objects.create(workout_day_log=day_log, workout_item=item)
        return WorkoutSetLog.objects.create(workout_item_log=item_log, set_number=1)

    return _create
