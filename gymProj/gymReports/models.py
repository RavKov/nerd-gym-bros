from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


REPORT_TEMPLATE_CHOICES = [
    ("gyms_directory", "Gyms Directory"),
    ("clients_overview", "Clients Overview"),
    ("subscription_payments", "Subscription Payments"),
]


class PrintTemplate(models.Model):
    report_key = models.CharField(max_length=64, choices=REPORT_TEMPLATE_CHOICES)
    name = models.CharField(max_length=120)
    template_file = models.FileField(upload_to="print_templates/")
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [models.Index(fields=["report_key", "is_active"])]
        ordering = ["-updated_at", "-created_at"]

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.is_active:
            PrintTemplate.objects.filter(report_key=self.report_key, is_active=True).exclude(
                pk=self.pk
            ).update(is_active=False)

    def __str__(self):
        return f"{self.name} ({self.report_key})"
