from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand

from apps.pets.models import Pet
from apps.adoptions.models import AdoptionRequest


class Command(BaseCommand):
    help = "Create Shelter and Adopter groups with appropriate permissions"

    def handle(self, *args, **options):
        # Create or get the Shelter group
        shelter_group, created = Group.objects.get_or_create(name="Shelter")
        if created:
            self.stdout.write(self.style.SUCCESS("Created 'Shelter' group"))
        else:
            self.stdout.write(self.style.WARNING("'Shelter' group already exists"))

        # Create or get the Adopter group
        adopter_group, created = Group.objects.get_or_create(name="Adopter")
        if created:
            self.stdout.write(self.style.SUCCESS("Created 'Adopter' group"))
        else:
            self.stdout.write(self.style.WARNING("'Adopter' group already exists"))

        # Assign permissions to Shelter group (can manage pets and adoption requests)
        pet_permissions = Permission.objects.filter(
            codename__in=["add_pet", "change_pet", "delete_pet", "view_pet"],
            content_type__model="pet",
        )
        adoption_permissions = Permission.objects.filter(
            codename__in=["add_adoptionrequest", "change_adoptionrequest", "delete_adoptionrequest", "view_adoptionrequest"],
            content_type__model="adoptionrequest",
        )

        shelter_group.permissions.set(list(pet_permissions) + list(adoption_permissions))
        shelter_group.save()
        self.stdout.write(self.style.SUCCESS("Assigned permissions to 'Shelter' group"))

        # Adopter group has no special permissions (can view pets and create requests via views)
        self.stdout.write(self.style.SUCCESS("'Adopter' group configured"))

        self.stdout.write(self.style.SUCCESS("Groups bootstrapped successfully!"))
