from django.contrib import admin

from .models import (
    DifficultyLevel,
    Equipment,
    Exercise,
    ExerciseType,
    WorkoutItem,
    WorkoutPlan,
    WorkoutDay,
    SubscriptionPlan,
    MobileTextContent,
    Gym,
    GymReview,
    Address,
    BugReport,
    NewFeatureRequest,
    ClientProfile,
    EmailVerificationCode,
    Subscription,
    SubscriptionPayment,
    WorkoutPlanRun,
    WorkoutDayLog,
    WorkoutItemLog,
    WorkoutSetLog,
)

# Customize admin site
admin.site.site_header = "Nerd Gym Bros Superuser"
admin.site.site_title = "Nerd Gym Bros"
admin.site.index_title = "Welcome to Superuser Dashboard"


class MobileTextContentAdmin(admin.ModelAdmin):
    list_display = ("code", "group", "created_at")
    list_filter = ("group", "created_at")
    search_fields = ("code", "group", "text")
    ordering = ("-created_at",)
    readonly_fields = ("created_at",)


admin.site.register(
    [
        DifficultyLevel,
        Equipment,
        Exercise,
        ExerciseType,
        WorkoutItem,
        WorkoutDay,
        WorkoutPlan,
        SubscriptionPlan,
        Gym,
        GymReview,
        Address,
        BugReport,
        NewFeatureRequest,
        ClientProfile,
        EmailVerificationCode,
        Subscription,
        SubscriptionPayment,
        WorkoutPlanRun,
        WorkoutDayLog,
        WorkoutItemLog,
        WorkoutSetLog,
    ]
)
admin.site.register(MobileTextContent, MobileTextContentAdmin)
