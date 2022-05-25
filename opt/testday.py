from opti import *
from parse import *
from sklearn.metrics import r2_score

#initial time, base load, solar load, powerwall, grid usage, battery charge
def findRange(arr): 
    continuous = False
    ranges = []
    for index, i in enumerate(arr):
        if i == 1:
            if continuous == False:
                continuous = True 
                ranges.append([index, index+1])
        elif len(ranges) != 0 and continuous == True:
            continuous = False
            ranges[-1][-1] = index
    return ranges

def convertIndexToTime(index): #0-96, 0 being 00:00, 96 being 24:00
	if (index == 96):
		return "11:59 PM"

	hours = index // 4
	minutes = (index % 4)*15
	if minutes == 0:
		minutes = "00"

	time = "AM"
	if hours >= 12:
		hours -= 12
		time = "PM"

	if hours == 0:
		hours = 12

	return "{}:{} {}".format(hours, minutes, time)

def scheduleToString(sched):
    # tempSched = [flexibleLoad.id, duration, i]

    return "Charge {} hrs at {}".format(sched[1]/4, convertIndexToTime(sched[2]))

def convertRangeToTimes(arr):
	length = len(arr)
	output = ""
	for index, ele in enumerate(arr):
		if (ele[0] == ele[1]):
			output += convertIndexToTime(ele[0])
		else:
			output += convertIndexToTime(ele[0]) + " to " + convertIndexToTime(ele[1])

		if (index == length - 2):
			output += ", and "
		else: 
			output += ", "

	return output[:-2]

def compareTimes():
    pass

#schedule ["", isOn, timeofday]
#inputs: baseload to test on, flexible load to schedule, schedule of flexible load, initial battery state, solar generation, number of dates
#outputs: utility usage, solar integration 
def checkTime(batterystate, batterySize, baseLoad, solar, shouldCharge, flexibleLoad, day, timeOfDay):
    entire_home_usage = sum(baseLoad) + sum(flexibleLoad)
    entire_solar_gen = sum(solar)

    if shouldCharge:
        for ind, ele in enumerate(flexibleLoad):
            baseLoad[day*96 + timeOfDay + ind] += ele

    energyFlow = computeEnergyFlow(solar, baseLoad)
    costGrid, costRenewableIntegration, excessSolar, excessBattery, utility, temp_battery= computePredictedBatteryChargeAndTotalCost(batterystate, energyFlow, 20, batterySize)
    solarToGrid = sum([item*1000 for item in utility if item >= 0])
    gridUsage = sum([item*-1000 for item in utility if item <= 0])

    return  (gridUsage/entire_home_usage, solarToGrid/entire_solar_gen, baseLoad, temp_battery[-1])

# schedule = [[day, timeOfDay, duration], [day, timeOfDay, duration], ... ]
# flexibleLoad = FLs to charge [ [1000, 1200, ...], [500,500...]]
def checkMonth(batterystate, batterySize, baseLoad, solar, flexibleLoad, schedule, thresholds):
    fl_sum = 0
    solarToGrid = 0
    gridUsage = 0
    util_final = []
    battery_final = []

    for i in flexibleLoad:
        fl_sum += sum(i)
    

    for ind, (day, timeOfDay, duration) in enumerate(schedule):
        for i in range(duration):
            if i < len(flexibleLoad[ind]):
                baseLoad[day*96 + timeOfDay + i] += flexibleLoad[ind][i]

    
    entire_home_usage = sum(baseLoad)
    entire_solar_gen = sum(solar)
    energyFlow = computeEnergyFlow(solar, baseLoad)

    # costGrid, costRenewableIntegration, excessSolar, excessBattery, utility, temp_battery= computePredictedBatteryChargeAndTotalCost(batterystate, energyFlow, 20, batterySize)
    # solarToGrid = sum([item*1000 for item in utility if item >= 0])
    # gridUsage = sum([item*-1000 for item in utility if item <= 0])

    for index, threshold in enumerate(thresholds):
        costGrid, costRenewableIntegration, excessSolar, excessBattery, utility, temp_battery= computePredictedBatteryChargeAndTotalCost(batterystate, energyFlow[index*96:index*96+96], threshold, batterySize)
        batterystate = temp_battery[95]*1000
        # print("batt for day{}: {}".format(index*96, round((batterystate*100)/ batterySize, 2)))
        solarToGrid += sum([item*1000 for item in utility if item >= 0])
        gridUsage += sum([item*-1000 for item in utility if item <= 0])
        util_final = util_final + utility
        battery_final = battery_final + temp_battery


    return  (gridUsage/entire_home_usage, solarToGrid/entire_solar_gen, (baseLoad, energyFlow, util_final, battery_final), temp_battery[-1]*1000)


# array of filtered flexible loads --> array of arrays of individual flexible load
def reconstructFilter(filteredFlex): 
    returnArr = []
    tempArr = []
    for i in filteredFlex: 
        if i == 0:
            if tempArr: 
                returnArr.append(tempArr)
                tempArr = []
        else:
            tempArr.append(i)
    return returnArr

def randomlyPruneSchedule(arr, n):
    to_delete = set(random.sample(range(len(arr)), n))
    return [ele for ind, ele in enumerate(arr) if not ind in to_delete]

# array of filtered flexible loads --> days on which charge occurs 
def findDays(filteredFlex):
    curCharge = False
    days = [0]*(len(filteredFlex) // 96)
    for ind, i in enumerate(filteredFlex):
        if i == 0:
            curCharge = False
        elif curCharge:
            continue
        else:
            curCharge = True
            days[(ind//96)] = 1
    return days




if __name__ == "__main__":
  
    fileNames =["apr25"]

    historical_baseload_avg = [202.81, 194.58, 201.93, 191.39, 182.69, 173.9, 152.74, 148.41, 156.21, 152.03, 145.35, 131.46, 145.11, 131.88, 113.24, 126.82, 123.58, 117.17, 105.16, 117.01, 124.4, 124.16, 136.53, 153.96, 195.83, 188.04, 206.4, 185.39, 157.31, 162.97, 167.69, 157.64, 154.85, 168.95, 180.86, 184.54, 188.6, 211.03, 239.68, 235.96, 240.09, 240.21, 255.46, 256.34, 271.9, 271.71, 284.37, 276.12, 274.44, 280.25, 273.16, 255.94, 259.27, 263.37, 258.82, 253.67, 237.28, 245.57, 238.39, 230.99, 213.81, 210.52, 219.89, 212.48, 199.15, 195.35, 218.14, 209.27, 190.1, 160.07, 153.15, 131.11, 114.27, 101.31, 101.25, 113.19, 118.95, 123.82, 125.34, 123.33, 125.79, 133.73, 128.9, 127.8, 129.78, 120.72, 125.98, 138.6, 139.75, 122.82, 124.05, 121.42, 195.17, 198.38, 219.35, 219.91]

        

    #settings 
    weight1 = 1 #importance of cost 
    weight2 = 2 #importance of renewable integ
    weight3 = 2 #importance of shutoff
    lowerLimit = 30
    maximumLimit = 100
    shutOffRisk = 0
    idealReserveThreshold = 80
    

    #4 powerwalls = 4*13.5kwH = 54kWh 
    batterySize = 54000
    currentBatteryState1, currentBatteryState2, originalBatteryState = 0.894*batterySize, 0.894*batterySize, 0.894*batterySize

    pred_battery_tesla = []
    pred_battery_watthours = []
    entire_home = []
    entire_solar = []
    weekly_best_times = []
    actual_grid = []
    modeled_grid = []
    actual_battery = []

    battery_level_from_forecasted = []
    gridUsage = 0
    solarToGrid = 0 

    hoursLost = 0
    energyLost = 0
    fl_to_charge = [1085.491] * 48
    fl_to_charge = [fl_to_charge]
    daysLost = 0




    for ind, name in enumerate(fileNames):

        #print(currentBatteryState)
        home, solar, powerwall, grid, battery_level = parse("data/"+name+".csv")

        #extracting data
        actual_grid = actual_grid + grid
        entire_home = entire_home + home
        entire_solar = entire_solar + solar
        actual_battery = actual_battery + battery_level
        energyFlow = computeEnergyFlow(solar, home)
        costGrid, costRenewableIntegration, excessSolar, excessBattery, utility, temp_battery= computePredictedBatteryChargeAndTotalCost(currentBatteryState1, energyFlow, lowerLimit, batterySize)
        utility = utility[:96]
        solarToGrid += sum([item*1000 for item in utility if item >= 0])
        gridUsage += sum([item*-1000 for item in utility if item <= 0])
        modeled_grid = modeled_grid + utility[:96]
        # print(excessSolar)
        currentBatteryState1 = temp_battery[95]*1000
        pred_battery_watthours = pred_battery_watthours + temp_battery[:96]
        temp_battery = [round(item / (batterySize/1000), 2)*100 for item in temp_battery] #convert to battery percentage
        temp_battery = temp_battery[:96]
        pred_battery_tesla = pred_battery_tesla + temp_battery
    


    print("Original grid usage: {}%, solar to grid: {}%".format(gridUsage*100/ sum(entire_home), solarToGrid*100/(sum(entire_solar))))
    entire_solar = entire_solar * 2

    algoScheduleResults = []
    algoThresholdResults = []
    lostChargeSessions = []
    extraChargeSessions = []
    reconstructed_filter_index = 0


    for ind, name in enumerate(fileNames):

        home, solar, powerwall, grid, battery_level = parse("data/"+name+".csv")


        baseForecast = historical_baseload_avg*2
        solarForecast = entire_solar[ind*96:ind*96+192]

        if (len(solarForecast) != 192 or len(baseForecast) != 192):
            print("ERROR")
        user_model = UserProfile(weight1, weight2, weight3, lowerLimit, maximumLimit, shutOffRisk, idealReserveThreshold, solarForecast, baseForecast, currentBatteryState2, batterySize, 0, 96)
        #64 --> 4pm 

        TeslaEV = FlexibleLoad("Tesla EV", 1085.491, 0, 60) #example

        (best_threshold, best_performance, best_sol, best_batt, (cost, schedule, utility, battery), should_charge, solutions)= find_optimal_threshold_and_schedule(user_model, TeslaEV)
        algoThresholdResults.append(best_threshold)

        #assume user follows recommended schedule
        #currentBatteryState2 = best_batt[95]*1000
        #assume never charge
        currentBatteryState2 = battery[-1][95]*1000

        # good_times, costCharge = find_good_times(user_model, best_threshold, TeslaEV)
        # besttimes = convertRangeToTimes(findRange(good_times + [0]))
        # weekly_best_times = weekly_best_times + good_times
        # shouldCharge = should_charge(user_model, best_threshold, costCharge)
        print("Results for {}: Best threshold - {}, Should charge - {}, Best Solution - {}, End of day Battery level - {}%. ".format(name, best_threshold, should_charge, scheduleToString(best_sol), round(currentBatteryState2  * 100 / batterySize, 2 )))
        algoScheduleResults.append([ind, best_sol[2], best_sol[1]])
        # if daysCharged[ind] == 1: #user charged in reality
        #     if (should_charge):
        #         print("Success: User also needed to charge in reality, charge #{} lasting {} hrs.".format( reconstructed_filter_index, len(reconstructed_filter[reconstructed_filter_index])/4))
        #         fl_to_charge.append(reconstructed_filter[reconstructed_filter_index])
        #         algoScheduleResults.append([ind, best_sol[2], best_sol[1]])
        #     else:
        #         daysLost += 1
        #         print("Failure: User needed to charge today, charge #{} lasting {} hrs.".format( reconstructed_filter_index, len(reconstructed_filter[reconstructed_filter_index])/4))
        #     # print(best_sol[1])
        #     hoursLost += max((len(reconstructed_filter[reconstructed_filter_index])- best_sol[1]), 0)/4
        #     energyLost += sum(reconstructed_filter[reconstructed_filter_index][best_sol[1]:])/1000
        #     lostChargeSessions.append(reconstructed_filter[reconstructed_filter_index][best_sol[1]:])
        #     reconstructed_filter_index += 1
        #     # algoScheduleResults.append([ind, findRange(schedule + [0])[0][0]])
        # else :
        #     if (should_charge):
        #         extraChargeSessions.append([ind, best_sol[2], best_sol[1]])
                
        print("--------------------------------------------------------------------------")


    val1, val2, (baseLoad, energyFlow, util_final, battery_final), endingBatt = checkMonth(originalBatteryState, batterySize, entire_home, entire_solar[:-96], fl_to_charge, algoScheduleResults, algoThresholdResults)
    print("Estimated performance: grid usage {}%, solar to grid: {}%, with ending battery {}".format(val1*100, val2*100, round((endingBatt*100) / batterySize, 2) ))
 
    battery_final = [round((item*1000*100) / batterySize, 2) for item in battery_final] #convert to battery percentage

# schedule = [[day, timeOfDay, duration], [day, timeOfDay, duration], ... ]
# flexibleLoad = FLs to charge 
# def checkMonth(batterystate, batterySize, baseLoad, solar, flexibleLoad, schedule):

    print("STATS - hours of charging lost: {}, kWh lost: {}, days lost: {}. ".format( hoursLost, energyLost, daysLost))



    # flat_list = [item for sublist in lostChargeSessions for item in sublist]
    # lostChargeSessions = [ flat_list[0:30], flat_list[30:]]
    # print(lostChargeSessions)
    # print(len(lostChargeSessions))

    # val1, val2, (baseLoad, energyFlow, util_final, battery_final), endingBatt = checkMonth(originalBatteryState, batterySize, baseLoad, entire_solar[:-96], lostChargeSessions, [[11,64,99],[12,64,99]], algoThresholdResults)
    # print("Estimated performance of inserting charge time: grid usage {}%, solar to grid: {}%, with ending battery {}".format(val1*100, val2*100, round((endingBatt*100) / batterySize, 2) ))


    #model
    # # print("DATA:")
    print("baseload_test = ", baseLoad)
    print("energyflow_test = ", energyFlow)
    print("util_test = ", util_final)
    print("batt_test = ", battery_final)


    print("pred_battery_tesla = ", pred_battery_tesla)
    print("entire_solar = ", entire_solar)
    print("entire_home = " , entire_home)
    # print(actual_grid)
    # print(modeled_grid)
    print("actual_battery = " , actual_battery)

    #testing results
    print("RESULTS:")

    # battery_level_from_forecasted = [round(item / (batterySize/1000), 2)*100 for item in battery_level_from_forecasted] #convert to battery percentage
    # print(battery_level_from_forecasted)
    # print(weekly_best_times)





    


