import numpy as np
import random
from typing import List


#from base_load import calculate_base_load

class UserProfile:
  def __init__(self, weight1, weight2, lowerLimit, maximumLimit, shutOffRisk, idealReserveThreshold, solarForecast, baseForecast, currentBatteryState, batterySize):
    self.weight1 = weight1
    self.weight2 = weight2
    self.lowerLimit = lowerLimit
    self.maximumLimit = maximumLimit
    self.shutOffRisk = shutOffRisk
    self.idealReserveThreshold = idealReserveThreshold
    self.solarForecast = solarForecast
    self.baseForecast = baseForecast
    self.currentBatteryState = currentBatteryState
    self.batterySize = batterySize

class FlexibleLoad:
  def __init__(self, id, energyCost, duration):
    self.id = id
    self.energyCost = energyCost
    self.duration = duration



# alerts: an array severity rankings
def calculate_shutOffRisk(alerts):
    risk = 0
    for alert in alerts:
        if alert == 1 or alert == "Advisory":
            risk += 0.1
        elif alert == 2 or alert == "Watch":
            risk += 0.34
        elif alert == 3 or alert == "Warning":
            risk += 0.67
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

def computePredictedBatteryChargeAndTotalCost(currentCharge, energyFlow, threshold, maxStorage):
    #todo: use utility rate plan to determine exact costs
    price = 1
    costGrid = 0
    costRenewableIntegration = 0

    #todo: implement maxcharge/maxdischarge
    maxCharge = 825 #watt hours per 15 min increment or ~3.3 kWh
    maxDischarge = -1925 #watt hours per 15 min increment or ~7.7 kWh

    excessSolar = [0]*192 #if solar generation is too high
    excessBattery = [0]*192 #if battery storage is capped out

    #keep track of maximum costs to minmax normalize values 
    maxCostGrid = 0.01
    maxCostRenewableIntegration = 0.01

    thresholdWattHours = 0.01 *threshold*maxStorage #convert threshold percentage into watt hours
    minimumWattHours = 0.2*maxStorage

    for index, e in enumerate(energyFlow):
        #print("energyupdate", index, ": ", e,", currentCharge: ", currentCharge, ", costs:", costGrid, maxCostGrid, costGrid/maxCostGrid)
        if (e > 0): #producing excess solar energy
            currentCharge += min(e, maxCharge)
            excessSolar[index] += max(0, e-maxCharge)
            maxCostRenewableIntegration += e
        else:
            currentCharge += max(e, maxDischarge) #max to take less negative number
            maxCostGrid += max(e, maxDischarge)*price

        diff = currentCharge - thresholdWattHours if (index < 96) else currentCharge - minimumWattHours

        if (diff < 0):
            costGrid += diff*price
            currentCharge -= diff #todo maxcharge
        
        if (currentCharge > maxStorage): #wasted solar
            excess = currentCharge - maxStorage 
            costRenewableIntegration += excess
            excessBattery[index] += currentCharge
            currentCharge -= excess
        

    # cost to grid
    # wasted solar
    # excess solar (not wasted, could not capture bc of limitations)
    # excess battery (wasted)
    return (costGrid/maxCostGrid, costRenewableIntegration/maxCostRenewableIntegration, excessSolar, excessBattery)

def computeShutOffCost(shutOffRisk, idealReserveThreshold, threshold):
        return shutOffRisk * (1 - (threshold/idealReserveThreshold))


def thresholdCost(userProfile: UserProfile, threshold):
    #solarForecast -> 2 day forecasted solar production beginning from right now
    #batteryState -> batteryPercentage, maxCharge, maxDischarge

    energyFlow = computeEnergyFlow(userProfile.solarForecast, userProfile.baseForecast)
    costGrid, costRenewableIntegration, excessSolar, excessBattery = computePredictedBatteryChargeAndTotalCost(userProfile.currentBatteryState, energyFlow, threshold, userProfile.batterySize)
    costShutOff = computeShutOffCost(userProfile.shutOffRisk, userProfile.idealReserveThreshold, threshold)

    cost = userProfile.weight1*costGrid + (1-userProfile.weight1)* costShutOff + userProfile.weight2 * costRenewableIntegration

    return (cost, excessSolar, excessBattery)

def find_optimal_threshold(userProfile: UserProfile):
    step_size = 20
    temp = 10

    initial_eval = thresholdCost(userProfile, userProfile.lowerLimit)[0]
    curr, curr_eval = userProfile.lowerLimit, initial_eval
    best, best_eval = curr, curr_eval
    best_solar, best_battery = [],[]

    for i in range(1000):
        candidate = curr + np.random.randn() * step_size
        candidate = max(userProfile.lowerLimit, candidate)
        candidate = min(userProfile.maximumLimit, candidate)
        candidate_eval, excessSolar, excessBattery = thresholdCost(userProfile, candidate)

        if candidate_eval < best_eval:
            best, best_eval, best_solar, best_battery = candidate, candidate_eval, excessSolar, excessBattery
            print('>%d cost(%s) = %.5f' % (i, best, best_eval))
        diff = candidate_eval - curr_eval
        t = temp / float(i + 1)
        metropolis = np.exp(-diff / t)
        if diff < 0 or np.random.rand() < metropolis:
            curr, curr_eval = candidate, candidate_eval

    return [best, best_eval, best_solar, best_battery]

def flexibleLoadEnergyFlow(energyFlow, flexibleLoads: List[FlexibleLoad], schedule: List[List[int]]):
    for i in range(len(flexibleLoads)):
        loadCost = flexibleLoads[i].energyCost
        duration = flexibleLoads[i].duration
        isOn = schedule[i][1]
        beginTime = schedule[i][2]

        if isOn == 1:
            avgConsumption = loadCost/duration
            for t in range(beginTime, beginTime+duration):
                energyFlow[t] -= avgConsumption
    return energyFlow

def flexibleLoadScheduleCost(userProfile: UserProfile, threshold, flexibleLoads: List[FlexibleLoad], schedule: List[List[int]]):
    #todo: use utility rate plan to determine exact costs
    price = 1
    costGrid = 0
    costRenewableIntegration = 0

    #todo: implement maxcharge/maxdischarge
    maxCharge = 825 #watt hours per 15 min increment or ~3.3 kWh
    maxDischarge = -1925 #watt hours per 15 min increment or ~7.7 kWh

    excessSolar = [0]*192 #if solar generation is too high
    excessBattery = [0]*192 #if battery storage is capped out

    #keep track of maximum costs to minmax normalize values 
    maxCostGrid = 0.01
    maxCostRenewableIntegration = 0.01

    thresholdWattHours = 0.01 *threshold*userProfile.batterySize #convert threshold percentage into watt hours
    minimumWattHours = 0.2*userProfile.batterySize
    currentCharge = userProfile.currentBatteryState

    energyFlow = computeEnergyFlow(userProfile.solarForecast, userProfile.baseForecast)
    energyFlow = flexibleLoadEnergyFlow(energyFlow, flexibleLoads, schedule)

    for index, e in enumerate(energyFlow):
        #print("energyupdate", index, ": ", e,", currentCharge: ", currentCharge, ", costs:", costGrid, maxCostGrid, costGrid/maxCostGrid)
        if (e > 0): #producing excess solar energy
            currentCharge += min(e, maxCharge)
            excessSolar[index] += max(0, e-maxCharge)
            maxCostRenewableIntegration += e
        else:
            currentCharge += max(e, maxDischarge) #max to take less negative number
            maxCostGrid += max(e, maxDischarge)*price

        diff = currentCharge - thresholdWattHours if (index < 96) else currentCharge - minimumWattHours

        if (diff < 0):
            costGrid += diff*price
            currentCharge -= diff #todo maxcharge
        
        if (currentCharge > userProfile.batterySize): #wasted solar
            excess = currentCharge - userProfile.batterySize 
            costRenewableIntegration += excess
            excessBattery[index] += currentCharge
            currentCharge -= excess
    cost = userProfile.weight1*(costGrid/maxCostGrid) + userProfile.weight2 * (costRenewableIntegration/maxCostRenewableIntegration)
    return (cost, excessSolar, excessBattery)

def find_good_times(best_solar, best_battery):
    #for user visualization
    schedule = [0]*96
    for i in range(96):
        schedule[i] += best_solar[i]
        if (best_battery[i] > 0):
            for j in range(i+1):
                schedule[j] += best_battery[i]/(i+1)
    maxExcess = max(schedule)
    return [val / maxExcess for val in schedule]

def create_candidate_schedule(schedule, step, epoch):
    for i in range(len(schedule)):
        if epoch < 5:
            schedule[i][1] = np.random.randint(2)
        schedule[i][2] += np.random.randn()*step
        schedule[i][2] = round(schedule[i][2])
        schedule[i][2] = max(0, schedule[i][2])
        schedule[i][2] = min(95, schedule[i][2])
    return schedule


def find_optimal_fl_schedule(userProfile: UserProfile, threshold, flexibleLoads: List[FlexibleLoad]):
    #for best possible schedule & score
    step_size = 10
    temp = 10

    initial_schedule = []
    for i in range(len(flexible_loads)):
        initial_schedule.append([flexibleLoads[i].id, np.random.randint(2), np.random.randint(96)])
    initial_eval = flexibleLoadScheduleCost(userProfile, threshold, flexibleLoads, initial_schedule)[0]

    curr, curr_eval = initial_schedule, initial_eval
    best, best_eval = curr, curr_eval
    best_solar, best_battery = [],[]

    for epoch in range(10):
        for i in range(1000):
            candidate = create_candidate_schedule(curr, step_size, epoch)
            candidate_eval, excessSolar, excessBattery = flexibleLoadScheduleCost(userProfile, threshold, flexibleLoads, candidate)

            if candidate_eval < best_eval:
                best, best_eval, best_solar, best_battery = candidate, candidate_eval, excessSolar, excessBattery
                print('>%d cost(%s) = %.5f' % (i, best, best_eval))
            diff = candidate_eval - curr_eval
            t = temp / float(i + 1)
            metropolis = np.exp(-diff / t)
            if diff < 0 or np.random.rand() < metropolis:
                curr, curr_eval = candidate, candidate_eval

    return [best, best_eval, best_solar, best_battery]

def should_charge(userProfile: UserProfile, threshold, flexibleLoads: List[FlexibleLoad], schedule: List[List[int]], optimum: float):
    #is given schedule close enough to optimum? 
    cost = flexibleLoadScheduleCost(userProfile, threshold, flexibleLoads, schedule)[0]
    return (cost-optimum <= 0.2)

if __name__ == "__main__":

    weight1 = 0.7 #importance of cost over shutoff (0 is no consideration for cost, 1 is only consider cost)
    weight2 = 0.6
    lowerLimit = 20
    maximumLimit = 90
    shutOffRisk = 0.2
    idealReserveThreshold = 80

    solarForecast = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,10,10,10,10,40,60,80,100,15000,40579,71855, 80123, 90432, 100213, 123100, 130412, 123400, 102103, 105033, 90123, 70123, 15000, 5000,4000,3000,1999,500,50,10,10,10,10,10,10,10,10,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,10,10,10,10,40,60,80,100,15000,40579,71855, 80123, 90432, 100213, 123100, 130412, 123400, 102103, 105033, 90123, 70123, 15000, 5000,4000,3000,1999,500,50,10,10,10,10,10,10,10,10,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    baseForecast = [1000]*192
    currentBatteryState = 14000
    batterySize = 14000

    user_model = UserProfile(weight1, weight2, lowerLimit, maximumLimit, shutOffRisk, idealReserveThreshold, solarForecast, baseForecast, currentBatteryState, batterySize)
    best_threshold, best_score, best_solar, best_battery = find_optimal_threshold(user_model)
    
    #get user flexible loads (should pull from db and get required energy cost and duration of load)
    TeslaEV = FlexibleLoad("Tesla EV", 10000,3) #example
    SomethingElse = FlexibleLoad("Something Else", 50000000000,1 )
    flexible_loads = [TeslaEV, SomethingElse] #array of all user flexible loads

    #output good times for user visualization
    good_times = find_good_times(best_solar, best_battery)

    #output ideal schedule
    best_schedule, best_schedule_score, best_solarFL, best_batteryFL = find_optimal_fl_schedule(user_model, best_threshold, flexible_loads) #should return 2d array [ [1 (should charge), 20 (timeOfDay)], [0 (should not charge), 0 (irrelevant)]]

    #user preferred schedule
    user_preferred_schedule = [["Asdf", 1, 21],["Asdf", 1, 21]] #preferred start times for TeslaEV/etc pulled from database

    #output acceptable boolean
    shouldCharge = should_charge(user_model, best_threshold, flexible_loads, user_preferred_schedule, best_schedule_score)


    print(good_times)
    print(best_threshold, best_score)
    print(best_schedule, best_schedule_score)
    #print(shouldCharge)
    #print(calculate_shutOffRisk([]))
    #print(calculate_base_load("jasun_chen@ucsb.edu", 0, 100000))

    #how to handle charging into next day? 
    # [['2022-01-25 06:54:00', 0], ['2022-01-25 06:57:00', 20], ['2022-01-25 07:00:00', 111], 
    # ['2022-01-25 08:00:00', 15074], ['2022-01-25 09:00:00', 40679], ['2022-01-25 10:00:00', 71855], 
    # ['2022-01-25 11:00:00', 105750], ['2022-01-25 12:00:00', 138258], ['2022-01-25 13:00:00', 172954], 
    # ['2022-01-25 14:00:00', 212896], ['2022-01-25 15:00:00', 247190], ['2022-01-25 16:00:00', 271581], 
    # ['2022-01-25 17:00:00', 278946], ['2022-01-25 17:14:00', 279296], ['2022-01-25 17:28:00', 279296],
    # ['2022-01-26 06:54:00', 0], ['2022-01-26 06:57:00', 20], ['2022-01-26 07:00:00', 111], 
    # ['2022-01-26 08:00:00', 17616], ['2022-01-26 09:00:00', 53003], ['2022-01-26 10:00:00', 103323], 
    # ['2022-01-26 11:00:00', 163618], ['2022-01-26 12:00:00', 227571], ['2022-01-26 13:00:00', 289371],
    # ['2022-01-26 14:00:00', 341193], ['2022-01-26 15:00:00', 379470], ['2022-01-26 16:00:00', 400744],
    # ['2022-01-26 17:00:00', 406536], ['2022-01-26 17:15:00', 406836], ['2022-01-26 17:29:00', 406836]]