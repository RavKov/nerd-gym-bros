from django.db import models
from django.utils import timezone

from .client_profile import ClientProfile
from .workout_plan import WorkoutDay, WorkoutItem, WorkoutPlan


class WorkoutPlanRun(models.Model):
    """
    Jedno uruchomienie (podejście) użytkownika do danego planu.
    Dzięki temu można robić ten sam plan wielokrotnie z osobnym postępem.
    """

    client = models.ForeignKey(
        ClientProfile, on_delete=models.CASCADE, related_name="workout_plan_runs"
    )
    workout_plan = models.ForeignKey(WorkoutPlan, on_delete=models.CASCADE, related_name="runs")
    started_at = models.DateTimeField(default=timezone.now)
    finished_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        indexes = [
            models.Index(fields=["client", "workout_plan", "is_active"]),
        ]

    def __str__(self):
        return f"{self.client.user.username} · {self.workout_plan.name} · active={self.is_active}"


class WorkoutDayLog(models.Model):
    workout_plan_run = models.ForeignKey(
        WorkoutPlanRun, on_delete=models.CASCADE, related_name="day_logs"
    )
    workout_day = models.ForeignKey(WorkoutDay, on_delete=models.CASCADE, related_name="logs")
    date = models.DateField(default=timezone.localdate)
    completed = models.BooleanField(default=False)

    class Meta:
        constraints = [
            # jeden log na (run, dzień, data)
            models.UniqueConstraint(
                fields=["workout_plan_run", "workout_day", "date"],
                name="unique_day_log_per_run_day_date",
            )
        ]
        indexes = [
            models.Index(fields=["workout_plan_run"]),
            models.Index(fields=["date"]),
        ]
        ordering = ["-date", "id"]

    def __str__(self):
        return f"Log {self.workout_day} ({self.workout_plan_run}) on {self.date}"


class WorkoutItemLog(models.Model):
    workout_day_log = models.ForeignKey(
        WorkoutDayLog, on_delete=models.CASCADE, related_name="item_logs"
    )
    workout_item = models.ForeignKey(WorkoutItem, on_delete=models.CASCADE, related_name="logs")
    completed = models.BooleanField(default=False)

    notes = models.TextField(blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["workout_day_log", "workout_item"],
                name="unique_item_log_per_day_log",
            )
        ]
        indexes = [
            models.Index(fields=["workout_day_log"]),
            models.Index(fields=["workout_item"]),
        ]

    def __str__(self):
        return f"{self.workout_day_log} · item#{self.workout_item.order} · done={self.completed}"


class WorkoutSetLog(models.Model):
    workout_item_log = models.ForeignKey(
        WorkoutItemLog, on_delete=models.CASCADE, related_name="set_logs"
    )
    set_number = models.IntegerField()
    actual_amount = models.IntegerField(default=0)
    weight = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["workout_item_log", "set_number"],
                name="unique_set_log_per_item_log",
            )
        ]
        indexes = [
            models.Index(fields=["workout_item_log"]),
        ]
        ordering = ["set_number"]

    def __str__(self):
        return f"{self.workout_item_log} · set {self.set_number}"
