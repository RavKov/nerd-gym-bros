from django.db import models

from .dictionaries import Equipment
from .client_profile import ClientProfile


class Address(models.Model):
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    latitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True
    )
    longitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True
    )

    class Meta:
        indexes = [
            models.Index(fields=["city"]),
            models.Index(fields=["country"]),
        ]

    def __str__(self):
        return f"{self.street}, {self.city}, {self.country}"


class Gym(models.Model):
    name = models.CharField(max_length=100)
    address = models.ForeignKey(Address, on_delete=models.CASCADE)
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=20)
    equipments = models.ManyToManyField(Equipment, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["address"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return self.name


class GymReview(models.Model):
    gym = models.ForeignKey(Gym, on_delete=models.CASCADE, related_name="reviews")
    client = models.ForeignKey(ClientProfile, on_delete=models.CASCADE)
    rating = models.IntegerField()  # e.g., 1 to 5
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (
            "gym",
            "client",
        )  # jeden użytkownik może dodać tylko jedną recenzję do danego gymu
        indexes = [
            models.Index(fields=["gym"]),
            models.Index(fields=["client"]),
            models.Index(fields=["rating"]),
        ]

    def __str__(self):
        return f"{self.gym.name} · {self.client.user.username} · {self.rating} stars"
