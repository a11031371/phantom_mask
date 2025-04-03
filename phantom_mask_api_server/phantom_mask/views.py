from django.shortcuts import render
from rest_framework import generics
from .models import Pharmacies, Masks, PharmacyMasks, Transactions, Users
from django.db.models import Q, F, Count
from . import serializers
from rest_framework.exceptions import ValidationError
from datetime import datetime
import re

class PharmacyOpenListCreate(generics.ListCreateAPIView):
    """ List all pharmacies that are open at a given time on a given day. """

    serializer_class = serializers.PharmaciesNameSerializer
    def get_queryset(self):
        queryset = Pharmacies.objects.all()
        
        # Get query parameters
        day = self.request.query_params.get("day")
        time = self.request.query_params.get("time")

        if day and time:
            # validate day
            valid_days = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
            day = day.lower()
            if day not in valid_days:
                raise ValidationError({"error": "Invalid day provided. Please use a valid day of the week."})
            
            # validate time
            try:
                time = datetime.strptime(time, "%H:%M").time()
            except ValueError:
                raise ValidationError({"error": "Invalid time format. Please use HH:MM (24-hour format)."})
            
            # set query columns
            open_field = f"{day}_open"
            close_field = f"{day}_close"

            # standard case (open_time < close_time)
            standard_case = Q(**{f"{open_field}__lte": time, f"{close_field}__gte": time})

            # cross-day case (open_time > close_time)
            cross_day_case = Q(**{f"{open_field}__gt": F(f"{close_field}")}) & (
                Q(**{f"{close_field}__gte": time}) |  # 00:00 - close_time
                Q(**{f"{open_field}__lte": time})    # open_time - 23:59
            )
        else:
            raise ValidationError({"error": "Please provide both day and time parameters."})
        
        return queryset.filter(standard_case | cross_day_case)
    
class PharmacyMasksListCreate(generics.ListCreateAPIView):
    """ List all masks sold by a given pharmacy, sorted by mask name or price."""
    serializer_class = serializers.PharmacyMasksSerializer

    def get_queryset(self):
        queryset = PharmacyMasks.objects.all()

        # Get query parameters
        pharmacy_name = self.request.query_params.get("pharmacy")
        sort_by = self.request.query_params.get("sort_by")
        pharmacy_id = Pharmacies.objects.filter(name=pharmacy_name).values_list('id', flat=True).first()
        if pharmacy_id:
            queryset = queryset.filter(pharmacy_id=pharmacy_id)
        else:
            raise ValidationError({"error": "Pharmacy not found."})
        
        if sort_by:
            if sort_by == "name":
                queryset = queryset.order_by("mask__name")
            elif sort_by == "price":
                queryset = queryset.order_by("price")
            else:
                raise ValidationError({"error": "Invalid sort_by parameter. Use 'name' or 'price'."})

        return queryset
    
class PharmaciesMaskCompareListCreate(generics.ListCreateAPIView):
    """ List all pharmacies with more or less than x mask products within a price range."""

    serializer_class = serializers.PharmaciesMaskCountSerializer

    def get_queryset(self):
        """
        query parameters:
            min: minimum price of the masks.
            max: maximum price of the masks.
            cond: comparison operator + number (e.g., 'gt5', 'lt10').
        """

        # Get query parameters
        min_price = self.request.query_params.get("min")
        max_price = self.request.query_params.get("max")
        cond = self.request.query_params.get("cond")
        comp, x = re.match(r"([A-Za-z]+)(\d+)", cond).groups() if cond else (None, None)

        min_price = float(min_price) if min_price else 0.0
        max_price = float(max_price) if max_price else float("inf")

        queryset = Pharmacies.objects.filter(
            pharmacy_masks__price__gte=min_price,
            pharmacy_masks__price__lte=max_price
        ).annotate(
            mask_count=Count("pharmacy_masks__mask", distinct=True)
        ).all()

        if comp and x:
            if comp in ["gt", "lt", "gte", "lte"]:
                filter_arg = f"mask_count__{comp}"
                queryset = queryset.filter(**{filter_arg: x})
            else:
                raise ValidationError({"error": "Invalid condition. Use 'gt', 'lt', 'gte' or 'lte' followed by a number."})

        return queryset


        
