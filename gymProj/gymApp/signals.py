def grant_group_perms(sender, **kwargs):
    from django.contrib.auth.models import Group, Permission
    from .models import (
        Exercise,
        WorkoutPlan,
        WorkoutItem,
        SubscriptionPlan,
        ClientProfile,
        WorkoutDay,
        Gym,
        BugReport,
        NewFeatureRequest,
    )

    permNameToModel = {
        "Exercise Managers": Exercise,
        "Workout Managers": [WorkoutPlan, WorkoutItem, WorkoutDay],
        "Subscription Managers": SubscriptionPlan,
        "Client Managers": ClientProfile,
        "Gym Managers": Gym,
        "Support Team": [BugReport, NewFeatureRequest],
    }

    for group_name, model in permNameToModel.items():
        group, _ = Group.objects.get_or_create(name=group_name)
        if isinstance(model, list):
            perms = Permission.objects.filter(
                content_type__app_label="gymApp",
                content_type__model__in=[m._meta.model_name for m in model],
            )
        else:
            perms = Permission.objects.filter(
                content_type__app_label="gymApp",
                content_type__model=model._meta.model_name,
            )
        group.permissions.add(*perms)
