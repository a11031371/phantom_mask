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
    class Meta:
        model = PharmacyMasks
        fields = '__all__'

class TransactionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transactions
        fields = '__all__'

class UsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = '__all__'