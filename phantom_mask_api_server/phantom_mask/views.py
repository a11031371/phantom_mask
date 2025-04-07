from django.shortcuts import render
from rest_framework import generics, views
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from .models import Pharmacies, Masks, PharmacyMasks, Transactions, Users
from django.db.models import Count, Sum
from django.db.models.functions import Round
from django.db import transaction
from . import serializers
from datetime import datetime
from django.utils.timezone import now
import re
from .utils.StringRelevance import StringRelevance as sr
from .services.PharmacyQueryService import PharmacyQueryService
from .services.UserQueryService import UserQueryService

class APIRootView(views.APIView):
    """ API root view. """

    def get(self, request):
        """
        Returns a welcome message.
        """
        data = {
            "message": "Welcome to the Phantom Mask API.",
        }
        return Response(data)

class PharmacyOpenListView(generics.ListAPIView):
    """ List all pharmacies that are open at a given time on a given day. """

    serializer_class = serializers.PharmaciesNameSerializer
    
    def get_queryset(self):
        """
        query parameters:
            day: day of the week (mon, tue, wed, thu, fri, sat, sun).
            time: time in HH:MM (24-hour format).
        """
        # get query parameters
        day = self.request.query_params.get("day")
        time = self.request.query_params.get("time")

        if not day or not time:
            raise ValidationError({"error": "Both day and time parameters are required."})

        queryset = Pharmacies.objects.all()
        
        try:
            queryset = PharmacyQueryService.filter_by_day_and_time(queryset, day, time)
        except ValueError as e:
            raise ValidationError({"error": str(e)})
        
        return queryset
    
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

        # get query parameters
        pharmacy_name = self.request.query_params.get("pharmacy")
        sort_by = self.request.query_params.get("sort_by")
        
        try:
            queryset = PharmacyQueryService.get_pharmacy_masks(queryset, pharmacy_name, sort_by)
        except ValueError as e:
            raise ValidationError({"error": str(e)})

        return queryset
    
class PharmaciesCompareMaskListView(generics.ListAPIView):
    """ List all pharmacies with more or less than x mask products within a price range. """

    serializer_class = serializers.PharmaciesMaskCountSerializer

    def get_queryset(self):
        """
        query parameters:
            min: minimum price of the masks.
            max: maximum price of the masks.
            cond: comparison operator + number (e.g., 'gt5', 'lt10').
        """
        queryset = Pharmacies.objects.all()

        # get query parameters
        min_price = self.request.query_params.get("min")
        max_price = self.request.query_params.get("max")
        cond = self.request.query_params.get("cond")
        r = re.match(r"([A-Za-z]+)(\d+)", cond)
        comp, x = r.groups() if r else (None, None)

        min_price = float(min_price) if min_price else 0.0
        max_price = float(max_price) if max_price else float("inf")

        try:
            # query the number of masks in the price range
            queryset = PharmacyQueryService.filter_by_price_range(
                queryset, min_price, max_price
            ).annotate( # join with pharmacy_masks table
                mask_count=Count("pharmacy_masks__mask", distinct=True)
            ).all()

            if comp and x:
                # filter by condition
                queryset = PharmacyQueryService.filter_by_mask_count(queryset, comp, int(x))
            elif comp and not x or not comp and x:
                raise ValidationError({"error": "Both condition and number must be provided."})
            
        except ValueError as e:
            raise ValidationError({"error": str(e)})

        return queryset

class ActiveTransactionsUserListView(generics.ListAPIView):
    """ List the top x users by total transaction amount of masks within a date range. """
    
    serializer_class = serializers.TransactionsUserSerializer
    
    def get_queryset(self):
        """
        query parameters:
            start: start date (YYYY-MM-DD).
            end: end date (YYYY-MM-DD).
            x: number of users to return.
        """
        queryset = Users.objects.all()

        # get query parameters
        start_date = self.request.query_params.get("start")
        end_date = self.request.query_params.get("end")
        x = self.request.query_params.get("x")

        try:
            # Get the top x users by total transaction amount within the date range
            queryset = UserQueryService.filter_by_date_range(
                queryset, start_date, end_date
            ).annotate( # join with transactions table
                total_transaction_amount=Round(Sum("transactions__transaction_amount"), 2)  
            ).order_by( # descending order
                "-total_transaction_amount"
            )
            
            # limit the number of users returned
            queryset = UserQueryService.limit(queryset, int(x)) if x else queryset
        except ValueError as e:
            raise ValidationError({"error": str(e)})

        return queryset
    
class MaskTransactionsView(views.APIView):
    """ Find the total number of masks and dollar value of transactions within a date range. """
        
    serializer_class = serializers.TransactionsAmountSerializer
    
    def get(self, request):
        """
        query parameters:
            start: start date (YYYY-MM-DD).
            end: end date (YYYY-MM-DD).
        """
        # get query parameters
        start_date = request.query_params.get("start")
        end_date = request.query_params.get("end")

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

        return Response(queryset)
    
class SearchView(views.APIView):
    """ Search for pharmacies or masks by name, ranked by relevance to the search term. """

    # define the search models
    search_models = {
        "pharmacy": {
            "model": Pharmacies,
            "serializer": serializers.PharmaciesNameSerializer,
            "compared_field": "name"
        },
        "mask": {
            "model": Masks,
            "serializer": serializers.MasksNameSerializer,
            "compared_field": "model"
        }
    }

    def get(self, request):
        """
        query parameters:
            type: type of search (pharmacy or mask).
            q: search term.
        """
        search_type = request.query_params.get("type")
        search_term = request.query_params.get("q")

        search_term = search_term.strip().lower() if search_term else ""
        

        # validate search type
        if search_type not in self.search_models:
            return Response({"error": "Invalid search type. Use 'pharmacy' or 'mask'."})

        # calculate relevance for each object in the model
        results = []
        for obj in self.search_models[search_type]["model"].objects.all():
            # get the compared field value
            compared_field_value = getattr(obj, self.search_models[search_type]["compared_field"])
            # calculate relevance using StringRelevance class
            relevance = sr(search_term, compared_field_value).get_relevance()
            # append the result to the list if not existing
            results.append({
                "name": compared_field_value,
                "relevance": relevance
            })

        # distinct results
        results = {result["name"]: result for result in results}.values()
        

        # sort results by relevance
        results = sorted(results, key=lambda x: x["relevance"])

        serializer_class = self.search_models[search_type]["serializer"]
        serializer = serializer_class(results, many=True)
    
        return Response(serializer.data)

class PurchaseMaskView(views.APIView):
    """ Purchase a mask from a pharmacy. """
    
    def post(self, request):
        serializer = serializers.PurchaseMasksSerializer(data=request.data)
        if not serializer.is_valid():
            raise ValidationError(serializer.errors)

        data = serializer.validated_data

        try:
            with transaction.atomic():
                # get the pharmacy, mask, and user objects
                pharmacy = Pharmacies.objects.get(id=data["pharmacy_id"])
                mask = Masks.objects.get(id=data["mask_id"])
                user = Users.objects.get(id=data["user_id"])
                pharmacy_mask = PharmacyMasks.objects.get(pharmacy=pharmacy, mask=mask)

                # calculate total cost
                total_cost = round(pharmacy_mask.price * data["quantity"], 2)

                # check if the cash balance of the user is enough
                if user.cash_balance < total_cost:
                    raise ValidationError({"error": "User does not have enough balance."})

                # update the cash balance of the user and pharmacy
                user.cash_balance -= total_cost
                pharmacy.cash_balance += total_cost
                user.save()
                pharmacy.save()

                # create a transaction record
                Transactions.objects.create(
                    user=user,
                    pharmacy=pharmacy,
                    mask=mask,
                    transaction_amount=total_cost,
                    transaction_date=now().replace(microsecond=0)
                )

                # return the response
                return Response({
                    "message": "Thank you! Have a nice day!",
                    "user": user.name,
                    "pharmacy": pharmacy.name,
                    "mask": mask.name,
                    "quantity": data["quantity"],
                    "total_cost": total_cost,
                    "transaction_date": now().replace(microsecond=0)
                })
            
        # handle exceptions
        except Pharmacies.DoesNotExist:
            return Response({"error": "Pharmacy not found."}, status=404)
        except Masks.DoesNotExist:
            return Response({"error": "Mask not found."}, status=404)
        except Users.DoesNotExist:
            return Response({"error": "User not found."}, status=404)
        except PharmacyMasks.DoesNotExist:
            return Response({"error": "Pharmacy does not sell this mask."}, status=400)
        except ValidationError as e:
            return Response(e.detail, status=400)
        except Exception as e:
            import traceback
            traceback.print_exc()  # Print the stack trace for debugging
            return Response({"error": str(e)}, status=500)

class CancelLatestTransactionView(views.APIView):
    """ Cancel the latest transaction. """

    # (Simply delete a record. Needs to be refactored in a more robust way for production.)
    def post(self, request):
        """
        API to cancel the latest transaction.
        It will revert the transaction and restore user and pharmacy balance.
        """
        try:
            # get the latest transaction
            latest_transaction = Transactions.objects.order_by('-transaction_date').first()

            if not latest_transaction:
                raise ValidationError("No transactions found.")

            # Ensure this is a valid transaction for cancellation (e.g., not already cancelled)

            user = latest_transaction.user
            pharmacy = latest_transaction.pharmacy
            mask = latest_transaction.mask
            total_cost = latest_transaction.transaction_amount

            with transaction.atomic():
                # Revert user balance
                user.cash_balance += total_cost
                user.save()

                # Revert pharmacy balance
                pharmacy.cash_balance -= total_cost
                pharmacy.save()

                # Delete the transaction record
                latest_transaction.delete()

            # Return the success response with details
            response_data = {
                "message": "The latest transaction has been successfully canceled.",
                "user": user.name,
                "pharmacy": pharmacy.name,
                "mask": mask.name,
                "transaction_amount": total_cost,
            }
            return Response(response_data, status=200)

        except Exception as e:
            return Response({"error": str(e)}, status=500)