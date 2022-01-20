from django.test import TestCase
from ucsb.models import user, user_asset, asset_data
from django.forms.models import model_to_dict
from rest_framework.test import APIClient

class UserTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.client.post('/registerUser', {'email': 'test@ucsb.edu'}, format='json')
        self.client.post('/registerUser', {'email': 'bcd@ucsb.edu'}, format='json')
    
    def test_register_user_email(self):
        response = self.client.get('/getAllUsers')
        self.assertEqual(response.data[0]['user_email'], "test@ucsb.edu")
        self.assertEqual(response.data[1]['user_email'], "bcd@ucsb.edu")

class user_assetTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        user.objects.create(user_email="test@ucsb.edu")

    def test_get_user_asset(self):
        user1 = user.objects.get(user_email="test@ucsb.edu")
        user_asset.objects.create(user=user1, asset_name="test_asset", description="test", type_of_asset="base")
        response = self.client.get('/getAllAssets?email=test@ucsb.edu')
        self.assertEqual(response.data['base'][0]['asset_name'], "test_asset")
        self.assertEqual(response.data['base'][0]['description'], "test")
    
    def test_add_user_asset(self):
        self.client.post('/addUserAsset', {'email': 'test@ucsb.edu', 'name': 'test_asset', 'description': 'test', 'type_of_asset': 'base'}, format='json')
        response = self.client.get('/getAllAssets?email=test@ucsb.edu')
        self.assertEqual(response.data['base'][0]['asset_name'], "test_asset")
        self.assertEqual(response.data['base'][0]['description'], "test")
    
    def test_delete_user_asset(self):
        user1 = user.objects.get(user_email="test@ucsb.edu")
        user_asset.objects.create(user=user1, asset_name="test_asset", description="test", type_of_asset='base')
        response = self.client.get('/getAllAssets?email=test@ucsb.edu')
        self.client.delete('/deleteUserAsset', {'id' : response.data['base'][0]['id']}, format='json')
        response = self.client.get('/getAllAssets?email=test@ucsb.edu')
        self.assertEqual(len(response.data['base']), 0)

    def test_update_user_asset(self):
        user1 = user.objects.get(user_email="test@ucsb.edu")
        user_asset.objects.create(user=user1, asset_name="test_asset", description="test")
        res = self.client.get('/getAllAssets?email=test@ucsb.edu')
        response = self.client.post('/updateUserAsset', {'id': res.data['base'][0]['id'], 'name': 'test_asset_updated', 'description': 'test_updated', 'type_of_asset': 'base'}, format='json')
        response = self.client.get('/getAllAssets?email=test@ucsb.edu')
        self.assertEqual(response.data['base'][0]['asset_name'], "test_asset_updated")
        self.assertEqual(response.data['base'][0]['description'], "test_updated")
    

class asset_dataTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        user.objects.create(user_email="test@ucsb.edu")
        user1 = user.objects.get(user_email="test@ucsb.edu")
        user_asset.objects.create(user=user1, asset_name="test_asset_data", description="test")
        res = self.client.get('/getAllAssets?email=test@ucsb.edu')
        self.id = res.data['base'][0]['id']

    def test_get_asset_data(self):
        asset = user_asset.objects.get(asset_name="test_asset_data")
        asset_data.objects.create(asset_id=asset, start_time=175049, interval=1, consumed_energy=0.0, produced_energy=0.0)
        response = self.client.get('/getAssetData?id={}&start={}&end={}&page={}'.format(self.id, 0, 9999999, 1))
        self.assertEqual(response.data['data'][0]['start_time'], 175049)
        self.assertEqual(response.data['data'][0]['interval'], 1)
        self.assertEqual(response.data['data'][0]['consumed_energy'], 0.0)
        self.assertEqual(response.data['data'][0]['produced_energy'], 0.0)
        self.assertEqual(response.data['has_previous'], False)
        self.assertEqual(response.data['has_next'], False)

    def test_add_asset_data(self):
        body = {
                "id": self.id,
                "data": [{
                    "start_time": "01/01/2020 16:30",
                    "interval": 15,
                    "consumed_energy": 1.00,
                    "produced_energy": 0.15
                }]
            }
        self.client.post('/createAssetData', body, format='json')
        response = self.client.get('/getAssetData?id={}&start={}&end={}&page={}'.format(self.id, 0, 1577896299, 1))
        self.assertEqual(response.data['data'][0]['start_time'], 1577896200)
        self.assertEqual(response.data['data'][0]['interval'], 15)
        self.assertEqual(response.data['data'][0]['consumed_energy'], 1.00)
        self.assertEqual(response.data['data'][0]['produced_energy'], 0.15)
    
    def test_delete_asset_data(self):
        asset = user_asset.objects.get(asset_name="test_asset_data")
        asset_data.objects.create(asset_id=asset, start_time=175049, interval=1, consumed_energy=0.0, produced_energy=0.0)
        response = self.client.delete('/deleteAssetData', {'id' : self.id }, format='json')
        response = self.client.get('/getAssetData?id={}&start={}&end={}&page={}'.format(self.id, 0, 9999999, 1))
        self.assertEqual(len(response.data['data']), 0)

    


