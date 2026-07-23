from django.urls import path

from . import views

app_name = "pets"

urlpatterns = [
    path("", views.home, name="pets_home"),
    path("list/", views.PetListView.as_view(), name="pet_list"),
    path("<int:pk>/", views.PetDetailView.as_view(), name="pet_detail"),
    path("create/", views.PetCreateView.as_view(), name="pet_create"),
    path("<int:pk>/edit/", views.PetUpdateView.as_view(), name="pet_update"),
    path("<int:pk>/delete/", views.PetDeleteView.as_view(), name="pet_delete"),
]
