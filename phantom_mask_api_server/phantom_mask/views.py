from django.shortcuts import render
from rest_framework import generics
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from .models import Pharmacies, Masks, PharmacyMasks, Transactions, Users
from django.db.models import Q, F, Count, Sum
from django.db.models.functions import Round
from . import serializers
from datetime import datetime
import re

class PharmacyOpenListView(generics.ListAPIView):
    """ List all pharmacies that are open at a given time on a given day. """

    serializer_class = serializers.PharmaciesNameSerializer
    
    def get_queryset(self):
        """
        query parameters:
            day: day of the week (mon, tue, wed, thu, fri, sat, sun).
            time: time in HH:MM (24-hour format).
        """
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
    
class PharmacyMasksListView(generics.ListAPIView):
    """ List all masks sold by a given pharmacy, sorted by mask name or price."""
    serializer_class = serializers.PharmacyMasksSerializer

    def get_queryset(self):
        """
        query parameters:
            pharmacy: name of the pharmacy.
            sort_by: 'name' or 'price'.
        """
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
    
class PharmaciesCompareMaskListView(generics.ListAPIView):
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

        # query the number of masks in the price range
        queryset = Pharmacies.objects.filter( # filter by price range
            pharmacy_masks__price__gte=min_price,
            pharmacy_masks__price__lte=max_price
        ).annotate( # join with pharmacy_masks table
            mask_count=Count("pharmacy_masks__mask", distinct=True)
        ).all()

        # filter by condition
        if comp and x:
            if comp in ["gt", "lt", "gte", "lte"]:
                filter_arg = f"mask_count__{comp}"
                queryset = queryset.filter(**{filter_arg: x})
            else:
                raise ValidationError({"error": "Invalid condition. Use 'gt', 'lt', 'gte' or 'lte' followed by a number."})

        return queryset

class FrequentTransactionsUserListView(generics.ListAPIView):
    """ List the top x users by total transaction amount of masks within a date range."""
    
    serializer_class = serializers.TransactionsUserSerializer
    
    def get_queryset(self):
        """
        query parameters:
            start: start date (YYYY-MM-DD).
            end: end date (YYYY-MM-DD).
            x: number of users to return.
        """
        # Get query parameters
        start_date = self.request.query_params.get("start")
        end_date = self.request.query_params.get("end")
        x = self.request.query_params.get("x")

        # validate date format and range
        if start_date and end_date:
            try:
                start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
                end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
            except ValueError:
                raise ValidationError({"error": "Invalid date format. Please use YYYY-MM-DD."})
            
            if start_date > end_date:
                raise ValidationError({"error": "Start date must be before end date."})
        
        else:
            raise ValidationError({"error": "Please provide both start and end dates."})

        # Get the top x users by total transaction amount within the date range
        queryset = Users.objects.filter( # filter by date range
            transactions__transaction_date__date__gte=start_date,
            transactions__transaction_date__date__lte=end_date
        ).annotate( # join with transactions table
            total_transaction_amount=Round(Sum("transactions__transaction_amount"), 2)  
        ).order_by( # descending order
            "-total_transaction_amount"
        ) 
        
        # limit the number of users returned
        if x:
            try:
                x = int(x)
                queryset = queryset[:x]
            except ValueError:
                raise ValidationError({"error": "Invalid value for x. Please provide an non-negative integer."})

        return queryset
    
class MaskTransactionsListView(generics.ListAPIView):
    """ Find the total number of masks and dollar value of transactions within a date range."""
        
    serializer_class = serializers.TransactionsAmountSerializer
    
    def get_queryset(self):
        """
        query parameters:
            start: start date (YYYY-MM-DD).
            end: end date (YYYY-MM-DD).
        """
        # Get query parameters
        start_date = self.request.query_params.get("start")
        end_date = self.request.query_params.get("end")

        filters = {}

        # validate start_date
        if start_date:
            try:
                start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
                filters["transaction_date__date__gte"] = start_date
            except ValueError:
                raise ValidationError({"error": "Invalid start date format. Use YYYY-MM-DD."})

        # validate end_date
        if end_date:
            try:
                end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
                filters["transaction_date__date__lte"] = end_date
            except ValueError:
                raise ValidationError({"error": "Invalid end date format. Use YYYY-MM-DD."})

        queryset = Transactions.objects.filter(**filters).aggregate(
            total_transaction_amount=Round(Sum("transaction_amount"), 2),
            total_mask_product_count=Count("id"),
            total_mask_count=Sum("mask__num_per_pack")
        )

        return [queryset]

        
