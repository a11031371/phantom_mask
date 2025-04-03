from django.urls import path
from . import views

urlpatterns = [
    path("pharmacies/open/", views.OpenPharmaciesListCreate.as_view(), name="open-pharmacies-view-create"),
]