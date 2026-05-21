from django.db import models
from django.contrib.auth.models import User

from django.utils import timezone
import secrets
from django.utils.crypto import salted_hmac

from django.utils import timezone
from .subscription import SubscriptionPlan
from .workout_plan import WorkoutPlan


class ClientProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    subscription_plan = models.ForeignKey(
        SubscriptionPlan, on_delete=models.SET_NULL, null=True, blank=True
    )
    active_workout_plan = models.ForeignKey(
        WorkoutPlan, on_delete=models.SET_NULL, null=True, blank=True
    )
    age = models.IntegerField(null=True, blank=True)
    weight = models.FloatField(null=True, blank=True)  # in kg
    height = models.FloatField(null=True, blank=True)  # in cm
    goals = models.TextField(null=True, blank=True)
    verified = models.BooleanField(default=False)
    stripe_customer_id = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["subscription_plan"]),
            models.Index(fields=["active_workout_plan"]),
            models.Index(fields=["verified"]),
            models.Index(fields=["stripe_customer_id"]),
        ]

    def __str__(self):
        return self.user.username


class EmailVerificationCode(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="email_verification_codes"
    )
    code_hash = models.CharField(max_length=64)  # hexdigest sha256 z HMAC
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["user", "expires_at"]),
            models.Index(fields=["user", "used_at"]),
        ]

    @staticmethod
    def _hash_code(code: str) -> str:
        return salted_hmac("gymapp.email.verify", code).hexdigest()

    @classmethod
    def issue_for_user(
        cls, user: User, ttl_minutes: int = 15
    ) -> tuple["EmailVerificationCode", str]:
        """
        Tworzy nowy kod (6 cyfr), unieważnia poprzednie nieużyte kody i zwraca (obiekt, kod_plaintext).
        Kod plaintext zwracasz tylko do wysyłki mailem/SMS.
        """
        code = f"{secrets.randbelow(1_000_000):06d}"

        # unieważnij poprzednie nieużyte
        cls.objects.filter(user=user, used_at__isnull=True).delete()

        obj = cls.objects.create(
            user=user,
            code_hash=cls._hash_code(code),
            expires_at=timezone.now() + timezone.timedelta(minutes=ttl_minutes),
        )
        return obj, code

    def is_expired(self) -> bool:
        return self.expires_at <= timezone.now()

    def mark_used(self):
        self.used_at = timezone.now()
        self.save(update_fields=["used_at"])

    @classmethod
    def verify(cls, user: User, code: str) -> bool:
        """
        Zwraca True jeśli kod poprawny i aktualny; w takim wypadku oznacza go jako użyty.
        """
        evc = (
            cls.objects.filter(user=user, used_at__isnull=True)
            .order_by("-created_at")
            .first()
        )
        if not evc or evc.is_expired():
            return False
        if evc.code_hash != cls._hash_code(code):
            return False
        evc.mark_used()
        return True

    def __str__(self):
        return f"{self.user.username} · expires {self.expires_at} · used={bool(self.used_at)}"
