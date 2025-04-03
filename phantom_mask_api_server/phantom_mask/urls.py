from django.urls import path
from . import views

urlpatterns = [
    path("pharmacies/open/", views.PharmacyOpenListCreate.as_view(), name="pharmacies-open-view-create"),
    path("pharmacies/masks/", views.PharmacyMasksListCreate.as_view(), name="pharmacy-masks-view-create"),
    path("pharmacies/compare-masks/", views.PharmaciesMaskCompareListCreate.as_view(), name="pharmacies-open-view-create"),
]