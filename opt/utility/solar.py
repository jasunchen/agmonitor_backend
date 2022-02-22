import requests
from datetime import datetime
import environ

env = environ.Env()


def convertTime(s):
    return int((datetime.strptime(s, '%Y-%m-%d %H:%M:%S') - datetime(1970, 1, 1)).total_seconds())


def getSolarData(latitude: float, longitude: float, declination: float, azimuth: float, power: float):
    solar_api_key = env('SOLARAPIKEY')
    #solar_api_key = ''
    response = requests.get(
        headers={'content-type': 'application/json'},
        url='https://api.forecast.solar/{}/estimate/{}/{}/{}/{}/{}'.format(
            solar_api_key, latitude, longitude, declination, azimuth, power),
        verify=False
    )
    response = response.json()

    if response['message']['code'] == 0:
        result = [[15 * t, 0] for t in range(672)]
        data = [[convertTime(k), v / 1000] for k, v in response['result']['watt_hours'].items()]

        # offset for days
        offset = 86400 * (data[0][0] % 604800 // 86400)
        previousIndex = 0
        previousValue = 0

        for t, v in data:
            # calculate index of result array
            index = int((t - offset) % 604800 / 60 // 15)

            # calculate energy generated
            energyGenerated = max(0, v - previousValue)

            # calculate energy generated between index and previousIndex
            # assume energy generated equally through time period (this is not great, but workable)
            if previousIndex == index:
                result[index][1] += energyGenerated
            elif previousIndex < index:
                for i in range(previousIndex, index):
                    result[i][1] += energyGenerated / (index - previousIndex)

            previousValue = v
            previousIndex = index

        return (200, result)
    else:
        return (400, response['message']['text'])


if __name__ == "__main__":
    latitude = 34.463829
    longitude = -119.740647
    declination = 0.0
    azimuth = 180.0
    power = 3000.0
    # print(getSolarData(latitude, longitude, declination, azimuth, power))
    solar = []
    for i in range(0, 2866, 15):
        solar.append([i, 0])
    data = getSolarData(latitude, longitude, declination, azimuth, power)
    print(data)
