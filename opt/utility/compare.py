import requests
import json
import environ

env = environ.Env()
url = "https://api.enphaseenergy.com/api/v2/systems/2140366/stats?start_at={}&end_at={}&key=f2af1b02da727c9f4f06bf4a80e2f3ba&user_id=4d6a49784f446b784d413d3d0a"
headers = {'content-type' : 'application/json'}

def get_data(start_time):
    end_time = start_time + 86400
    response = requests.get(url.format(start_time, end_time), headers=headers)
    response = response.json()

    arr = [0]*96
    for data in response['intervals']:
        index = int((data['end_at']-start_time)/900)
        arr[index] += data['enwh']

    return arr

if __name__ == "__main__":
    start_time = 1644393600
    actual_generated = get_data(start_time)