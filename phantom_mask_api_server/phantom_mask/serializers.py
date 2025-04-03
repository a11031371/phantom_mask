from rest_framework import serializers
from .models import Pharmacies, Masks, PharmacyMasks, Transactions, Users

class PharmaciesNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pharmacies
        fields = ['name']

class MaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Masks
        fields = '__all__'

class PharmacyMasksSerializer(serializers.ModelSerializer):
    model = serializers.CharField(source='mask.model', read_only=True)
    color = serializers.CharField(source='mask.color', read_only=True)
    num_per_pack = serializers.IntegerField(source='mask.num_per_pack', read_only=True)
    pharmacy_name = serializers.CharField(source='pharmacies.name', read_only=True)
    mask_name = serializers.CharField(source='mask.name', read_only=True)

    class Meta:
        model = PharmacyMasks
        fields = ['pharmacy_name', 'mask_name', 'model', 'color', 'num_per_pack', 'price']

class TransactionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transactions
        fields = '__all__'

class UsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = '__all__'