from django.shortcuts import render
from rest_framework import generics
from .models import Pharmacies, Masks, PharmacyMasks, Transactions, Users
from django.db.models import Q, F
from .serializers import PharmaciesNameSerializer
from rest_framework.exceptions import ValidationError
from datetime import datetime

class OpenPharmaciesListCreate(generics.ListCreateAPIView):
    serializer_class = PharmaciesNameSerializer
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