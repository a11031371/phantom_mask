# Generated by Django 5.1.7 on 2025-04-02 16:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('phantom_mask', '0003_masks_pharmacies_pharmacymasks_transactions_users_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='masks',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='pharmacies',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='pharmacymasks',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='transactions',
            options={'managed': False},
        ),
        migrations.AlterModelOptions(
            name='users',
            options={'managed': False},
        ),
    ]
