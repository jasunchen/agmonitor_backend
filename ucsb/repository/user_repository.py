from ucsb.models import user, user_asset
from rest_framework.response import Response
from django.forms.models import model_to_dict
from rest_framework.decorators import api_view
from ucsb.repository.helpers import *
from opt.optimization import *
from opt.base_load import *
from opt.utility.solar import *
from opt.utility.weather import *
# from ucsb.repository.helpers import *
import smtplib, ssl


@api_view(['POST', 'DELETE'])
def update_user(request):
    if request.method == 'POST':

        params = ["email", "low_limit", "max_limit", "battery_size", "cost_or_shutoff", "hours_of_power", "longitude", "latitude"]
    
        #Check for Required Fields
        for p in params:
            if request.data.get(p, None) == None:
                return Response(
                    {"message": "Missing Required Parameters: {}".format(p)}, 
                    status = 400)

        #Check for Invalid Parameters
        if verify(request.data, params): 
            return Response(
                {"message": "Request has invalid parameter not in {}".format(params)}, 
                status = 400)

        email = request.data.get('email')
        low_limit = request.data.get('low_limit')
        max_limit = request.data.get('max_limit')
        battery_size = request.data.get('battery_size')
        cost_or_shutoff = request.data.get('cost_or_shutoff')
        hours_of_power = request.data.get('hours_of_power')
        longitude = request.data.get('longitude')
        latitude = request.data.get('latitude')

        tmp_user = user.objects.get(user_email=email)
        tmp_user.low_limit = low_limit
        tmp_user.max_limit = max_limit
        tmp_user.battery_size = battery_size
        tmp_user.cost_or_shutoff = cost_or_shutoff
        tmp_user.hours_of_power = hours_of_power
        tmp_user.longitude = longitude
        tmp_user.latitude = latitude
        tmp_user.save()
        return Response({"detail": "User updated successfully"}, status=200)
    elif request.method == 'DELETE':
        email = request.data.get('email')
        if email == '':
            return Response({"detail": "Email cannot be empty"}, status=400)
        tmp_user = user.objects.get(user_email=email)
        tmp_user.delete()
        return Response({"detail": "User deleted successfully"})
    else:
        return Response({"detail": "Error: Invalid request"}, status=400)



#test function
@api_view(['GET'])
def getAllUsers(request):
    res = []
    result = user.objects.all()
    for r in result:
        res.append(model_to_dict(r))
    return Response(res)

@api_view(['GET'])
def get_user(request):
    params = ["email"]
    #Check for Required Fields
    for p in params:
        if request.query_params.get(p, None) == None:
            return Response(
                {"message": "Missing Required Parameters: {}".format(p)}, 
                status = 400)

    #Check for Invalid Parameters
    if verify(request.query_params, params): 
        return Response(
            {"message": "Request has invalid parameter not in {}".format(params)}, 
            status = 400)

    email = request.query_params.get('email')
    tmp_user = user.objects.get(user_email=email)
    return Response(model_to_dict(tmp_user))

@api_view(['POST'])
def register_user(request):
    if request.method == 'POST':
        email = request.data.get('email')
        if email == '':
            return Response({"detail": "Email cannot be empty"}, status=400)
        try:
            a_user = user.objects.get(user_email=email)
            return Response({"detail": "User has already registered"})
        except (user.DoesNotExist, user.MultipleObjectsReturned):
           tmp_user = user(user_email=email)
           tmp_user.save()
           return Response({"detail": "User created successfully"}, status=200)
    else:
        return Response({"detail": "Error: Invalid request"}, status=400)


@api_view(['POST'])
def optimization(request):
    params = ["email"]
    #Check for Required Fields
    for p in params:
        if request.data.get(p, None) == None:
            return Response(
                {"message": "Missing Required Parameters: {}".format(p)}, 
                status = 400)

    #Check for Invalid Parameters
    if verify(request.data, params): 
        return Response(
            {"message": "Request has invalid parameter not in {}".format(params)}, 
            status = 400)

    email = request.data.get('email')
    tmp_user = user.objects.get(user_email=email)
    generation_assets = user_asset.objects.filter(user=tmp_user, type_of_asset='generation')

    low_limit = tmp_user.low_limit
    max_limit = tmp_user.max_limit
    battery_size = tmp_user.battery_size
    cost_or_shutoff = tmp_user.cost_or_shutoff
    hours_of_power = tmp_user.hours_of_power
    longitude = tmp_user.longitude
    latitude = tmp_user.latitude
    alert = get_alerts(latitude, longitude)
    risk = calculate_shutOffRisk(alert)
    solar = []
    for i in range(0, 2866, 15):
        solar.append([i, 0])
    for gen in generation_assets:
        declination = gen.declination
        azimuth = gen.azimuth
        modules_power = gen.modules_power
        data = getSolarData(latitude, longitude, declination, azimuth, modules_power)[1]
        # print(data)
        # data = json.loads(data)
        for i in range(192):
            solar[i][1] += data[i][1]
    base_load = calculate_base_load(tmp_user, 0, 100000000000000000)
    ave_base_load = 0
    for i in range(96):
        ave_base_load += base_load[i][1]
    ave_base_load /= 96
    idealReserveThreshold = calculate_idealReserveThreshold(hours_of_power, ave_base_load, battery_size)
    base_load = base_load * 2
    weight1 = 0.7
    weight2 = 0.6
    solar_forecast = [item[1] for item in solar]
    base_forecast = [item[1] for item in base_load]
    cur_battery = 14000
    best, score = find_optimal_threshold(UserProfile(weight1, weight2, low_limit, max_limit, risk, idealReserveThreshold, solar_forecast, base_forecast, cur_battery, battery_size))
    tmp_user.pred_opt_threshold = best
    return Response({"detail": best}, status=200)
    
    
    
@api_view(['POST'])
def post_email(request):
    if request.method == 'POST':
        receiver_email = request.data.get('email')
        port = 465  # For SSL
        smtp_server = "smtp.gmail.com"
        sender_email = "yuyuanwang1999@gmail.com"
        password = "ytpuqhpomlekpeqh"
        message = """\
        Subject: Hi there

        This message is sent from Python."""

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message)
            return Response({"detail": "User send email successfully"}, status=200)
