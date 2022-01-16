from django.db import models
from datetime import datetime

class user(models.Model):
    user_email = models.EmailField(max_length=100, unique=True, primary_key=True)
    low_limit = models.IntegerField(default=0)
    max_limit = models.IntegerField(default=100)
    battery_size = models.IntegerField(default=0)
    cost_or_shutoff = models.IntegerField(default=50)
    hours_of_power = models.IntegerField(default=0)
    longitude = models.FloatField(default=34.4208)
    latitude = models.FloatField(default=-119.6982)

    def __str__(self):
        return self.user_email

class user_asset(models.Model):
    user = models.ForeignKey(user, on_delete=models.DO_NOTHING)
    description = models.TextField(max_length=254 ,blank=True)
    asset_name = models.CharField(max_length=254, blank=True)
    declination = models.FloatField(default=0 ,blank=True)
    azimuth = models.FloatField(default=0 ,blank=True)
    modules_power = models.FloatField(default=0 ,blank=True)
    is_generation = models.BooleanField(default=False)

    def __str__(self):
        return self.asset_name

class asset_data(models.Model):
    start_time = models.BigIntegerField(default=0)
    interval = models.IntegerField()
    asset_id =  models.ForeignKey(user_asset, on_delete=models.DO_NOTHING)
    consumed_energy = models.FloatField()
    produced_energy = models.FloatField()

    def __str__(self):
        return self.asset_id + self.start_time
