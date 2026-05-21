from django.db import models, transaction
from .dictionaries import DifficultyLevel, Equipment


class Exercise(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    metabolic_equivalent = (
        models.FloatField()
    )  # Will be used to calculate calories burned
    video = models.FileField(upload_to="videos/")
    thumbnail = models.ImageField(upload_to="thumbnails/")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    equipments = models.ManyToManyField(Equipment, blank=True)
    difficulty_level = models.ForeignKey(DifficultyLevel, on_delete=models.CASCADE)
    amount_unit = models.CharField(max_length=50)  # e.g., reps, minutes
    exercise_type = models.ForeignKey("ExerciseType", on_delete=models.CASCADE)

    class Meta:
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["exercise_type"]),
            models.Index(fields=["difficulty_level"]),
        ]

    def __str__(self):
        return self.name


class WorkoutPlan(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    difficulty_level = models.ForeignKey(DifficultyLevel, on_delete=models.CASCADE)

    class Meta:
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["difficulty_level"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return self.name


class WorkoutDay(models.Model):
    workout_plan = models.ForeignKey(
        WorkoutPlan, on_delete=models.CASCADE, related_name="workout_days"
    )
    day_number = models.IntegerField()  # Order of the day in the workout plan
    description = models.TextField(blank=True)  # Optional description
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["day_number", "id"]
        indexes = [
            models.Index(fields=["workout_plan"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["workout_plan", "day_number"], name="unique_day_number_per_plan"
            )
        ]

    def __str__(self):
        return f"Day {self.day_number} of {self.workout_plan.name}"

    @classmethod
    def create_at_end(cls, **fields):
        with transaction.atomic():
            max_day_number = (
                cls.objects.select_for_update()
                .filter(workout_plan=fields["workout_plan"])
                .aggregate(models.Max("day_number"))["day_number__max"]
                or 0
            )
            fields["day_number"] = max_day_number + 1
            return cls.objects.create(**fields)

    def delete(self, *args, **kwargs):
        workout_plan = self.workout_plan
        day_to_free = self.day_number
        super().delete(*args, **kwargs)
        subsequent_days = WorkoutDay.objects.filter(
            workout_plan=workout_plan, day_number__gt=day_to_free
        )
        for item in subsequent_days:
            item.day_number -= 1
            item.save()


class WorkoutItem(models.Model):
    workout_day = models.ForeignKey(
        WorkoutDay, on_delete=models.CASCADE, related_name="items"
    )
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    amount = models.IntegerField()  # e.g., number of reps or duration in minutes
    sets = models.IntegerField()  #  number of sets
    order = models.IntegerField()  # Order in the workout plan
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.exercise.name}: {self.sets} sets of {self.amount} {self.exercise.amount_unit}"

    class Meta:
        ordering = ["order", "id"]
        indexes = [
            models.Index(fields=["workout_day"]),
            models.Index(fields=["exercise"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["workout_day", "order"], name="unique_order_per_workout_day"
            )
        ]

    @classmethod
    def create_at_end(cls, **fields):
        with transaction.atomic():
            max_order = (
                cls.objects.select_for_update()
                .filter(workout_day=fields["workout_day"])
                .aggregate(models.Max("order"))["order__max"]
                or 0
            )
            fields["order"] = max_order + 1
            return cls.objects.create(**fields)

    def delete(self, *args, **kwargs):
        wday = self.workout_day
        order_to_free = self.order
        super().delete(*args, **kwargs)
        subsequent_items = WorkoutItem.objects.filter(
            workout_day=wday, order__gt=order_to_free
        )
        for item in subsequent_items:
            item.order -= 1
            item.save()
