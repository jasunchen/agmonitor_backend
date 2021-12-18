from django.db import models
from datetime import datetime

class user(models.Model):
    user_email = models.EmailField(max_length=100, unique=True, primary_key=True)
    
    def __str__(self):
        return self.user_email

class user_asset(models.Model):
    user = models.ForeignKey(user, on_delete=models.DO_NOTHING)
    description = models.TextField(max_length=254 ,blank=True)
    asset_name = models.CharField(max_length=254, blank=True)

    def __str__(self):
        return self.asset_name

class asset_data(models.Model):
    start_date = models.CharField(max_length=10, blank=True)
    start_time = models.TimeField(default=datetime.now())
    interval = models.IntegerField()
    asset_id =  models.ForeignKey(user_asset, on_delete=models.DO_NOTHING)
    consumed_energy = models.FloatField()
    produced_energy = models.FloatField()

    def __str__(self):
        return self.asset_id + self.start_time
