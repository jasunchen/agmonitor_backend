from opt.utility.send_email import send_email
# from ucsb.models import *
from apscheduler.schedulers.background import BackgroundScheduler
from opt.utility.send_message import send_message
from opt.utility.schedulerHelper import *
import json


message = "Hello, this is a daily automated notification. Based on weather forecasts and historical data for tomorrow, the ideal reserve percentage for your battery is {} percent.{}Please visit https://agmonitor-pina-colada.herokuapp.com/ for more details."
bestTimes = " The best times for you to charge tomorrow is from {}. "

def optimization(email):
    from ucsb.models import user,user_asset
    from opt.optimization import find_optimal_threshold, find_good_times, find_optimal_fl_schedule, should_charge, calculate_idealReserveThreshold, calculate_shutOffRisk, UserProfile, FlexibleLoad
    from opt.base_load import calculate_base_load
    from opt.utility.solar import getSolarData
    from opt.utility.weather import get_alerts
    tmp_user = user.objects.get(user_email=email)
    generation_assets = user_asset.objects.filter(user=tmp_user, type_of_asset='generation')

    try:
        low_limit = tmp_user.low_limit
        max_limit = tmp_user.max_limit
        battery_size = tmp_user.battery_size * 1000 #convert kwh to watt hours
        cost_or_shutoff = tmp_user.cost_or_shutoff
        hours_of_power = tmp_user.hours_of_power
        longitude = tmp_user.longitude
        latitude = tmp_user.latitude
        alerts = get_alerts(latitude, longitude)
        # tmp_user.text = json.dumps(alert)
        risk = calculate_shutOffRisk(alerts)
        solar = []
        for i in range(0, 2866, 15):
            solar.append([i, 0])
        for gen in generation_assets:
            declination = gen.declination
            azimuth = gen.azimuth
            modules_power = gen.modules_power
            data = getSolarData(latitude, longitude, declination, azimuth, modules_power)
            if data[0] == 400:
                return data[1]
            for i in range(192):
                solar[i][1] += data[1][i][1]
        base_load = calculate_base_load(tmp_user, 0, 100000000000000000)

        ave_base_load = 0
        for i in range(96):
            ave_base_load += base_load[i][1]
        ave_base_load /= 96
        idealReserveThreshold = calculate_idealReserveThreshold(hours_of_power, ave_base_load, battery_size)
        base_load = base_load * 2
        weight1 = 1
        weight2 = 1
        weight3 = 1
        solar_forecast = [round(item[1] / 1000, 2) for item in solar]
        tmp_user.pred_solar_generation = json.dumps(solar_forecast)
        print("Solar Forecast Done.")

        base_forecast = [round(item[1] / 1000, 2) for item in base_load]
        tmp_user.pred_baseload = json.dumps(base_forecast)
        cur_battery = battery_size
        print("Battery Forecast Done.")

        solar_forecast = [item * 1000 for item in solar_forecast] #convert to watt hours
        user_model = UserProfile(weight1, weight2, weight3, low_limit, max_limit, risk, idealReserveThreshold, solar_forecast, base_forecast, cur_battery, battery_size)
        best_threshold, best_score, best_solar, best_battery, utility, battery = find_optimal_threshold(user_model)
        tmp_user.pred_opt_threshold = best_threshold
        tmp_user.pred_battery_level = battery
        tmp_user.utility = [item * -1 for item in utility] 
        print("Optimal Threshold Done.")

        #get user flexible loads (should pull from db and get required energy cost and duration of load)
        TeslaEV = FlexibleLoad("Tesla EV",10000, 10) #example
        SomethingElse = FlexibleLoad("Something Else",50000,23)
        flexible_loads = [TeslaEV, SomethingElse] #array of all user flexible loads

        #output good times for user visualization
        good_times = find_good_times(user_model, best_threshold, TeslaEV)
        tmp_user.pred_good_time = json.dumps(good_times)
        print("Good Times Done.")

        #output ideal schedule
        best_schedule, best_schedule_score, best_solarFL, best_batteryFL = find_optimal_fl_schedule(user_model, best_threshold, flexible_loads) #should return 2d array [ [1 (should charge), 20 (timeOfDay)], [0 (should not charge), 0 (irrelevant)]]
        tmp_user.pred_best_schedule = json.dumps(best_schedule)
        print("Best Schedule Done.")

        #user preferred schedule
        user_preferred_schedule = [["Tesla EV", 1, 10], ["Something Else", 0, 0]] #preferred start times for TeslaEV/etc pulled from database

        #output acceptable boolean
        shouldCharge = should_charge(user_model, best_threshold, flexible_loads, user_preferred_schedule, best_schedule_score)
        tmp_user.should_charge = shouldCharge
        #construct good times message
        # save weather alerts and good times
        goodTimesRange = convertRangeToTimes(findRange(good_times))

        text_dict = {
            "goodTimesRange" : goodTimesRange,
            "alerts" : alerts
        }
        print("Should Charge Done.")
        tmp_user.text = json.dumps(text_dict)
        tmp_user.save()

        print("Data Saved.")

        userMsg = bestTimes.format(goodTimesRange)

        #todo only output when should charge
        if True:
            send_email(tmp_user.user_email, message.format(tmp_user.pred_opt_threshold, userMsg))
            send_message(message.format(tmp_user.pred_opt_threshold, userMsg), tmp_user.phone_number)
        else:
            send_email(tmp_user.user_email, message.format(tmp_user.pred_opt_threshold, " "))
            send_message(message.format(tmp_user.pred_opt_threshold, " "), tmp_user.phone_number)

    except Exception as e:
        print(e)
        return "failed"


def opt_scheduler():
    from ucsb.models import user
    users = user.objects.all()
    for user in users:
        receiver = user.user_email
        optimization(receiver)

def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(opt_scheduler, 'cron', hour=21, minute=00, timezone='America/Los_Angeles')
    # scheduler.add_job(opt_scheduler, 'interval', minutes=1)
    scheduler.start()
