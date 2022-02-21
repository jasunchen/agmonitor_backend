from optimization import *
from parse import *
from sklearn.metrics import r2_score

#initial time, base load, solar load, powerwall, grid usage, battery charge
    
def compareTimes():
    pass

if __name__ == "__main__":
    fileName = "data/battery.csv"
    home, solar, powerwall, grid, battery_level = parse(fileName)
    print("solar:", solar)
    print("base:", home)

    weight1 = 1 #importance of cost 
    weight2 = 1 #importance of renewable integ
    weight3 = 1 #importance of shutoff
    lowerLimit = 20
    maximumLimit = 90
    shutOffRisk = 0
    idealReserveThreshold = 80

    base = home
    solar = solar
    
    #4 powerwalls = 4*13.5kwH = 54kWh 
    batterySize = 54000
    currentBatteryState = 0.86*batterySize

    
    energyFlow = computeEnergyFlow(solar, base)
    costGrid, costRenewableIntegration, excessSolar, excessBattery, utility, pred_battery= computePredictedBatteryChargeAndTotalCost(currentBatteryState, energyFlow, 20, batterySize)

    pred_battery = [round(item / (batterySize/1000), 2)*100 for item in pred_battery]
    pred_battery = pred_battery[:96]

    # print(battery_level)
    # print(battery[:96])

    diff = [real - pred for real, pred in zip(battery_level, pred_battery)]
    r2 = r2_score(battery_level, pred_battery )
    print(r2) #0.9759982805785794
    print(pred_battery)
    print(battery_level)
    # print(diff)
    # print(sum(diff))

    # user_model = UserProfile(weight1, weight2, weight3, lowerLimit, maximumLimit, shutOffRisk, idealReserveThreshold, solarForecast, baseForecast, currentBatteryState, batterySize)
    # best_threshold, best_score, best_solar, best_battery, utility, battery = find_optimal_threshold(user_model)
    
    # TeslaEV = FlexibleLoad("Tesla EV", 10000, 3) #example
    # SomethingElse = FlexibleLoad("Something Else", 5000000, 1)
    # flexible_loads = [TeslaEV] #array of all user flexible loads

    #output good times for user visualization
    # good_times = find_good_times(user_model, best_threshold, TeslaEV)

    #output ideal schedule
    #best_schedule, best_schedule_score, best_solarFL, best_batteryFL = find_optimal_fl_schedule(user_model, best_threshold, flexible_loads) #should return 2d array [ [1 (should charge), 20 (timeOfDay)], [0 (should not charge), 0 (irrelevant)]]

    #user preferred schedule
    # user_preferred_schedule = [["Asdf", 1, 21]]  

    #output acceptable boolean
    #shouldCharge = should_charge(user_model, best_threshold, flexible_loads, user_preferred_schedule, best_schedule_score)

    #print(computeEnergyFlow(solarForecast, baseForecast))
    #print(computeEnergyFlow(solarForecast, baseForecast))
    # print(best_threshold, best_score, utility)
    #print(best_schedule, best_schedule_score)
    #print(shouldCharge)
    #print(calculate_shutOffRisk([]))

