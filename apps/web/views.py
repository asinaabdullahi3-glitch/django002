from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _

from apps.adoptions.models import AdoptionRequest, RequestStatus
from apps.pets.models import AdoptionStatus, Pet

from .forms import ContactForm


def home(request):
    if request.user.is_authenticated:
        # Get statistics based on user type
        if request.user.is_shelter() or request.user.is_superuser:
            # Shelter dashboard statistics
            total_pets = Pet.objects.count()
            available_pets = Pet.objects.filter(adoption_status=AdoptionStatus.AVAILABLE).count()
            pending_requests = AdoptionRequest.objects.filter(status=RequestStatus.PENDING).count()
            adopted_pets = Pet.objects.filter(adoption_status=AdoptionStatus.ADOPTED).count()
            
            context = {
                "active_tab": "dashboard",
                "page_title": _("Dashboard"),
                "is_shelter": True,
                "total_pets": total_pets,
                "available_pets": available_pets,
                "pending_requests": pending_requests,
                "adopted_pets": adopted_pets,
            }
        else:
            # Adopter dashboard statistics
            my_requests = AdoptionRequest.objects.filter(user=request.user).count()
            pending_requests = AdoptionRequest.objects.filter(
                user=request.user, status=RequestStatus.PENDING
            ).count()
            approved_requests = AdoptionRequest.objects.filter(
                user=request.user, status=RequestStatus.APPROVED
            ).count()
            available_pets = Pet.objects.filter(adoption_status=AdoptionStatus.AVAILABLE).count()
            
            context = {
                "active_tab": "dashboard",
                "page_title": _("Dashboard"),
                "is_shelter": False,
                "my_requests": my_requests,
                "pending_requests": pending_requests,
                "approved_requests": approved_requests,
                "available_pets": available_pets,
            }
        
        return render(request, "web/app_home.html", context)
    else:
        return render(request, "web/landing_page.html")


def contact(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            # In a real application, you would send an email here
            # For now, we'll just show a success message
            messages.success(request, "Thank you for your message! We'll get back to you soon.")
            return render(request, "web/contact.html", {"form": ContactForm()})
    else:
        form = ContactForm()

    return render(request, "web/contact.html", {"form": form})


@user_passes_test(lambda u: u.is_superuser)
def simulate_error(request):
    raise Exception("This is a simulated error.")
