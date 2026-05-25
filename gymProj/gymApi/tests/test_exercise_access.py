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
)


@pytest.mark.django_db
def test_exercise_detail_returns_404_for_exercise_outside_subscription_plan(
    api_client: APIClient,
):
    plan_a = SubscriptionPlan.objects.create(name="Plan A", price=0, features="A")

    user_a = User.objects.create_user(username="user_a", password="pass12345")
    ClientProfile.objects.create(user=user_a, subscription_plan=plan_a)

    difficulty = DifficultyLevel.objects.create(name="Easy")
    exercise_type = ExerciseType.objects.create(name="Strength")
    exercise = Exercise.objects.create(
        name="Other plan exercise",
        description="desc",
        metabolic_equivalent=1.0,
        video=SimpleUploadedFile("v.mp4", b"video"),
        thumbnail=SimpleUploadedFile("t.jpg", b"thumb"),
        difficulty_level=difficulty,
        amount_unit="reps",
        exercise_type=exercise_type,
    )

    api_client.force_authenticate(user=user_a)
    response = api_client.get(f"/api/exercises/{exercise.pk}/")

    assert response.status_code == 404
