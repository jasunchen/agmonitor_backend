import requests
import json
import environ

env = environ.Env()
relevantAlerts = ["Avalanche", "Snow", "Rain", "Wind", "Blizzard", "Flood", "Hurricane", "Thunderstorm", "Storm", "Tornado", "Gale"] #just storm alerts
 
  
def get_alerts(latitude: float, longitude: float):      
        weather_api_key = env('WEATHERAPIKEY')
        response = requests.get('https://api.weatherbit.io/v2.0/alerts?key={}&lat={}&lon={}'.format(weather_api_key, str(latitude), str(longitude)))
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
