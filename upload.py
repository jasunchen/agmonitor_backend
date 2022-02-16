import time
import requests
import json

from calendar import timegm

ASSET_ID = 14
FILE_NAME = "subset.csv"

file = open(FILE_NAME, "r").read()
lyst = list()

for line in file.split("\n")[1:]:
<<<<<<< HEAD
    t, consumed_energy, produced_energy = line.strip("\r").split(",")
=======
        t, consumed_energy, produced_energy = line.strip("\r").split(",")
        
        lyst.append({
                "start_time" : t,
                "interval": 15,
                "consumed_energy": float(consumed_energy),
                "produced_energy": 0.0
        })
>>>>>>> ee1aa3a228764bd0b89ed677691023e4494e0f8c

    lyst.append({
        "start_time": t,
        "interval": 15,
        "consumed_energy": float(consumed_energy),
        "produced_energy": 0.0
    })

headers = {'content-type': 'application/json'}

for i in range(9):
    response = requests.post(
        headers=headers,
        url='http://0.0.0.0:8000/createAssetData',
        json={"id": ASSET_ID,
              "data": lyst[1000*i: 1000*(i+1)]})

    print(i, response.json())
