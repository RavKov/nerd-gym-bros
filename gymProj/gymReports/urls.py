from django.urls import path

from . import views

app_name = "gymReports"

urlpatterns = [
    path("", views.reports_index, name="reports_index"),
    path(
        "print-templates/",
        views.PrintTemplateListView.as_view(),
        name="print_template_list",
    ),
    path(
        "print-templates/create/",
        views.PrintTemplateCreateView.as_view(),
        name="print_template_create",
    ),
    path(
        "print-templates/<int:pk>/update/",
        views.PrintTemplateUpdateView.as_view(),
        name="print_template_update",
    ),
    path(
        "print-templates/<int:pk>/delete/",
        views.PrintTemplateDeleteView.as_view(),
        name="print_template_delete",
    ),
    path(
        "print-templates/<slug:report_key>/reset/",
        views.reset_default_template,
        name="print_template_reset",
    ),
    path(
        "print/<slug:report_key>.docx",
        views.report_docx,
        name="report_docx",
    ),
    path(
        "print/<slug:report_key>/<int:template_id>.docx",
        views.report_docx,
        name="report_docx_by_template",
    ),
    path(
        "exercises.xlsx",
        views.exercises_xlsx,
        name="exercises_xlsx",
    ),
    path(
        "workout_plans_full.xlsx",
        views.workout_plans_full_report_xlsx,
        name="workout_plans_full_report_xlsx",
    ),
    path("<slug:report_key>.xlsx", views.report_xlsx, name="report_xlsx"),
    path("<slug:report_key>.pdf", views.report_pdf, name="report_pdf"),
]
