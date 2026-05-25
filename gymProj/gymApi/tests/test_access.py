import pytest
from django.contrib.auth.models import User
from django.http import Http404

from gymApi.access import (
    get_workout_day_log_for_user,
    get_workout_item_log_for_user,
    get_workout_set_log_for_user,
)
from gymApp.models import (
    ClientProfile,
    SubscriptionPlan,
    WorkoutDayLog,
)


@pytest.mark.django_db
def test_get_workout_set_log_for_user_returns_own_log(user, client_profile, make_workout_set_log):
    set_log = make_workout_set_log(client_profile)
    result = get_workout_set_log_for_user(user, set_log.pk)
    assert result.pk == set_log.pk


@pytest.mark.django_db
def test_get_workout_set_log_for_user_raises_404_for_other_client(make_workout_set_log):
    plan = SubscriptionPlan.objects.create(name="Plan", price=0, features="x")
    user_a = User.objects.create_user(username="user_a", password="pass12345")
    user_b = User.objects.create_user(username="user_b", password="pass12345")
    ClientProfile.objects.create(user=user_a, subscription_plan=plan)
    profile_b = ClientProfile.objects.create(user=user_b, subscription_plan=plan)

    set_log_b = make_workout_set_log(profile_b)

    with pytest.raises(Http404):
        get_workout_set_log_for_user(user_a, set_log_b.pk)


@pytest.mark.django_db
def test_get_workout_item_log_for_user_returns_own_log(user, client_profile, make_workout_set_log):
    set_log = make_workout_set_log(client_profile)
    item_log = set_log.workout_item_log

    result = get_workout_item_log_for_user(user, item_log.pk)
    assert result.pk == item_log.pk


@pytest.mark.django_db
def test_get_workout_day_log_for_user_returns_own_log(user, client_profile, make_workout_set_log):
    set_log = make_workout_set_log(client_profile)
    day_log = set_log.workout_item_log.workout_day_log

    result = get_workout_day_log_for_user(user, day_log.pk)
    assert result.pk == day_log.pk


@pytest.mark.django_db
def test_get_workout_day_log_for_user_raises_404_for_other_client(make_workout_set_log):
    plan = SubscriptionPlan.objects.create(name="Plan", price=0, features="x")
    user_a = User.objects.create_user(username="user_a2", password="pass12345")
    user_b = User.objects.create_user(username="user_b2", password="pass12345")
    ClientProfile.objects.create(user=user_a, subscription_plan=plan)
    profile_b = ClientProfile.objects.create(user=user_b, subscription_plan=plan)

    set_log_b = make_workout_set_log(profile_b)
    day_log_b: WorkoutDayLog = set_log_b.workout_item_log.workout_day_log

    with pytest.raises(Http404):
        get_workout_day_log_for_user(user_a, day_log_b.pk)
