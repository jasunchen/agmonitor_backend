import requests
import json
import environ
import numpy as np

env = environ.Env()

apikey = env('ENPHASEKEY')
userid = env('ENPHASEUSERID')
url = "https://api.enphaseenergy.com/api/v2/systems/2140366/stats?start_at={}&end_at={}&key={}&user_id={}"
headers = {'content-type' : 'application/json'}

def get_data(start_time):
    end_time = start_time + 86400
    response = requests.get(url.format(start_time, end_time, apikey, userid), headers=headers)
    response = response.json()

    arr = [0]*96
    for data in response['intervals']:
        index = int((data['end_at']-start_time)/900)
        arr[index] += data['enwh']

    return arr

#should truncate the predicted array to 96 (first 96 predicted values)
def linear_fit(real, predicted):
    real_0, pred_0 = real[0], predicted[0]
    real_max = max(real)
    pred_max = max(predicted)
    m = (pred_max-pred_0)/(real_max-real_0)
    b = pred_0 - m * real_0
    return m, b

#length of predicted does not matter
def apply_fit(m,b, predicted):
    return [(i - b)/m for i in predicted]

if __name__ == "__main__":
    start_time = 1644220800 #call here first
    results = []
    for i in range(8):
        gen = get_data(start_time + i*86400)
        results = results + (gen)
    print(results)
    # actual_generated = get_data(start_time)
    # print(actual_generated)
    #print(len(actual_generated))
    #print(linear_fit(actual_generated, [0]*96))
    #print(linear_fit([0,1], [0,1]))