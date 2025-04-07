from django.db import models
class Masks(models.Model):
    model = models.TextField()
    color = models.TextField()
    num_per_pack = models.IntegerField()
    name = models.TextField(unique=True)

    class Meta:
        managed = False
        db_table = 'masks'

class Pharmacies(models.Model):
    name = models.TextField(unique=True)
    cash_balance = models.FloatField()
    mon_open = models.TextField(blank=True, null=True)
    mon_close = models.TextField(blank=True, null=True)
    tue_open = models.TextField(blank=True, null=True)
    tue_close = models.TextField(blank=True, null=True)
    wed_open = models.TextField(blank=True, null=True)
    wed_close = models.TextField(blank=True, null=True)
    thu_open = models.TextField(blank=True, null=True)
    thu_close = models.TextField(blank=True, null=True)
    fri_open = models.TextField(blank=True, null=True)
    fri_close = models.TextField(blank=True, null=True)
    sat_open = models.TextField(blank=True, null=True)
    sat_close = models.TextField(blank=True, null=True)
    sun_open = models.TextField(blank=True, null=True)
    sun_close = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'pharmacies'


class PharmacyMasks(models.Model):
    mask = models.ForeignKey(Masks, related_name="pharmacy_masks", on_delete=models.PROTECT)
    pharmacy = models.ForeignKey(Pharmacies, related_name="pharmacy_masks", on_delete=models.PROTECT)
    price = models.FloatField()

    class Meta:
        managed = False
        db_table = 'pharmacy_masks'

class Users(models.Model):
    name = models.TextField()
    cash_balance = models.FloatField()

    class Meta:
        managed = False
        db_table = 'users'
        
class Transactions(models.Model):
    user = models.ForeignKey(Users, related_name="transactions", on_delete=models.PROTECT)
    pharmacy = models.ForeignKey(Pharmacies, related_name="transactions", on_delete=models.PROTECT)
    mask = models.ForeignKey(Masks, related_name="transactions", on_delete=models.PROTECT)
    transaction_amount = models.FloatField()
    transaction_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'transactions'
