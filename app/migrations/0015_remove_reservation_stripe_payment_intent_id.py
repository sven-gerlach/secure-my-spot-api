# Generated by Django 3.2.9 on 2022-01-26 22:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0014_reservation_stripe_setup_intent_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='reservation',
            name='stripe_payment_intent_id',
        ),
    ]
