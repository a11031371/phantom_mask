from django.urls import path
from . import views

urlpatterns = [
    path("pharmacies/open/", views.OpenPharmaciesListCreate.as_view(), name="open-pharmacies-view-create"),
    path("pharmacies/masks/", views.PharmacyMasksListCreate.as_view(), name="pharmacy-masks-view-create"),
]