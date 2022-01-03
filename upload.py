import time
import requests
import json

from calendar import timegm

ASSET_ID =  3
FILE_NAME = "fulldata.csv"

file = open(FILE_NAME, "r").read()
lyst = list()

# finished up to 5K
for line in file.split("\n")[3001:5001]:
        t, consumed_energy, produced_energy = line.strip("\r").split(",")
        
        lyst.append({
                "start_time" : t,
                "interval": 15,
                "consumed_energy": float(consumed_energy),
                "produced_energy": float(produced_energy)
        })

headers = {'content-type' : 'application/json'}

response = requests.post(
        headers=headers,
        url='http://0.0.0.0:8000/createAssetData', 
        json={"id" : ASSET_ID,
                "data" : lyst})

print(response.json())