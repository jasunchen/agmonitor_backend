from rest_framework.response import Response
from django.forms.models import model_to_dict
from rest_framework.decorators import api_view
import requests
import json

@api_view(['POST'])
def get_alerts(request):
    if request.method == 'POST':
        lat = request.data.get('lat')
        lon = request.data.get('lon')
        if lat == '':
            return Response({"detail": "lat cannot be empty"}, status=400)
        if lon == '':
            return Response({"detail": "lon cannot be empty"}, status=400)
        response = requests.get('https://api.weatherbit.io/v2.0/alerts?key=e4ab5eb2ee6b4d2db1bd229c8800daf6&lat=' + str(lat) +'&lon=' + str(lon))
        weather = json.loads(response.text)
        # alerts = []
        # for alert in weather['alerts']:
        #     alerts.append(alert['severity'])
        # weather['alerts'] = alerts
        return Response({"detail": weather}, status=200)
    else:
        return Response({"detail": "Error: Invalid request"}, status=400)
