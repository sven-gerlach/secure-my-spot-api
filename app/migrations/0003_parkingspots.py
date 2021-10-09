# Generated by Django 3.2.7 on 2021-10-09 04:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_alter_user_email'),
    ]

    operations = [
        migrations.CreateModel(
            name='ParkingSpots',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('latitude', models.DecimalField(decimal_places=6, help_text='GPS latitude bounded by [-90,90] and with 6 decimal places', max_digits=9)),
                ('longitude', models.DecimalField(decimal_places=6, help_text='GPS longitude bounded by (-180, 180] with 6 decimal places', max_digits=9)),
                ('reserved', models.BooleanField(default=False, help_text='Specifies if the parking spot is already reserved')),
                ('rate', models.DecimalField(decimal_places=2, help_text='hourly rate in USD', max_digits=5)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
