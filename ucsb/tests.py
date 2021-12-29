from django.test import TestCase
from ucsb.models import user, user_asset, asset_data
from rest_framework.test import APIClient
import requests

class UserTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        user.objects.create(user_email="abc@ucsb.edu")
        user.objects.create(user_email="bcd@ucsb.edu")
    
    def test_user_email(self):
        response = self.client.get('/getUser')
        self.assertEqual(response.data[0]['user_email'], "abc@ucsb.edu")
        self.assertEqual(response.data[1]['user_email'], "bcd@ucsb.edu")

class user_assetTestCase(TestCase):
    def setUp(self):
        user.objects.create(user_email="abc@ucsb.edu")
        user1 = user.objects.get(user_email="abc@ucsb.edu")
        user_asset.objects.create(user=user1, description="test1", asset_name="test1")
        user_asset.objects.create(user=user1, description="test2", asset_name="test2")
    
    def test_user_email(self):
        user1 = user.objects.get(user_email="abc@ucsb.edu")
        user_asset1 = user_asset.objects.get(user=user1, asset_name="test1")
        user_asset2 = user_asset.objects.get(user=user1, asset_name="test2")
        self.assertEqual(user_asset1.asset_name, "test1")
        self.assertEqual(user_asset2.asset_name, "test2")


