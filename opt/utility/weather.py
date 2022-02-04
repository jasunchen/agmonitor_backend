import requests
import json

def get_alerts(latitude: float, longitude: float):
        response = requests.get('https://api.weatherbit.io/v2.0/alerts?key=e4ab5eb2ee6b4d2db1bd229c8800daf6&lat=' + str(latitude) +'&lon=' + str(longitude))
        return json.loads(response.text)['alerts']
       
if __name__ == "__main__":
    latitude = 44.5588
    longitude = -72.5778
    alerts = [[a['severity'], a['title']] for a in get_alerts(latitude, longitude)]
    print(alerts)