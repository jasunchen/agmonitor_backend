import requests
import json

relevantAlerts = ["Avalanche", "Snow", "Rain", "Wind", "Blizzard", "Flood", "Hurricane", "Thunderstorm", "Storm", "Tornado", "Gale"]

  
def get_alerts(latitude: float, longitude: float):
        response = requests.get('https://api.weatherbit.io/v2.0/alerts?key=e4ab5eb2ee6b4d2db1bd229c8800daf6&lat=' + str(latitude) +'&lon=' + str(longitude))
        alerts = json.loads(response.text)['alerts']
        parsedAlerts = []
        for a in alerts:
                for relevantAlert in relevantAlerts:
                        if a['title'].find(relevantAlert) != -1:
                                parsedAlerts.append([a['severity'], a['title']])
                                break
        return parsedAlerts
       
if __name__ == "__main__":
    latitude = 68.111
    longitude = 145.581
    print(get_alerts(latitude, longitude))
