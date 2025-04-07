from datetime import datetime
from rest_framework.exceptions import ValidationError
from ..models import Users

class UserQueryService:
    """
    Service for querying user information.
    """

    def filter_by_date_range(queryset, start_date, end_date):
        """
        Filters the queryset based on the provided date range.

        Args:
            queryset: The queryset to filter.
            start_date: The start date in YYYY-MM-DD format.
            end_date: The end date in YYYY-MM-DD format.

        Returns:
            A filtered queryset based on the provided date range.
        """

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
        
        # filter the queryset based on the date range
        queryset = Users.objects.filter(
            transactions__transaction_date__date__gte=start_date,
            transactions__transaction_date__date__lte=end_date
        )

        return queryset
    
    def limit(queryset, limit):
        """
        Limits the queryset to the specified number of results.

        Args:
            queryset: The queryset to limit.
            limit: The maximum number of results to return.

        Returns:
            A limited queryset based on the provided limit.
        """
        if limit <= 0:
            raise ValidationError({"error": "Limit must be a positive integer."})
        
        return queryset[:limit]