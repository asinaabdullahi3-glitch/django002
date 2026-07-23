from django.db import models

from apps.pets.models import Pet
from apps.users.models import CustomUser
from apps.utils.models import BaseModel


class RequestStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    APPROVED = "approved", "Approved"
    REJECTED = "rejected", "Rejected"
    CANCELLED = "cancelled", "Cancelled"


class AdoptionRequest(BaseModel):
    """
    Adoption request model linking users to pets.
    """

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="adoption_requests")
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE, related_name="adoption_requests")
    status = models.CharField(
        max_length=20,
        choices=RequestStatus.choices,
        default=RequestStatus.PENDING,
    )
    message = models.TextField(blank=True, help_text="Optional message from the adopter")

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Adoption Request"
        verbose_name_plural = "Adoption Requests"
        unique_together = [["user", "pet"]]  # Prevent duplicate requests

    def __str__(self):
        return f"{self.user.get_display_name()} - {self.pet.name} ({self.status})"
