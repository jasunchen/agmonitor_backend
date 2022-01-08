import time
import requests
import json

from calendar import timegm

ASSET_ID =  2
FILE_NAME = "subset.csv"

file = open(FILE_NAME, "r").read()
lyst = list()

for line in file.split("\n")[1:]:
        t, consumed_energy, produced_energy = line.strip("\r").split(",")
        
        lyst.append({
                "start_time" : t,
                "interval": 15,
                "consumed_energy": float(consumed_energy),
                "produced_energy": float(produced_energy)
        })

headers = {'content-type' : 'application/json'}

for i in range(9):
        response = requests.post(
                headers=headers,
                url='https://agmonitor-pina-colada-back.herokuapp.com/createAssetData', 
                json={"id" : ASSET_ID,
                        "data" : lyst[1000*i : 1000*(i+1)]})

        print(i, response.json())