import numpy as np
import random
from typing import List

class UserProfile:
  def __init__(self, weight1, weight2, weight3, lowerLimit, maximumLimit, shutOffRisk, idealReserveThreshold, solarForecast, baseForecast, currentBatteryState, batterySize, time1, time2):
    self.weight1 = weight1
    self.weight2 = weight2
    self.weight3 = weight3
    self.lowerLimit = lowerLimit
    self.maximumLimit = maximumLimit
    self.shutOffRisk = shutOffRisk
    self.idealReserveThreshold = idealReserveThreshold
    self.solarForecast = solarForecast
    self.baseForecast = baseForecast
    self.currentBatteryState = currentBatteryState
    self.batterySize = batterySize
    self.time1 = time1
    self.time2 = time2

class FlexibleLoad:
  def __init__(self, id, energyCost, minDuration, maxDuration):
    self.id = id
    self.energyCost = energyCost #avg cost per 15 minute interval 
    self.minDuration = minDuration 
    self.maxDuration = maxDuration 

class Schedule: 
    def __init__(self, id, duration, startTime):
        self.id = id
        self.duration = duration 
        self.startTime = startTime 

# alerts: an array severity rankings
def calculate_shutOffRisk(alerts):
    risk = 0
    for (alert, description) in alerts:
        if alert == 1 or alert == "Advisory":
            risk += 0.01
        elif alert == 2 or alert == "Watch":
            risk += 0.05
        elif alert == 3 or alert == "Warning":
            risk += 0.5
    return min(1, risk)

def calculate_idealReserveThreshold(numberOfHours, avgBaseload, batterySize):
    if (batterySize == 0):
        return 0.01
    return max(min(1,(numberOfHours * avgBaseload) / batterySize), 0.01)

#solar and base should be 192 arrays of length 192 to represent 48 hour broken into 15 min intervals
def computeEnergyFlow(solar, base):
    energyFlow = []
    for i in range(len(solar)):
        energyFlow.append(solar[i] - base[i])
    return energyFlow

def flexibleLoadEnergyFlow(energyFlow, flexibleLoads: List[FlexibleLoad], schedule: List[List[int]]):
    maxTime = len(energyFlow) - 1
    for i in range(len(flexibleLoads)):
        loadCost = flexibleLoads[i].energyCost
        duration = schedule[i][1]
        beginTime = schedule[i][2]
        for t in range(beginTime, min(beginTime+duration, maxTime)):
                energyFlow[t] -= loadCost
    return energyFlow
    #    tempSched = [flexibleLoad.id, duration, i]


def computePredictedBatteryChargeAndTotalCost(currentCharge, energyFlow, threshold, maxStorage):
    #todo: use utility rate plan to determine exact costs
    price = 1
    costGrid = 0
    costRenewableIntegration = 0

    #todo: implement maxcharge/maxdischarge
    maxCharge = 0.37 * maxStorage #5 kW rate #825 #watt hours per 15 min increment or ~3.3 kWh
    maxDischarge = -0.37 * maxStorage #5 kW #1925 #watt hours per 15 min increment or ~7.7 kWh

    length = len(energyFlow) #should be 192 for 2 days
    excessSolar = [0]*length #if solar generation is too high 
    excessBattery = [0]*length #if battery storage is capped out
    utility = [0]*length #positive = solar to grid, negative = utility to customer
    battery = [0]*length

    #keep track of maximum costs to minmax normalize values 
    maxCostGrid = 0.01
    maxCostRenewableIntegration = 0.01

    thresholdWattHours = 0.01 *threshold*maxStorage #convert threshold percentage into watt hours

    for index, e in enumerate(energyFlow):
        currentMaxCharge = min(maxCharge, maxStorage - currentCharge)
        currentMaxDischarge = max(maxDischarge, min(thresholdWattHours - currentCharge, 0))
        #print("energyupdate", index, ": ", e,", currentCharge: ", currentCharge, ", costs:", costGrid, maxCostGrid, costGrid/maxCostGrid)
        if (e > 0): #producing excess solar energy
            currentCharge += min(e, currentMaxCharge)
            excess = max(0, e-currentMaxCharge)
            excessSolar[index] += excess
            maxCostRenewableIntegration += e
            utility[index] += excess
            costRenewableIntegration += excess
        else:
            deficit = min(0, e-currentMaxDischarge) #-1000 - -1925 --> 925 --> 0, -2000 --1925 --> -75
            currentCharge += max(e, currentMaxDischarge) #max to take less negative number
            maxCostGrid += e*price
            utility[index] += deficit
            costGrid += deficit

        if (currentCharge < thresholdWattHours):
            if (e > 0): #try to charge battery as much as possible still
                additionalCharge = max(currentMaxCharge - e, 0)
                currentCharge += additionalCharge
                utility[index] += -1*additionalCharge
                costGrid += -1*additionalCharge
                maxCostGrid += -1*additionalCharge
            else: #not using battery, but charge anyways as much as possible
                currentCharge += currentMaxCharge
                utility[index] += -1*currentMaxCharge
                costGrid += -1*currentMaxCharge
                maxCostGrid += -1*currentMaxCharge

        utility[index] = round((utility[index]/1000),8)
        battery[index] = round(currentCharge/1000,8)        
        # if (battery[index] < round(thresholdWattHours/1000,2)):
        #     print("ERROR: {}, {}".format(battery[index], thresholdWattHours/1000))

    # cost to grid
    # wasted solar
    # excess solar (not wasted, could not capture bc of limitations)
    # excess battery (wasted)
    return (costGrid/maxCostGrid, costRenewableIntegration/maxCostRenewableIntegration, excessSolar, excessBattery, utility, battery)

def computeShutOffCost(shutOffRisk, idealReserveThreshold, threshold):
        return shutOffRisk * (1 - (threshold/idealReserveThreshold))


def flCost(userProfile: UserProfile, threshold, flexibleLoads: List[FlexibleLoad], schedule: List[List[int]]):
    energyFlow = computeEnergyFlow(userProfile.solarForecast, userProfile.baseForecast)
    if flexibleLoads:
        energyFlow = flexibleLoadEnergyFlow(energyFlow, flexibleLoads, schedule)


    costGrid, costRenewableIntegration, excessSolar, excessBattery, utility, battery= computePredictedBatteryChargeAndTotalCost(userProfile.currentBatteryState, energyFlow, threshold, userProfile.batterySize)
    costShutOff = (computeShutOffCost(userProfile.shutOffRisk, userProfile.idealReserveThreshold, battery[95]) 
        # + computeShutOffCost(userProfile.shutOffRisk, userProfile.idealReserveThreshold, battery[191]) 
        + computeShutOffCost(userProfile.shutOffRisk, userProfile.idealReserveThreshold, threshold)) / 2

    cost = userProfile.weight1*costGrid  + userProfile.weight2 * costRenewableIntegration + userProfile.weight3* costShutOff
    # print("cost: {}, {},{}".format(costGrid, costRenewableIntegration,costShutOff ))
    return (cost, costGrid/(costRenewableIntegration+0.1), costGrid/(costShutOff+0.1), utility, battery)


def find_optimal_threshold_and_schedule(userProfile: UserProfile, flexibleLoad: FlexibleLoad):
    differentThresholds = []
    differentThresholdPerformance = []
    minCost = 999999
    should_charge = [0]*101
    ri = []
    so = []
    solutions = []

    for threshold in range(userProfile.lowerLimit, userProfile.maximumLimit+1): 
        schedule = []
        cost = []
        utility = []
        battery = []
        for i in range(userProfile.time1, userProfile.time2):
            for duration in range(flexibleLoad.maxDuration, flexibleLoad.minDuration-1, -4):
                tempSched = [flexibleLoad.id, duration, i]
                candidate_cost, _ri, _so, _util, _battery = flCost(userProfile, threshold, [flexibleLoad], [tempSched])
                schedule.append(tempSched)
                cost.append(candidate_cost)
                battery.append(_battery)


                if (candidate_cost < minCost):
                    minCost = candidate_cost
                    solutions.clear()
                    utility.clear()
                    
                    solutions.append(tempSched)
                    utility.append(_util)
                elif (candidate_cost == minCost): #abs(candidate_cost - minCost) < 0.0000001
                    solutions.append(tempSched)
                    utility.append(_util)


                #weights
                ri.append(_ri)
                so.append(_so)

        #check no FL scheduled
        no_fl_cost, _ri, _so, _util, _battery = flCost(userProfile, threshold, None, None) 

        # if minCost > no_fl_cost:
        #     should_charge = False
        if (min(cost) <= no_fl_cost):
            should_charge[threshold] = 1
        schedule.append([flexibleLoad.id, 0, 0])
        cost.append(no_fl_cost)
        utility.append(_util)
        battery.append(_battery)

        ri.append(_ri)
        so.append(_so)



        differentThresholds.append((cost, schedule, utility, battery))
        differentThresholdPerformance.append(min(cost))

    # print("WEIGHTS: {} , {} ".format(sum(ri) / len(ri), sum(so) / len(so)))

    best_performance = min(differentThresholdPerformance)
    best_performance_index = differentThresholdPerformance.index(best_performance)
    best_threshold = best_performance_index + userProfile.lowerLimit
    best_threshold_should_charge = (bool) (should_charge[best_threshold])
    (cost, schedule, utility, battery) = differentThresholds[best_performance_index]
    best_sol = schedule[cost.index(min(cost))]
    best_batt = battery[cost.index(min(cost))]

    num_sol = 0
    for i in range(len(differentThresholds)):
        if differentThresholdPerformance[i] == best_performance:
            num_sol += differentThresholds[i][0].count(best_performance)
    # print("Num solutions: {}".format(num_sol))

    return (best_threshold, best_performance, best_sol, best_batt, differentThresholds[best_performance_index], best_threshold_should_charge, solutions)


if __name__ == "__main__":

    weight1 = 1 #importance of cost 
    weight2 = 8 #importance of renewable integ
    weight3 = 3.94 #importance of shutoff
    lowerLimit = 20
    maximumLimit = 90
    shutOffRisk = 0.5
    idealReserveThreshold = 80
    
    time1 = 0
    time2 = 96

    baseForecast = [202.81, 194.58, 201.93, 191.39, 182.69, 173.9, 152.74, 148.41, 156.21, 152.03, 145.35, 131.46, 145.11, 131.88, 113.24, 126.82, 123.58, 117.17, 105.16, 117.01, 124.4, 124.16, 136.53, 153.96, 195.83, 188.04, 206.4, 185.39, 157.31, 162.97, 167.69, 157.64, 154.85, 168.95, 180.86, 184.54, 188.6, 211.03, 239.68, 235.96, 240.09, 240.21, 255.46, 256.34, 271.9, 271.71, 284.37, 276.12, 274.44, 280.25, 273.16, 255.94, 259.27, 263.37, 258.82, 253.67, 237.28, 245.57, 238.39, 230.99, 213.81, 210.52, 219.89, 212.48, 199.15, 195.35, 218.14, 209.27, 190.1, 160.07, 153.15, 131.11, 114.27, 101.31, 101.25, 113.19, 118.95, 123.82, 125.34, 123.33, 125.79, 133.73, 128.9, 127.8, 129.78, 120.72, 125.98, 138.6, 139.75, 122.82, 124.05, 121.42, 195.17, 198.38, 219.35, 219.91]
    baseForecast = baseForecast * 2
    solarForecast = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 26, 153, 299, 419, 509, 587, 661, 730, 795, 846, 894, 938, 980, 1022, 1051, 1077, 1089, 1101, 1116, 1125, 1119, 1119, 1109, 1080, 1049, 1023, 986, 944, 899, 845, 792, 731, 662, 584, 503, 417, 326, 231, 145, 72, 15, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 45, 157, 283, 420, 507, 593, 671, 742, 799, 855, 871, 928, 958, 1013, 967, 1024, 1029, 1092, 1041, 1074, 1085, 1113, 1101, 1080, 1068, 1020, 1014, 864, 761, 759, 711, 734, 679, 576, 439, 414, 313, 219, 130, 46, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 48, 163, 285, 432, 510, 591, 666, 732, 793, 848, 897, 939, 979, 1014, 1039, 1064, 1089, 1104, 1113, 1121, 1123, 1114, 1095, 1071, 1043, 1013, 982, 943, 893, 843, 791, 727, 660, 585, 503, 418, 328, 236, 152, 80, 25, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 33, 167, 310, 435, 512, 591, 664, 730, 791, 848, 902, 948, 983, 1015, 1038, 1053, 1070, 1086, 1101, 1105, 1103, 1107, 1105, 1086, 1061, 1031, 990, 951, 908, 853, 790, 726, 657, 583, 507, 422, 332, 240, 154, 80, 25, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 39, 177, 314, 426, 513, 591, 660, 728, 790, 838, 886, 933, 975, 1010, 1044, 1087, 1105, 1124, 1121, 1108, 1110, 1107, 1097, 1064, 1032, 1010, 977, 941, 896, 851, 788, 725, 656, 583, 503, 422, 335, 243, 158, 84, 24, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5, 57, 185, 312, 442, 523, 602, 674, 738, 798, 852, 903, 951, 973, 1023, 1061, 1081, 1099, 1107, 1115, 1116, 1119, 1114, 1100, 1077, 1050, 1021, 987, 943, 898, 848, 789, 724, 656, 585, 508, 427, 341, 249, 169, 92, 34, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 49, 171, 303, 447, 521, 599, 671, 736, 794, 848, 898, 943, 984, 1018, 1044, 1073, 1098, 1115, 1122, 1119, 1115, 1106, 1089, 1071, 1052, 1026, 987, 944, 903, 856, 799, 736, 669, 596, 517, 433, 344, 253, 166, 91, 33, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 9, 66, 204, 320, 434, 534, 592, 692, 720, 776, 865, 890, 907, 947, 984, 1057, 1044, 1114, 1149, 1141, 1136, 1090, 1030, 1038, 1049, 981, 934, 930, 980, 882, 818, 723, 645, 592, 532, 503, 472, 381, 252, 162, 117, 55, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    solarForecast = solarForecast[0:192]
    currentBatteryState = 40000
    batterySize = 50000

    user_model = UserProfile(weight1, weight2, weight3, lowerLimit, maximumLimit, shutOffRisk, idealReserveThreshold, solarForecast, baseForecast, currentBatteryState, batterySize, time1, time2)
    TeslaEV = FlexibleLoad("Tesla EV", 10854.91, 10, 40) #example

    (best_threshold, best_performance, best_sol, best_batt, (cost, schedule, utility, battery), should_charge, solutions) = find_optimal_threshold_and_schedule(user_model, TeslaEV)
    print("Best threshold: {}, score: {}, should_charge: {}".format(best_threshold, best_performance, should_charge))
    #print("Costs: ", cost)
    print("Best schedule:", schedule[cost.index(min(cost))])
    print("Best: ", best_sol)
    print("Solutions:", solutions)

