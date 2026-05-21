from django.db import models


class DifficultyLevel(models.Model):
    name = models.CharField(max_length=50)  # e.g., Beginner, Intermediate, Advanced

    class Meta:
        indexes = [
            models.Index(fields=["name"]),
        ]

    def __str__(self):
        return self.name


class Equipment(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        indexes = [
            models.Index(fields=["name"]),
        ]

    def __str__(self):
        return self.name


class ExerciseType(models.Model):
    name = models.CharField(max_length=100)  # e.g., Cardio, Strength, Flexibility

    class Meta:
        indexes = [
            models.Index(fields=["name"]),
        ]

    def __str__(self):
        return self.name
