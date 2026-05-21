from django.db import models
from django.contrib.auth.models import User


class BugReport(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    screenshot = models.ImageField(upload_to="bug_screenshots/", null=True, blank=True)
    resolved = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["resolved"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"{self.title} · reported by {self.user.username if self.user else 'Anonymous'}"


class NewFeatureRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    implemented_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=50,
        choices=[
            ("pending", "Pending"),
            ("accepted", "Accepted"),
            ("implemented", "Implemented"),
            ("rejected", "Rejected"),
        ],
        default="pending",
    )

    class Meta:
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["status"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"{self.title} · requested by {self.user.username if self.user else 'Anonymous'}"


class MobileTextContent(models.Model):
    code = models.CharField(max_length=255, unique=True)
    group = models.CharField(max_length=255)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["group"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return self.code
