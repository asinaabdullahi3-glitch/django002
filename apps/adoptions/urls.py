from django.urls import path

from . import views

app_name = "adoptions"

urlpatterns = [
    path("", views.home, name="adoptions_home"),
    path("request/<int:pet_id>/", views.AdoptionRequestCreateView.as_view(), name="request_create"),
    path("my-requests/", views.MyRequestsView.as_view(), name="my_requests"),
    path("requests/", views.RequestListView.as_view(), name="request_list"),
    path("request/<int:pk>/approve/", views.approve_request, name="request_approve"),
    path("request/<int:pk>/reject/", views.reject_request, name="request_reject"),
    path("request/<int:pk>/cancel/", views.cancel_request, name="request_cancel"),
]
