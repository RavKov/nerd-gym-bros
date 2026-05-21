"""
Helpers to fetch workout log resources scoped to the authenticated client.
"""

from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

from gymApp.models import ClientProfile, WorkoutDayLog, WorkoutItemLog, WorkoutSetLog


def get_client_profile(user: User) -> ClientProfile:
    return get_object_or_404(ClientProfile, user=user)


def get_workout_day_log_for_user(user: User, pk: int) -> WorkoutDayLog:
    client = get_client_profile(user)
    return get_object_or_404(
        WorkoutDayLog.objects.filter(workout_plan_run__client=client),
        pk=pk,
    )


def get_workout_item_log_for_user(user: User, pk: int) -> WorkoutItemLog:
    client = get_client_profile(user)
    return get_object_or_404(
        WorkoutItemLog.objects.filter(
            workout_day_log__workout_plan_run__client=client
        ),
        pk=pk,
    )


def get_workout_set_log_for_user(user: User, pk: int) -> WorkoutSetLog:
    client = get_client_profile(user)
    return get_object_or_404(
        WorkoutSetLog.objects.filter(
            workout_item_log__workout_day_log__workout_plan_run__client=client
        ),
        pk=pk,
    )
