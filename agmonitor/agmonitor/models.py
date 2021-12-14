from django.contrib.auth.models import AbstractUser
from django.db.models import CharField
from django.db.models.fields import EmailField
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.db import models

class ag_user(models.Model):
    user_email = models.EmailField(max_length=100, unique=True, primary_key=True)
    
    def __str__(self):
        return self.user_email

class ag_user_asset(models.Model):
    user = models.ForeignKey(ag_user, on_delete=models.DO_NOTHING)
    description = models.TextField(max_length=254 ,blank=True)
    asset_name = models.CharField(max_length=254, blank=True)

    def __str__(self):
        return self.asset_name

class ag_asset_data(models.Model):
    start_time = models.TimeField()
    interval = models.IntegerField()
    asset_id =  models.ForeignKey(ag_user_asset, on_delete=models.DO_NOTHING)
    consumed_energy = models.FloatField()
    produced_energy = models.FloatField()

    def __str__(self):
        return self.consumed_energy