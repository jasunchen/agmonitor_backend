import requests
from datetime import datetime

def convertTime(s):
    return int((datetime.strptime(s, '%Y-%m-%d %H:%M:%S') - datetime(1970,1,1)).total_seconds())

def getSolarData(latitude: float, longitude: float, declination: float, azimuth: float, power: float):
    response = requests.get(
        headers={'content-type' : 'application/json'},
        url='https://api.forecast.solar/estimate/{}/{}/{}/{}/{}'.format(latitude, longitude, declination, azimuth, power), 
        verify=False
    )
    response = response.json()

    if response['message']['code'] == 0:
        result = [[15 * t, 0] for t in range(192)]
        data = [[convertTime(k), v / 1000] for k, v in response['result']['watt_hours'].items()]
        
        # offset for odd / even days
        offset = 86400 if data[0][0] % 172800 >= 86400 else 0
        previousIndex = 0
        previousValue = 0

        for t, v in data:
            # calculate index of result array
            index = int((t + offset) % 172800 / 60 // 15)

            # calculate energy generated
            energyGenerated = max(0, v - previousValue)
            
            # calculate energy generated between index and previousIndex
            # assume energy generated equally through time period (this is not great, but workable)
            for i in range(previousIndex, index):
                result[i][1] += energyGenerated / (index - previousIndex)
            
            previousValue = v
            previousIndex = index

        return (200, result)
    else:
        return (400, response['message']['text'])

if __name__ == "__main__":
    latitude = 34.4208
    longitude = -119.6982
    declination = 0
    azimuth = 0
    power = 100
    # print(getSolarData(latitude, longitude, declination, azimuth, power))
    solar = []
    for i in range(0, 2866, 15):
        solar.append([i, 0])
    data = getSolarData(latitude, longitude, declination, azimuth, power)[1]
    print(data)
