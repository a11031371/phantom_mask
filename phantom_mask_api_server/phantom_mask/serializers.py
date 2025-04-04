from rest_framework import serializers
from .models import Pharmacies, Masks, PharmacyMasks, Transactions, Users

class PharmaciesNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pharmacies
        fields = ['name']

class MasksNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Masks
        fields = ['name']

class UsersNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ['name']

class PharmacyMasksSerializer(serializers.ModelSerializer):
    model = serializers.CharField(source='mask.model', read_only=True)
    color = serializers.CharField(source='mask.color', read_only=True)
    num_per_pack = serializers.IntegerField(source='mask.num_per_pack', read_only=True)
    pharmacy_name = serializers.CharField(source='pharmacies.name', read_only=True)
    mask_name = serializers.CharField(source='mask.name', read_only=True)

    class Meta:
        model = PharmacyMasks
        fields = ['pharmacy_name', 'mask_name', 'model', 'color', 'num_per_pack', 'price']

class PharmaciesMaskCountSerializer(serializers.ModelSerializer):
    mask_count = serializers.IntegerField()

    class Meta:
        model = Pharmacies
        fields = ["name", "mask_count"]

class TransactionsUserSerializer(serializers.ModelSerializer):
    total_transaction_amount = serializers.FloatField()
    class Meta:
        model = Users
        fields = ["name", "total_transaction_amount"]

class TransactionsAmountSerializer(serializers.ModelSerializer):
    total_transaction_amount = serializers.FloatField()
    total_mask_product_count = serializers.IntegerField()
    total_mask_count = serializers.IntegerField()

    class Meta:
        model = Transactions
        fields = ["total_transaction_amount", "total_mask_product_count", "total_mask_count"]

class PharmaciesNameRelevanceSerializer(serializers.ModelSerializer):
    relevance = serializers.FloatField()
    class Meta:
        model = Pharmacies
        fields = ['name', 'relevance']

class MasksNameRelevanceSerializer(serializers.ModelSerializer):
    relevance = serializers.FloatField()
    class Meta:
        model = Masks
        fields = ['name', 'relevance']