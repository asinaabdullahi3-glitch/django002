from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import reverse, reverse_lazy
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, ListView

from apps.adoptions.models import AdoptionRequest, RequestStatus
from apps.pets.models import AdoptionStatus, Pet


@login_required
def home(request):
    template = "adoptions/adoptions_home.html#page-content" if request.htmx else "adoptions/adoptions_home.html"

    return TemplateResponse(request, template, {"active_tab": "adoptions"})


class AdoptionRequestCreateView(LoginRequiredMixin, CreateView):
    """Create a new adoption request for a pet."""

    model = AdoptionRequest
    template_name = "adoptions/request_form.html"
    fields = ["message"]

    def dispatch(self, request, *args, **kwargs):
        # Let LoginRequiredMixin handle unauthenticated users first
        if not request.user.is_authenticated:
            return super().dispatch(request, *args, **kwargs)
        self.pet = Pet.objects.get(pk=self.kwargs["pet_id"])
        
        # Check if pet is available
        if self.pet.adoption_status != AdoptionStatus.AVAILABLE:
            messages.error(request, "This pet is not available for adoption.")
            return redirect(reverse("pets:pet_detail", kwargs={"pk": self.pet.pk}))
        
        # Check if user already has any active request for this pet (non-cancelled)
        if AdoptionRequest.objects.filter(
            user=request.user, pet=self.pet
        ).exclude(status=RequestStatus.CANCELLED).exists():
            messages.warning(request, "You already have an adoption request for this pet.")
            return redirect(reverse("pets:pet_detail", kwargs={"pk": self.pet.pk}))
        
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.pet = self.pet
        form.instance.status = RequestStatus.PENDING
        messages.success(self.request, "Your adoption request has been submitted successfully!")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("adoptions:my_requests")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["pet"] = self.pet
        return context


class MyRequestsView(LoginRequiredMixin, ListView):
    """List view for current user's adoption requests."""

    model = AdoptionRequest
    template_name = "adoptions/my_requests.html"
    context_object_name = "requests"

    def get_queryset(self):
        return AdoptionRequest.objects.filter(user=self.request.user).select_related("pet")


class RequestListView(LoginRequiredMixin, ListView):
    """List view for all adoption requests (shelter admin only)."""

    model = AdoptionRequest
    template_name = "adoptions/request_list.html"
    context_object_name = "requests"

    def dispatch(self, request, *args, **kwargs):
        if not (request.user.is_shelter() or request.user.is_superuser):
            messages.error(request, "You don't have permission to view this page.")
            return redirect("web:home")
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        queryset = AdoptionRequest.objects.all().select_related("user", "pet")
        
        # Filter by status
        status = self.request.GET.get("status")
        if status:
            queryset = queryset.filter(status=status)
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["status_choices"] = RequestStatus.choices
        context["current_status"] = self.request.GET.get("status", "")
        return context


@login_required
@require_POST
def approve_request(request, pk):
    """Approve an adoption request (shelter admin only)."""
    if not (request.user.is_shelter() or request.user.is_superuser):
        messages.error(request, "You don't have permission to perform this action.")
        return redirect("web:home")
    
    adoption_request = AdoptionRequest.objects.get(pk=pk)
    
    if adoption_request.status != RequestStatus.PENDING:
        messages.warning(request, "This request has already been processed.")
        return redirect("adoptions:request_list")
    
    # Update request status
    adoption_request.status = RequestStatus.APPROVED
    adoption_request.save()
    
    # Update pet status
    adoption_request.pet.adoption_status = AdoptionStatus.ADOPTED
    adoption_request.pet.save()
    
    # Reject other pending requests for this pet
    AdoptionRequest.objects.filter(
        pet=adoption_request.pet,
        status=RequestStatus.PENDING
    ).exclude(pk=pk).update(status=RequestStatus.REJECTED)
    
    messages.success(request, f"Adoption request for {adoption_request.pet.name} has been approved.")
    return redirect("adoptions:request_list")


@login_required
@require_POST
def reject_request(request, pk):
    """Reject an adoption request (shelter admin only)."""
    if not (request.user.is_shelter() or request.user.is_superuser):
        messages.error(request, "You don't have permission to perform this action.")
        return redirect("web:home")
    
    adoption_request = AdoptionRequest.objects.get(pk=pk)
    
    if adoption_request.status != RequestStatus.PENDING:
        messages.warning(request, "This request has already been processed.")
        return redirect("adoptions:request_list")
    
    adoption_request.status = RequestStatus.REJECTED
    adoption_request.save()
    
    messages.success(request, f"Adoption request for {adoption_request.pet.name} has been rejected.")
    return redirect("adoptions:request_list")


@login_required
@require_POST
def cancel_request(request, pk):
    """Cancel a pending adoption request (adopter only)."""
    adoption_request = AdoptionRequest.objects.get(pk=pk)
    
    if adoption_request.user != request.user:
        messages.error(request, "You can only cancel your own requests.")
        return redirect("adoptions:my_requests")
    
    if adoption_request.status != RequestStatus.PENDING:
        messages.warning(request, "You can only cancel pending requests.")
        return redirect("adoptions:my_requests")
    
    adoption_request.status = RequestStatus.CANCELLED
    adoption_request.save()
    
    messages.success(request, "Your adoption request has been cancelled.")
    return redirect("adoptions:my_requests")
