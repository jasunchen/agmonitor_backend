# Generated by Django 3.1.13 on 2021-12-12 18:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_ag_asset_data_ag_user_asset'),
    ]

    operations = [
        migrations.AddField(
            model_name='ag_user_asset',
            name='asset_name',
            field=models.CharField(blank=True, max_length=254),
        ),
    ]
