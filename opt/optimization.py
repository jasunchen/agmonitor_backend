import numpy as np
import random
from typing import List

class UserProfile:
  def __init__(self, weight1, weight2, weight3, lowerLimit, maximumLimit, shutOffRisk, idealReserveThreshold, solarForecast, baseForecast, currentBatteryState, batterySize):
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
    maxCharge = 0.37 * maxStorage #5 kW rate #825 #watt hours per 15 min increment or ~3.3 kWh
    maxDischarge = -0.37 * maxStorage #5 kW #1925 #watt hours per 15 min increment or ~7.7 kWh

    excessSolar = [0]*192 #if solar generation is too high
    excessBattery = [0]*192 #if battery storage is capped out
    utility = [0]*192
    battery = [0]*192

    #keep track of maximum costs to minmax normalize values 
    maxCostGrid = 0.01
    maxCostRenewableIntegration = 0.01

    thresholdWattHours = 0.01 *threshold*maxStorage #convert threshold percentage into watt hours
    minimumWattHours = 0.2*maxStorage

    for index, e in enumerate(energyFlow):
        # print("energyupdate", index, ": ", e,", currentCharge: ", currentCharge, ", costs:", costGrid, maxCostGrid, costGrid/maxCostGrid)
        if (e > 0): #producing excess solar energy
            currentCharge += min(e, maxCharge)
            excessSolar[index] += max(0, e-maxCharge)
            maxCostRenewableIntegration += e
            utility[index] += max(0, e-maxCharge)
            #print("pos:",e-maxCharge)
        else:
            currentCharge += max(e, maxDischarge) #max to take less negative number
            maxCostGrid += max(e, maxDischarge)*price
            utility[index] += min(0, e-maxDischarge) #-1000 - -1925 --> 925 --> 0, -2000 --1925 --> -75

        diff = currentCharge - thresholdWattHours if (index < 96) else currentCharge - minimumWattHours

        if (diff < 0):
            costGrid += diff*price
            currentCharge -= diff #todo maxcharge
        
        if (currentCharge > maxStorage): #wasted solar
            excess = currentCharge - maxStorage 
            costRenewableIntegration += excess
            excessBattery[index] += currentCharge
            currentCharge -= excess
        utility[index] = round((utility[index]/1000),4)
        battery[index] = round(currentCharge/1000,4)
        

    # cost to grid
    # wasted solar
    # excess solar (not wasted, could not capture bc of limitations)
    # excess battery (wasted)
    return (costGrid/maxCostGrid, costRenewableIntegration/maxCostRenewableIntegration, excessSolar, excessBattery, utility, battery)

def computeShutOffCost(shutOffRisk, idealReserveThreshold, threshold):
        return shutOffRisk * (1 - (threshold/idealReserveThreshold))


def thresholdCost(userProfile: UserProfile, threshold):
    #solarForecast -> 2 day forecasted solar production beginning from right now
    #batteryState -> batteryPercentage, maxCharge, maxDischarge

    energyFlow = computeEnergyFlow(userProfile.solarForecast, userProfile.baseForecast)
    costGrid, costRenewableIntegration, excessSolar, excessBattery, utility, battery= computePredictedBatteryChargeAndTotalCost(userProfile.currentBatteryState, energyFlow, threshold, userProfile.batterySize)
    costShutOff = computeShutOffCost(userProfile.shutOffRisk, userProfile.idealReserveThreshold, threshold)

    cost = userProfile.weight1*costGrid  + userProfile.weight2 * costRenewableIntegration + userProfile.weight3* costShutOff

    return (cost, excessSolar, excessBattery, utility, battery)

def find_optimal_threshold(userProfile: UserProfile):
    step_size = 20
    temp = 10

    initial_eval = thresholdCost(userProfile, userProfile.lowerLimit)[0]
    curr, curr_eval = userProfile.lowerLimit, initial_eval
    best, best_eval = curr, curr_eval
    best_solar, best_battery = [0]*96,[0]*96
    utility, battery = [0]*96, [0]*96

    for i in range(1000):
        candidate = curr + np.random.randn() * step_size
        candidate = max(userProfile.lowerLimit, candidate)
        candidate = min(userProfile.maximumLimit, candidate)
        candidate_eval, excessSolar, excessBattery, utility, battery = thresholdCost(userProfile, candidate)

        if candidate_eval < best_eval:
            best, best_eval, best_solar, best_battery = candidate, candidate_eval, excessSolar, excessBattery
            # print('>%d cost(%s) = %.5f' % (i, best, best_eval))
        diff = candidate_eval - curr_eval
        t = temp / float(i + 1)
        metropolis = np.exp(-diff / t)
        if diff < 0 or np.random.rand() < metropolis:
            curr, curr_eval = candidate, candidate_eval

    return [best, best_eval, best_solar, best_battery, utility, battery]

def flexibleLoadEnergyFlow(energyFlow, flexibleLoads: List[FlexibleLoad], schedule: List[List[int]]):
    maxTime = len(energyFlow) - 1
    for i in range(len(flexibleLoads)):
        loadCost = flexibleLoads[i].energyCost
        duration = flexibleLoads[i].duration
        isOn = schedule[i][1]
        beginTime = schedule[i][2]

        if isOn == 1:
            avgConsumption = loadCost/duration
            for t in range(beginTime, min(beginTime+duration, maxTime)):
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
    #print(costGrid/maxCostGrid,  costRenewableIntegration/maxCostRenewableIntegration)
    cost = (costGrid/maxCostGrid) + (costRenewableIntegration/maxCostRenewableIntegration)
    return (cost, excessSolar, excessBattery)

def find_good_times(userProfile: UserProfile, threshold, flexibleLoad: FlexibleLoad): #good times to start charging for one flexible load 
    schedule = [0]*96
    for i in range(96): 
        candidate_eval, excessSolar, excessBattery = flexibleLoadScheduleCost(userProfile, threshold, [flexibleLoad], [["temp", 1,i]])
        schedule[i] = candidate_eval
    minCost = min(schedule)
    maxCost = max(schedule)
    return ([round (1 - ((val - minCost) / max(maxCost - minCost, 0.01)), 2) for val in schedule], minCost)



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
    temp = 2

    initial_schedule = []
    for i in range(len(flexibleLoads)):
        initial_schedule.append([flexibleLoads[i].id, np.random.randint(2), np.random.randint(96)])
    initial_eval = flexibleLoadScheduleCost(userProfile, threshold, flexibleLoads, initial_schedule)[0]

    curr, curr_eval = initial_schedule, initial_eval
    best, best_eval = curr, curr_eval
    best_solar, best_battery = [],[]

    for epoch in range(10):
        # print("Epoch", epoch)
        for i in range(1000):
            candidate = create_candidate_schedule(curr, step_size, epoch)
            candidate_eval, excessSolar, excessBattery = flexibleLoadScheduleCost(userProfile, threshold, flexibleLoads, candidate)

            if candidate_eval < best_eval:
                best, best_eval, best_solar, best_battery = candidate, candidate_eval, excessSolar, excessBattery
                # print('>%d cost(%s) = %.5f' % (i, best, best_eval))
            diff = candidate_eval - curr_eval
            t = temp / float(i + 1)
            metropolis = np.exp(-diff / t)
            if diff < 0 or np.random.rand() < metropolis:
                curr, curr_eval = candidate, candidate_eval

    return best, best_eval, best_solar, best_battery

# def should_charge(userProfile: UserProfile, threshold, flexibleLoads: List[FlexibleLoad], schedule: List[List[int]], optimum: float):
#     #is performance better than not charging? 
#     cost = flexibleLoadScheduleCost(userProfile, threshold, flexibleLoads, schedule)[0]
#     return (cost-optimum <= 0.2)

def should_charge(userProfile: UserProfile, threshold, costOfSchedule):
    cost = flexibleLoadScheduleCost(userProfile, threshold, [], [[]])[0]
    # print(cost)
    return cost > costOfSchedule

if __name__ == "__main__":

    weight1 = 1 #importance of cost 
    weight2 = 1 #importance of renewable integ
    weight3 = 1 #importance of shutoff
    lowerLimit = 20
    maximumLimit = 90
    shutOffRisk = 0
    idealReserveThreshold = 80

    #solarForecast = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,10,10,10,10,40,60,80,100,15000,40579,71855, 80123, 90432, 100213, 123100, 130412, 123400, 102103, 105033, 90123, 70123, 15000, 5000,4000,3000,1999,500,50,10,10,10,10,10,10,10,10,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,10,10,10,10,40,60,80,100,15000,40579,71855, 80123, 90432, 100213, 123100, 130412, 123400, 102103, 105033, 90123, 70123, 15000, 5000,4000,3000,1999,500,50,10,10,10,10,10,10,10,10,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    #baseForecast = [1000]*192
    baseForecast = [123.57, 153.57, 173.57, 175.71, 150.71, 154.29, 133.57, 124.29, 119.29, 112.86, 101.43, 95.71, 100.0, 96.43, 102.14, 86.43, 102.86, 60.71, 53.57, 63.57, 62.14, 55.0, 48.57, 55.71, 55.0, 55.0, 59.29, 60.0, 65.0, 48.57, 45.71, 12.86, 3.57, 0.71, 0.71, 0.0, 0.0, 0.0, 0.0, 0.0, 0.71, 0.71, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.43, 4.64, 0.36, 0.71, 4.64, 1.79, 3.57, 0.36, 0.36, 0.0, 0.0, 0.0, 0.0, 0.36, 0.36, 0.0, 1.43, 0.71, 0.0, 0.0, 0.71, 0.0, 0.36, 16.79, 25.71, 23.57, 47.5, 83.57, 57.5, 73.57, 84.64, 95.36, 101.79, 121.79, 129.29, 115.71, 121.43, 123.21, 317.5, 295.36, 253.93, 237.86, 256.07, 260.36, 245.36, 217.5, 242.86, 230.71, 123.57, 153.57, 173.57, 175.71, 150.71, 154.29, 133.57, 124.29, 119.29, 112.86, 101.43, 95.71, 100.0, 96.43, 102.14, 86.43, 102.86, 60.71, 53.57, 63.57, 62.14, 55.0, 48.57, 55.71, 55.0, 55.0, 59.29, 60.0, 65.0, 48.57, 45.71, 12.86, 3.57, 0.71, 0.71, 0.0, 0.0, 0.0, 0.0, 0.0, 0.71, 0.71, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.43, 4.64, 0.36, 0.71, 4.64, 1.79, 3.57, 0.36, 0.36, 0.0, 0.0, 0.0, 0.0, 0.36, 0.36, 0.0, 1.43, 0.71, 0.0, 0.0, 0.71, 0.0, 0.36, 16.79, 25.71, 23.57, 47.5, 83.57, 57.5, 73.57, 84.64, 95.36, 101.79, 121.79, 129.29, 115.71, 121.43, 123.21, 317.5, 295.36, 253.93, 237.86, 256.07, 260.36, 245.36, 217.5, 242.86, 230.71]
    #solarForecast = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.5, 6.71, 78.05, 78.05, 78.05, 78.05, 141.86, 141.86, 141.86, 141.86, 264.33, 264.33, 264.33, 264.33, 326.81, 326.81, 326.81, 326.81, 360.75, 360.75, 360.75, 360.75, 472.2, 472.2, 472.2, 472.2, 453.98, 453.98, 453.98, 453.98, 362.26, 362.26, 362.26, 362.26, 321.52, 321.52, 321.52, 321.52, 105.11, 105.11, 105.11, 105.11, 31.17, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 3.0, 15.73, 210.82, 210.82, 210.82, 210.82, 431.02, 431.02, 431.02, 431.02, 622.24, 622.24, 622.24, 622.24, 744.35, 744.35, 744.35, 744.35, 785.77, 785.77, 785.77, 785.77, 771.45, 771.45, 771.45, 771.45, 678.9, 678.9, 678.9, 678.9, 516.03, 516.03, 516.03, 516.03, 317.11, 317.11, 317.11, 317.11, 103.91, 103.91, 103.91, 103.91, 31.17, 0.0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    #print(sum(baseForecast))
    #solarForecast = [0]*192
    #print(sum(solarForecast))



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
    good_times, costCharge = find_good_times(user_model, best_threshold, TeslaEV)
    # print(costCharge)

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

    print(should_charge(user_model, best_threshold, costCharge))
    #print(best_schedule, best_schedule_score)
    #print(shouldCharge)
    #print(calculate_shutOffRisk([]))

