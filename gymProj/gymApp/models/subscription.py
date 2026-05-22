from decimal import Decimal

from django.contrib.auth.models import User
from django.db import models

from .workout_plan import WorkoutPlan


class SubscriptionPlan(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # e.g., 99.99
    stripe_price_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    features = models.TextField()  # Description of features included
    workout_plans = models.ManyToManyField(WorkoutPlan)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return self.name


class Subscription(models.Model):
    STATUS_CHOICES = [
        ("incomplete", "Incomplete"),
        ("active", "Active"),
        ("past_due", "Past due"),
        ("canceled", "Canceled"),
        ("unpaid", "Unpaid"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stripe_customer_id = models.CharField(max_length=255)
    stripe_subscription_id = models.CharField(max_length=255, unique=True)
    price_id = models.CharField(max_length=255)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES)

    # Canonical billing period (source of truth: Stripe subscription)
    current_period_start = models.DateTimeField(null=True, blank=True)
    current_period_end = models.DateTimeField(null=True, blank=True)
    cancel_at_period_end = models.BooleanField(default=False)
    canceled_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["user", "status"]),
            models.Index(fields=["stripe_customer_id"]),
            models.Index(fields=["stripe_subscription_id"]),
            models.Index(fields=["current_period_end"]),
        ]

    def __str__(self):
        return f"{self.user.username} · {self.status} · ends {self.current_period_end}"


class SubscriptionPayment(models.Model):
    stripe_invoice_id = models.CharField(max_length=255, unique=True)
    subscription = models.ForeignKey(Subscription, null=True, blank=True, on_delete=models.SET_NULL)
    amount_paid = models.BigIntegerField()  # in cents
    currency = models.CharField(max_length=10)
    paid_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["subscription"]),
            models.Index(fields=["paid_at"]),
        ]

    @property
    def amount_paid_major(self):
        return Decimal(self.amount_paid or 0) / Decimal("100")

    def __str__(self):
        return f"Payment {self.stripe_invoice_id} {self.amount_paid} {self.currency}"
