from ucsb.models import user, user_asset
from rest_framework.response import Response
from django.forms.models import model_to_dict
from rest_framework.decorators import api_view
from ucsb.repository.helpers import *
from opt.optimization import *
from opt.base_load import *
from opt.utility.solar import *
from opt.utility.weather import *
from opt.utility.send_email import *
# from ucsb.repository.helpers import *
import smtplib, ssl

message = "Hello, this is a daily automated notification. Based on weather forecasts and historical data for tomorrow, the ideal battery reserve percentage for your battery is {}%. Please visit https://agmonitor-pina-colada.herokuapp.com/home/ for more details."

@api_view(['POST', 'DELETE'])
def update_user(request):
    if request.method == 'POST':

        params = ["email", "low_limit", "max_limit", "battery_size", "cost_or_shutoff", "hours_of_power", "longitude", "latitude", "phone_number"]
    
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
        phone_number = request.data.get('phone_number')

        tmp_user = user.objects.get(user_email=email)
        tmp_user.low_limit = low_limit
        tmp_user.max_limit = max_limit
        tmp_user.battery_size = battery_size
        tmp_user.cost_or_shutoff = cost_or_shutoff
        tmp_user.hours_of_power = hours_of_power
        tmp_user.longitude = longitude
        tmp_user.latitude = latitude
        tmp_user.phone_number = phone_number
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
    
    try:
        tmp_user = user.objects.get(user_email=email)
        return Response(model_to_dict(tmp_user))
    except:
        return Response({"detail": "Error: User does not exist"}, status=400)

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

    try:
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
            data = getSolarData(latitude, longitude, declination, azimuth, modules_power)
            if data[0] == 400:
                return Response({"Error": data[1]}, status=400)
            for i in range(192):
                solar[i][1] += data[1][i][1]
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

        user_model = UserProfile(weight1, weight2, low_limit, max_limit, risk, idealReserveThreshold, solar_forecast, base_forecast, cur_battery, battery_size)
        best_threshold, best_score, best_solar, best_battery = find_optimal_threshold(user_model)
        tmp_user.pred_opt_threshold = best_threshold
        

        #get user flexible loads (should pull from db and get required energy cost and duration of load)
        TeslaEV = FlexibleLoad("Tesla EV",1000,3) #example
        SomethingElse = FlexibleLoad("Something Else", 50000,23)
        flexible_loads = [TeslaEV, SomethingElse] #array of all user flexible loads

        #output good times for user visualization
        good_times = find_good_times(best_solar, best_battery)
        tmp_user.pred_good_time = json.dumps(good_times)

        #output ideal schedule
        best_schedule, best_schedule_score = find_optimal_fl_schedule(user_model, best_threshold, flexible_loads) #should return 2d array [ [1 (should charge), 20 (timeOfDay)], [0 (should not charge), 0 (irrelevant)]]
        tmp_user.pred_best_schedule = json.dumps(best_schedule)

        #user preferred schedule
        user_preferred_schedule = [8, 21] #preferred start times for TeslaEV/etc pulled from database

        #output acceptable boolean
        shouldCharge = should_charge(user_model, best_threshold, flexible_loads, user_preferred_schedule, best_schedule_score)
        tmp_user.should_charge = shouldCharge
        tmp_user.save()
        send_email(tmp_user.user_email, message.format(best_threshold))

    
    except Exception as e:
        return Response({"Error": str(e)}, status=400)


    #return best_threshold, good_times, best_schedule, and should_charge
    return Response({"detail": best_threshold}, status=200)