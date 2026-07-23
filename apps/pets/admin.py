from django.contrib import admin

from .models import Pet


@admin.register(Pet)
class PetAdmin(admin.ModelAdmin):
    list_display = ["name", "breed", "species", "age", "gender", "adoption_status", "created_at"]
    list_filter = ["species", "gender", "adoption_status"]
    search_fields = ["name", "breed", "description"]
    ordering = ["-created_at"]
