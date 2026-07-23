from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from apps.pets.models import AdoptionStatus


def _reset_pet_if_no_active_requests(pet):
    """
    If a pet has no remaining non-cancelled adoption requests,
    reset its status back to Available.
    This handles the case where the adopter user is deleted (CASCADE removes
    the request) or where requests are cancelled/deleted directly.
    """
    from apps.adoptions.models import AdoptionRequest

    if pet.adoption_status == AdoptionStatus.AVAILABLE:
        return  # nothing to do

    has_active = AdoptionRequest.objects.filter(pet=pet).exclude(status="cancelled").exists()
    if not has_active:
        pet.adoption_status = AdoptionStatus.AVAILABLE
        pet.save(update_fields=["adoption_status"])


@receiver(post_delete, sender="adoptions.AdoptionRequest")
def reset_pet_on_request_delete(sender, instance, **kwargs):
    """When an adoption request is deleted (including via user CASCADE), reset the pet."""
    _reset_pet_if_no_active_requests(instance.pet)


@receiver(post_save, sender="adoptions.AdoptionRequest")
def reset_pet_on_request_cancelled(sender, instance, created, **kwargs):
    """When a request is saved as Cancelled, reset the pet if no other active requests remain."""
    if not created and instance.status == "cancelled":
        _reset_pet_if_no_active_requests(instance.pet)
