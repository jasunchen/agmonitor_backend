import requests
import json

def get_alerts(latitude: float, longitude: float):
        response = requests.get('https://api.weatherbit.io/v2.0/alerts?key=e4ab5eb2ee6b4d2db1bd229c8800daf6&lat=' + str(latitude) +'&lon=' + str(longitude))
        weather = json.loads(response.text)
        alerts = []
        for alert in weather['alerts']:
             alerts.append([alert['severity'], alert['title']])
        
        print(alerts)

        return weather['alerts']

if __name__ == "__main__":
    latitude = 34.4208
    longitude = -119.6982
    print(get_alerts(latitude, longitude))