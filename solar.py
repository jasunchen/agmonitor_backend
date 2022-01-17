import requests

def getSolarData(latitude: float, longitude: float, declination: float, azimuth: float, power: float):
    response = requests.get(
        headers={'content-type' : 'application/json'},
        url='https://api.forecast.solar/estimate/{}/{}/{}/{}/{}'.format(latitude, longitude, declination, azimuth, power), 
    )
    response = response.json()

    if response['message']['code'] == 0:
        return (200, [[k, v] for k, v in response['result']['watt_hours'].items()])
    else:
        return (400, response['message']['text'])

if __name__ == "__main__":
    latitude = 34.4208
    longitude = -119.6982
    declination = 0
    azimuth = 0
    power = 100
    print(getSolarData(latitude, longitude, declination, azimuth, power))