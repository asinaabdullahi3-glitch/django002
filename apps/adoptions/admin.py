from django.contrib import admin

from .models import AdoptionRequest


@admin.register(AdoptionRequest)
class AdoptionRequestAdmin(admin.ModelAdmin):
    list_display = ["user", "pet", "status", "created_at"]
    list_filter = ["status", "created_at"]
    search_fields = ["user__email", "user__username", "pet__name", "pet__breed"]
    ordering = ["-created_at"]
    readonly_fields = ["created_at", "updated_at"]
