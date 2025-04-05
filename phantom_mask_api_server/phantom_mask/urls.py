from django.urls import path
from . import views

urlpatterns = [
    path("pharmacies/open/", views.PharmacyOpenListView.as_view(), name="pharmacies-open-list-view"),
    path("pharmacies/masks/", views.PharmacyMasksListView.as_view(), name="pharmacy-masks-list-view"),
    path("pharmacies/compare-masks/", views.PharmaciesCompareMaskListView.as_view(), name="pharmacies-compare-mask-list-view"),
    path("transactions/active-users/", views.ActiveTransactionsUserListView.as_view(), name="freq-transactions-user-list-view"),
    path("transactions/amounts/", views.MaskTransactionsListView.as_view(), name="mask-transactions-list-view"),
    path("search/", views.SearchView.as_view(), name="search-view"),
    path("purchase/masks/", views.PurchaseMaskView.as_view(), name="purchase-mask-view"),
    path("cancel-transactions/latest/", views.CancelLatestTransactionView.as_view(), name="cancel-latest-transaction-view"),
]