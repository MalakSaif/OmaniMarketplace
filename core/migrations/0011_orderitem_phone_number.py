# Generated by Django 5.2 on 2025-05-28 06:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_order_total_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderitem',
            name='phone_number',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
