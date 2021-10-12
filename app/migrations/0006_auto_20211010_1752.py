# Generated by Django 3.2.7 on 2021-10-10 17:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0005_rename_parkingspots_parkingspot'),
    ]

    operations = [
        migrations.AlterField(
            model_name='parkingspot',
            name='latitude',
            field=models.DecimalField(decimal_places=6, help_text='GPS latitude bounded by [-90,90] and with 6 decimals', max_digits=9),
        ),
        migrations.AlterField(
            model_name='parkingspot',
            name='longitude',
            field=models.DecimalField(decimal_places=6, help_text='GPS longitude bounded by (-180, 180] with 6 decimals', max_digits=9),
        ),
        migrations.AlterField(
            model_name='parkingspot',
            name='rate',
            field=models.DecimalField(decimal_places=2, help_text='hourly rate in USD with 2 decimals', max_digits=5),
        ),
    ]