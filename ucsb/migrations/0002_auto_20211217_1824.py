# Generated by Django 3.1.13 on 2021-12-18 02:24

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ucsb', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='asset_data',
            name='start_date',
            field=models.CharField(blank=True, max_length=10),
        ),
        migrations.AlterField(
            model_name='asset_data',
            name='start_time',
            field=models.TimeField(default=datetime.datetime(2021, 12, 17, 18, 24, 7, 241287)),
        ),
    ]
