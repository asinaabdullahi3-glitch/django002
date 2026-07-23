from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView
from django.contrib.auth.decorators import login_required

from .models import AdoptionStatus, Gender, Pet, Species


@login_required
def home(request):
    template = "pets/pets_home.html#page-content" if request.htmx else "pets/pets_home.html"

    return TemplateResponse(request, template, {"active_tab": "pets"})


class PetListView(ListView):
    """List view for all available pets with filtering."""

    model = Pet
    template_name = "pets/pet_list.html"
    context_object_name = "pets"
    paginate_by = 12

    def _is_admin(self):
        user = self.request.user
        return user.is_authenticated and (user.is_shelter() or user.is_superuser)

    def get_queryset(self):
        # Admins see all pets; adopters see only available ones
        if self._is_admin():
            queryset = Pet.objects.all()
        else:
            queryset = Pet.objects.filter(adoption_status=AdoptionStatus.AVAILABLE)

        # Filter by species
        species = self.request.GET.get("species")
        if species:
            queryset = queryset.filter(species=species)

        # Filter by gender
        gender = self.request.GET.get("gender")
        if gender:
            queryset = queryset.filter(gender=gender)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["species_choices"] = Species.choices
        context["gender_choices"] = Gender.choices
        context["is_admin"] = self._is_admin()
        context["current_filters"] = {
            "species": self.request.GET.get("species", ""),
            "gender": self.request.GET.get("gender", ""),
        }
        return context


class PetDetailView(DetailView):
    """Detail view for individual pet."""

    model = Pet
    template_name = "pets/pet_detail.html"
    context_object_name = "pet"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            from apps.adoptions.models import AdoptionRequest, RequestStatus
            context["has_existing_request"] = AdoptionRequest.objects.filter(
                user=self.request.user,
                pet=self.object,
            ).exclude(status=RequestStatus.CANCELLED).exists()
        else:
            context["has_existing_request"] = False
        return context


class PetCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """Create a new pet (shelter admin only)."""

    model = Pet
    template_name = "pets/pet_form.html"
    fields = ["name", "breed", "species", "age", "gender", "description", "adoption_status", "image"]
    success_url = reverse_lazy("pets:pet_list")

    def test_func(self):
        return self.request.user.is_shelter() or self.request.user.is_superuser

    def handle_no_permission(self):
        messages.error(self.request, "You don't have permission to add pets.")
        return redirect("pets:pet_list")

    def form_valid(self, form):
        messages.success(self.request, "Pet has been added successfully!")
        return super().form_valid(form)


class PetUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Update an existing pet (shelter admin only)."""

    model = Pet
    template_name = "pets/pet_form.html"
    fields = ["name", "breed", "species", "age", "gender", "description", "adoption_status", "image"]
    success_url = reverse_lazy("pets:pet_list")

    def test_func(self):
        return self.request.user.is_shelter() or self.request.user.is_superuser

    def handle_no_permission(self):
        messages.error(self.request, "You don't have permission to edit pets.")
        return redirect("pets:pet_list")

    def form_valid(self, form):
        messages.success(self.request, "Pet has been updated successfully!")
        return super().form_valid(form)


class PetDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Delete a pet (shelter admin only)."""

    model = Pet
    template_name = "pets/pet_confirm_delete.html"
    success_url = reverse_lazy("pets:pet_list")

    def test_func(self):
        return self.request.user.is_shelter() or self.request.user.is_superuser

    def handle_no_permission(self):
        messages.error(self.request, "You don't have permission to delete pets.")
        return redirect("pets:pet_list")

    def form_valid(self, form):
        messages.success(self.request, "Pet has been deleted successfully!")
        return super().form_valid(form)
