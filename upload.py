import time
import requests
import json

from calendar import timegm

ASSET_ID =  1
FILE_NAME = "test2.csv"

file = open(FILE_NAME, "r").read()
lyst = list()

for line in file.split("\n")[1:]:
        t, consumed_energy, produced_energy = line.strip("\r").split(",")
        
        lyst.append({
                "start_time" : t,
                "interval": 15,
                "consumed_energy": consumed_energy,
                "produced_energy": produced_energy
        })

headers = {'content-type' : 'application/json'}

response = requests.post(
        headers=headers,
        url='http://0.0.0.0:8000/createAssetData', 
        json={"id" : ASSET_ID,
                "data" : lyst})

response.raise_for_status()
print(response.json())