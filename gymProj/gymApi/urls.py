from django.urls import path

from gymApi import views
from gymApi.auth_views import (
    ThrottledTokenObtainPairView,
    ThrottledTokenRefreshView,
)

# TODO - ADD me TO URLS RELATED TO CLIENT IN APP
app_name = "gymApi"

urlpatterns = [
    path("health/", views.HealthCheckAPI.as_view(), name="health_check_api"),
    path(
        "auth/token/",
        ThrottledTokenObtainPairView.as_view(),
        name="token_obtain_pair",
    ),
    path(
        "auth/token/refresh/",
        ThrottledTokenRefreshView.as_view(),
        name="token_refresh",
    ),
    path("register/", views.RegisterAPI.as_view(), name="api_register"),
    path(
        "exercises/",
        views.ExerciseListAPI.as_view(),
        name="exercise_list_api",
    ),
    path(
        "exercises/<int:pk>/",
        views.ExerciseDetailUpdateDeleteAPI.as_view(),
        name="exercise_detail_update_delete_api",
    ),
    path(
        "me/detail/",
        views.ClientDetailAPI.as_view(),
        name="me_detail_api",
    ),
    path("me/verify/", views.VerifyEmailAPI.as_view(), name="verify_email_api"),
    path(
        "me/resend_verification/",
        views.ResendVerificationAPI.as_view(),
        name="resend_verification_api",
    ),
    path(
        "subscription_plans/",
        views.SubscriptionPlanListAPI.as_view(),
        name="subscription_plan_list_api",
    ),
    path(
        "me/subscription_plan/choose/",
        views.SubscriptionPlanChooseAPI.as_view(),
        name="subscription_plan_choose_api",
    ),
    path(
        "me/subscription/",
        views.SubscriptionDetailAPI.as_view(),
        name="subscription_detail_api",
    ),
    path(
        "workout_plans/",
        views.WorkoutPlanListAPI.as_view(),
        name="workout_plan_list_api",
    ),
    path(
        "me/workout_plan/",
        views.WorkoutPlanChooseAPI.as_view(),
        name="workout_plan_choose_api",
    ),
    # path("create_payment_intent/", views.CreatePaymentIntentAPI.as_view()),
    path("create_subscription_sheet/", views.CreateSubscriptionSheetAPI.as_view()),
    path("stripe_webhook/", views.stripe_webhook),
    path("cancel_subscription/", views.CancelSubscriptionAPI.as_view()),
    path("create_bug_report/", views.BugReportAPI.as_view(), name="bug_report_create_api"),
    path(
        "create_feature_request/",
        views.NewFeatureRequestAPI.as_view(),
        name="feature_request_create_api",
    ),
    path(
        "me/workout_plan_run/",
        views.WorkoutPlanRunAPI.as_view(),
        name="workout_plan_run_api",
    ),
    path(
        "me/workout_day_log/<int:pk>/",
        views.WorkoutDayDetailedLogAPI.as_view(),
        name="workout_day_detailed_log_api",
    ),
    path(
        "me/workout_item_log/<int:pk>/",
        views.WorkoutItemDetailedLogAPI.as_view(),
        name="workout_item_detailed_log_api",
    ),
    path("me/set_log/<int:pk>/", views.update_set_log, name="update_set_log_api"),
    path("gyms/", views.GymListAPI.as_view(), name="gym_list_api"),
    path("equipments/", views.EquipmentListAPI.as_view(), name="equipment_list_api"),
    path(
        "mobile_app_content/",
        views.MobileTextContentListAPI.as_view(),
        name="mobile_app_content_list_api",
    ),
    path(
        "mobile_app_content/create/",
        views.MobileTextContentCreateAPI.as_view(),
        name="mobile_app_content_create_api",
    ),
    path(
        "mobile_app_content/<str:code>/",
        views.MobileTextContentDetailAPI.as_view(),
        name="mobile_app_content_detail_api",
    ),
    path(
        "mobile_app_content/<str:code>/edit/",
        views.MobileTextContentUpdateDeleteAPI.as_view(),
        name="mobile_app_content_update_delete_api",
    ),
]
