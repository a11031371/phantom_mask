from datetime import datetime
from rest_framework.exceptions import ValidationError
from django.db.models import Q, F
from ..models import Pharmacies

class PharmacyQueryService:
    """
    This class is responsible for querying pharmacy data.
    """

    def filter_by_day_and_time(queryset, day, time):
        """ Filters the queryset based on the provided day and time.
        Args:
            queryset: The queryset to filter.
            day: The day of the week (e.g., 'mon', 'tue', etc.).
            time: The time in HH:MM format (24-hour format).

        Returns:
            A filtered queryset based on the provided day and time.
        """
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

            return queryset.filter(standard_case | cross_day_case)
        
    def filter_by_price_range(queryset, min_price, max_price):
        """ Filters the queryset based on the provided price range.

        Args:
            queryset: The queryset to filter.
            min_price: The minimum price.
            max_price: The maximum price.

        Returns:
            A filtered queryset based on the provided price range.
        """
        if min_price < 0 or max_price < 0:
            raise ValidationError({"error": "Price values must be non-negative."})
        
        queryset = Pharmacies.objects.filter( # filter by price range
            pharmacy_masks__price__gte=min_price,
            pharmacy_masks__price__lte=max_price
        )

        return queryset
    
    def filter_by_mask_count(queryset, comp, x):
        """ Filters the queryset based on the provided mask count condition.
        
        Args:
            queryset: The queryset to filter.
            comp: The comparison operator ('gt', 'lt', 'gte', 'lte').
            x: The value to compare against.

        """

        if comp in ["gt", "lt", "gte", "lte"]:
            filter_arg = f"mask_count__{comp}"
            queryset = queryset.filter(**{filter_arg: x})
        else:
            raise ValidationError({"error": "Invalid condition. Use 'gt', 'lt', 'gte' or 'lte' followed by a number."})
        
        return queryset
    
    def get_pharmacy_masks(queryset, pharmacy_name, sort_by):
        """
        Retrieves masks available at a specific pharmacy, optionally sorted by name or price.

        Args:
            queryset: The queryset to filter.
            pharmacy_name: The name of the pharmacy.
            sort_by: The field to sort by ('name' or 'price').
        
        Returns:
            A filtered queryset of masks available at the specified pharmacy.
        """
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
        