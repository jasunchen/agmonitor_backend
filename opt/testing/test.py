from opt.optimization import *

if __name__ == "__main__":

    weight1 = 1 #importance of cost 
    weight2 = 1 #importance of renewable integ
    weight3 = 1 #importance of shutoff
    lowerLimit = 20
    maximumLimit = 90
    shutOffRisk = 0
    idealReserveThreshold = 80


    baseForecast = [123.57, 153.57, 173.57, 175.71, 150.71, 154.29, 133.57, 124.29, 119.29, 112.86, 101.43, 95.71, 100.0, 96.43, 102.14, 86.43, 102.86, 60.71, 53.57, 63.57, 62.14, 55.0, 48.57, 55.71, 55.0, 55.0, 59.29, 60.0, 65.0, 48.57, 45.71, 12.86, 3.57, 0.71, 0.71, 0.0, 0.0, 0.0, 0.0, 0.0, 0.71, 0.71, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.43, 4.64, 0.36, 0.71, 4.64, 1.79, 3.57, 0.36, 0.36, 0.0, 0.0, 0.0, 0.0, 0.36, 0.36, 0.0, 1.43, 0.71, 0.0, 0.0, 0.71, 0.0, 0.36, 16.79, 25.71, 23.57, 47.5, 83.57, 57.5, 73.57, 84.64, 95.36, 101.79, 121.79, 129.29, 115.71, 121.43, 123.21, 317.5, 295.36, 253.93, 237.86, 256.07, 260.36, 245.36, 217.5, 242.86, 230.71, 123.57, 153.57, 173.57, 175.71, 150.71, 154.29, 133.57, 124.29, 119.29, 112.86, 101.43, 95.71, 100.0, 96.43, 102.14, 86.43, 102.86, 60.71, 53.57, 63.57, 62.14, 55.0, 48.57, 55.71, 55.0, 55.0, 59.29, 60.0, 65.0, 48.57, 45.71, 12.86, 3.57, 0.71, 0.71, 0.0, 0.0, 0.0, 0.0, 0.0, 0.71, 0.71, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.43, 4.64, 0.36, 0.71, 4.64, 1.79, 3.57, 0.36, 0.36, 0.0, 0.0, 0.0, 0.0, 0.36, 0.36, 0.0, 1.43, 0.71, 0.0, 0.0, 0.71, 0.0, 0.36, 16.79, 25.71, 23.57, 47.5, 83.57, 57.5, 73.57, 84.64, 95.36, 101.79, 121.79, 129.29, 115.71, 121.43, 123.21, 317.5, 295.36, 253.93, 237.86, 256.07, 260.36, 245.36, 217.5, 242.86, 230.71]
    solarForecast = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.5, 6.16, 80.14, 80.14, 80.14, 80.14, 144.18, 144.18, 144.18, 144.18, 266.67, 266.67, 266.67, 266.67, 330.13, 330.13, 330.13, 330.13, 374.62, 374.62, 374.62, 374.62, 482.84, 482.84, 482.84, 482.84, 464.04, 464.04, 464.04, 464.04, 374.93, 374.93, 374.93, 374.93, 331.0, 331.0, 331.0, 331.0, 107.96, 107.96, 107.96, 107.96, 31.17, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 3.0, 14.59, 207.65, 207.65, 207.65, 207.65, 422.78, 422.78, 422.78, 422.78, 620.13, 620.13, 620.13, 620.13, 745.72, 745.72, 745.72, 745.72, 801.83, 801.83, 801.83, 801.83, 784.19, 784.19, 784.19, 784.19, 691.59, 691.59, 691.59, 691.59, 531.03, 531.03, 531.03, 531.03, 326.56, 326.56, 326.56, 326.56, 106.72, 106.72, 106.72, 106.72, 31.17, 0.0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0] 

    currentBatteryState = 5000
    batterySize = 5000

    user_model = UserProfile(weight1, weight2, weight3, lowerLimit, maximumLimit, shutOffRisk, idealReserveThreshold, solarForecast, baseForecast, currentBatteryState, batterySize)
    best_threshold, best_score, best_solar, best_battery, utility, battery = find_optimal_threshold(user_model)
    
    #get user flexible loads (should pull from db and get required energy cost and duration of load)
    TeslaEV = FlexibleLoad("Tesla EV", 10000, 3) #example
    SomethingElse = FlexibleLoad("Something Else", 5000000, 1)
    flexible_loads = [TeslaEV, SomethingElse] #array of all user flexible loads

    #output good times for user visualization
    good_times = find_good_times(user_model, best_threshold, TeslaEV)

    #output ideal schedule
    #best_schedule, best_schedule_score, best_solarFL, best_batteryFL = find_optimal_fl_schedule(user_model, best_threshold, flexible_loads) #should return 2d array [ [1 (should charge), 20 (timeOfDay)], [0 (should not charge), 0 (irrelevant)]]

    #user preferred schedule
    user_preferred_schedule = [["Asdf", 1, 21],["Asdf", 1, 21]] #preferred start times for TeslaEV/etc pulled from database

    #output acceptable boolean
    #shouldCharge = should_charge(user_model, best_threshold, flexible_loads, user_preferred_schedule, best_schedule_score)

    #print(computeEnergyFlow(solarForecast, baseForecast))
    #print(good_times[0:96])
    #print(good_times.index(1))
    #print(good_times.index(0))
    #print(computeEnergyFlow(solarForecast, baseForecast))
    print(best_threshold, best_score, utility)
    #print(best_schedule, best_schedule_score)
    #print(shouldCharge)
    #print(calculate_shutOffRisk([]))

