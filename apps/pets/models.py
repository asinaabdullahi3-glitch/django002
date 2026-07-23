import uuid

from django.db import models

from apps.utils.models import BaseModel


def _get_pet_image_filename(instance, filename):
    """Use random filename to prevent overwriting existing files & fix caching issues."""
    return f"pet-images/{uuid.uuid4()}.{filename.split('.')[-1]}"


class Species(models.TextChoices):
    DOG = "dog", "Dog"
    CAT = "cat", "Cat"
    BIRD = "bird", "Bird"
    RABBIT = "rabbit", "Rabbit"
    OTHER = "other", "Other"


class Gender(models.TextChoices):
    MALE = "male", "Male"
    FEMALE = "female", "Female"


class AdoptionStatus(models.TextChoices):
    AVAILABLE = "available", "Available"
    PENDING = "pending", "Pending"
    ADOPTED = "adopted", "Adopted"


class Pet(BaseModel):
    """
    Pet model for the adoption system.
    """

    name = models.CharField(max_length=100)
    breed = models.CharField(max_length=100)
    species = models.CharField(max_length=20, choices=Species.choices, default=Species.DOG)
    age = models.PositiveIntegerField(help_text="Age in years")
    gender = models.CharField(max_length=10, choices=Gender.choices)
    description = models.TextField(blank=True)
    adoption_status = models.CharField(
        max_length=20,
        choices=AdoptionStatus.choices,
        default=AdoptionStatus.AVAILABLE,
    )
    image = models.ImageField(upload_to=_get_pet_image_filename, blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Pet"
        verbose_name_plural = "Pets"

    def __str__(self):
        return f"{self.name} ({self.breed})"
