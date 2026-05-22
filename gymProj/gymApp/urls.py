from django.shortcuts import render
from django.urls import path
import gymApp.views as views


def custom_permission_denied_view(request, exception=None):
    return render(request, "403.html", status=403)


handler403 = custom_permission_denied_view

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("", views.home_view, name="home"),
    path("exercises/", views.ExerciseListView.as_view(), name="exercise_list"),
    path(
        "exercises/<int:pk>/",
        views.ExerciseDetailView.as_view(),
        name="exercise_detail",
    ),
    path(
        "exercises/create/", views.ExerciseCreateView.as_view(), name="exercise_create"
    ),
    path(
        "exercises/<int:pk>/update/",
        views.ExerciseUpdateView.as_view(),
        name="exercise_update",
    ),
    path(
        "exercises/<int:pk>/delete/",
        views.ExerciseDeleteView.as_view(),
        name="exercise_delete",
    ),
    path(
        "workout_plans/", views.WorkoutPlanListView.as_view(), name="workout_plan_list"
    ),
    path(
        "workout_plans/create/",
        views.WorkoutPlanCreateView.as_view(),
        name="workout_plan_create",
    ),
    path(
        "workout_plans/<int:pk>/update/",
        views.WorkoutPlanUpdateView.as_view(),
        name="workout_plan_update",
    ),
    path(
        "workout_plans/<int:pk>/delete/",
        views.WorkoutPlanDeleteView.as_view(),
        name="workout_plan_delete",
    ),
    path(
        "workout_items/create/",
        views.workout_item_create_view,
        name="workout_item_create",
    ),
    path(
        "workout_items/<int:pk>/delete/",
        views.workout_item_delete_view,
        name="workout_item_delete",
    ),
    path(
        "workout_items/reorder/",
        views.workout_item_reorder_view,
        name="workout_item_reorder",
    ),
    path(
        "workout_days/reorder/",
        views.workout_day_reorder_view,
        name="workout_day_reorder",
    ),
    path(
        "workout_days/create/",
        views.workout_day_create_view,
        name="workout_day_create",
    ),
    path(
        "workout_days/<int:pk>/update/",
        views.workout_day_update_view,
        name="workout_day_update",
    ),
    path(
        "workout_days/<int:pk>/delete/",
        views.workout_day_delete_view,
        name="workout_day_delete",
    ),
    path(
        "subscription_plans/",
        views.SubscriptionPlanListView.as_view(),
        name="subscription_plan_list",
    ),
    path(
        "subscription_plans/create/",
        views.SubscriptionPlanCreateView.as_view(),
        name="subscription_plan_create",
    ),
    path(
        "subscription_plans/<int:pk>/update/",
        views.SubscriptionPlanUpdateView.as_view(),
        name="subscription_plan_update",
    ),
    path(
        "subscription_plans/<int:pk>/delete/",
        views.SubscriptionPlanDeleteView.as_view(),
        name="subscription_plan_delete",
    ),
    path("gyms/", views.GymListView.as_view(), name="gym_list"),
    path("gyms/create/", views.GymCreateView.as_view(), name="gym_create"),
    path("gyms/<int:pk>/", views.GymDetailView.as_view(), name="gym_detail"),
    path(
        "gyms/<int:pk>/update/",
        views.GymUpdateView.as_view(),
        name="gym_update",
    ),
    path(
        "gyms/<int:pk>/delete/",
        views.GymDeleteView.as_view(),
        name="gym_delete",
    ),
    path(
        "bug-reports/",
        views.BugReportListView.as_view(),
        name="bug_report_list",
    ),
    path(
        "bug-reports/create/",
        views.BugReportCreateView.as_view(),
        name="bug_report_create",
    ),
    path(
        "bug-reports/<int:pk>/",
        views.BugReportDetailView.as_view(),
        name="bug_report_detail",
    ),
    path(
        "bug-reports/<int:pk>/update/",
        views.BugReportUpdateView.as_view(),
        name="bug_report_update",
    ),
    path(
        "bug-reports/<int:pk>/delete/",
        views.BugReportDeleteView.as_view(),
        name="bug_report_delete",
    ),
    path(
        "feature-requests/",
        views.NewFeatureRequestListView.as_view(),
        name="new_feature_request_list",
    ),
    path(
        "feature-requests/create/",
        views.NewFeatureRequestCreateView.as_view(),
        name="new_feature_request_create",
    ),
    path(
        "feature-requests/<int:pk>/",
        views.NewFeatureRequestDetailView.as_view(),
        name="new_feature_request_detail",
    ),
    path(
        "feature-requests/<int:pk>/update/",
        views.NewFeatureRequestUpdateView.as_view(),
        name="new_feature_request_update",
    ),
    path(
        "feature-requests/<int:pk>/delete/",
        views.NewFeatureRequestDeleteView.as_view(),
        name="new_feature_request_delete",
    ),
    path("equipment/", views.EquipmentListView.as_view(), name="equipment_list"),
    path(
        "equipment/create/",
        views.EquipmentCreateView.as_view(),
        name="equipment_create",
    ),
    path(
        "equipment/<int:pk>/",
        views.EquipmentDetailView.as_view(),
        name="equipment_detail",
    ),
    path(
        "equipment/<int:pk>/update/",
        views.EquipmentUpdateView.as_view(),
        name="equipment_update",
    ),
    path(
        "equipment/<int:pk>/delete/",
        views.EquipmentDeleteView.as_view(),
        name="equipment_delete",
    ),
    path(
        "exercise-types/",
        views.ExerciseTypeListView.as_view(),
        name="exercise_type_list",
    ),
    path(
        "exercise-types/create/",
        views.ExerciseTypeCreateView.as_view(),
        name="exercise_type_create",
    ),
    path(
        "exercise-types/<int:pk>/",
        views.ExerciseTypeDetailView.as_view(),
        name="exercise_type_detail",
    ),
    path(
        "exercise-types/<int:pk>/update/",
        views.ExerciseTypeUpdateView.as_view(),
        name="exercise_type_update",
    ),
    path(
        "exercise-types/<int:pk>/delete/",
        views.ExerciseTypeDeleteView.as_view(),
        name="exercise_type_delete",
    ),
    path(
        "subscription-payments/",
        views.SubscriptionPaymentListView.as_view(),
        name="subscription_payment_list",
    ),
    path(
        "subscription-payments/create/",
        views.SubscriptionPaymentCreateView.as_view(),
        name="subscription_payment_create",
    ),
    path(
        "subscription-payments/<int:pk>/",
        views.SubscriptionPaymentDetailView.as_view(),
        name="subscription_payment_detail",
    ),
    path(
        "subscription-payments/<int:pk>/update/",
        views.SubscriptionPaymentUpdateView.as_view(),
        name="subscription_payment_update",
    ),
    path("staff/create/", views.StaffCreateView.as_view(), name="staff_create"),
    path("staff/", views.StaffListView.as_view(), name="staff_list"),
    path(
        "staff/<int:pk>/delete/",
        views.StaffDeleteView.as_view(),
        name="staff_delete",
    ),
    path(
        "staff/<int:pk>/update/", views.StaffUpdateView.as_view(), name="staff_update"
    ),
    path("clients/", views.ClientListView.as_view(), name="client_list"),
    path(
        "clients/<int:pk>/toggle_active",
        views.ClientToggleActiveView.as_view(),
        name="client_toggle_active",
    ),
    path("reports/", views.reports_view, name="reports"),
]

