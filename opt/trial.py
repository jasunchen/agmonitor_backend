import numpy as np
import random
from typing import List
from opti import *
from parse import *
from utility.solar import *
from utility.weather import get_alerts
from utility.schedulerHelper import *


alerts = []
solarForecast =  [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 8.0, 39.0, 65.0, 92.0, 131.0, 172.0, 234.0, 301.0, 366.0, 429.0, 498.0, 568.0, 633.0, 699.0, 762.0, 826.0, 880.0, 935.0, 984.0, 1048.0, 1094.0, 1138.0, 1176.0, 1213.0, 1239.0, 1266.0, 1283.0, 1300.0, 1307.0, 1315.0, 1312.0, 1304.0, 1285.0, 1269.0, 1240.0, 1213.0, 1176.0, 1140.0, 1095.0, 1049.0, 1109.0, 1068.0, 709.0, 709.0, 637.0, 704.0, 634.0, 564.0, 496.0, 426.0, 331.0, 237.0, 158.0, 80.0, 10.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 9.0, 38.0, 64.0, 90.0, 130.0, 171.0, 234.0, 296.0, 366.0, 433.0, 511.0, 590.0, 661.0, 736.0, 809.0, 878.0, 942.0, 1004.0, 1058.0, 1113.0, 1160.0, 1206.0, 1245.0, 1284.0, 1312.0, 1339.0, 1357.0, 1373.0, 1378.0, 1383.0, 1377.0, 1370.0, 1349.0, 1328.0, 1294.0, 1258.0, 1214.0, 1167.0, 1111.0, 1054.0, 1099.0, 1046.0, 671.0, 671.0, 602.0, 663.0, 597.0, 530.0, 464.0, 399.0, 309.0, 219.0, 146.0, 74.0, 9.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

apr28 = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 6, 36, 95, 175, 278, 360, 444, 535, 625, 709, 791, 866, 772, 538, 456, 493, 646, 614, 721, 757, 810, 861, 993, 1215, 1336, 1345, 1308, 1304, 1317, 1282, 1251, 1222, 1186, 1148, 1103, 1054, 1000, 945, 886, 824, 758, 685, 609, 527, 441, 352, 264, 183, 116, 64, 27, 8, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]


if __name__ == "__main__":
    firstTime = True
    #
    latitude = 34.463829
    longitude = -119.740647
    declination = 0.0
    azimuth = 180.0
    power = 5.8

    lowerLimit = 30
    maximumLimit = 100
    idealReserveThreshold = 80
    batterySize = 54000




    weight1 = 1
    weight2 = 2
    weight3 = 1







    if firstTime:
        solar = [[15 * i, 0] for i in range(192)]
        solar_data = getSolarData(latitude, longitude, declination, azimuth, power)
        for i in range(192):
            solar[i][1] += solar_data[1][i][1]
        solarForecast = [round(item[1], 4) * 1000 for item in solar]

        alerts = get_alerts(latitude, longitude)

    historical_baseload_avg = [202.81, 194.58, 201.93, 191.39, 182.69, 173.9, 152.74, 148.41, 156.21, 152.03, 145.35, 131.46, 145.11, 131.88, 113.24, 126.82, 123.58, 117.17, 105.16, 117.01, 124.4, 124.16, 136.53, 153.96, 195.83, 188.04, 206.4, 185.39, 157.31, 162.97, 167.69, 157.64, 154.85, 168.95, 180.86, 184.54, 188.6, 211.03, 239.68, 235.96, 240.09, 240.21, 255.46, 256.34, 271.9, 271.71, 284.37, 276.12, 274.44, 280.25, 273.16, 255.94, 259.27, 263.37, 258.82, 253.67, 237.28, 245.57, 238.39, 230.99, 213.81, 210.52, 219.89, 212.48, 199.15, 195.35, 218.14, 209.27, 190.1, 160.07, 153.15, 131.11, 114.27, 101.31, 101.25, 113.19, 118.95, 123.82, 125.34, 123.33, 125.79, 133.73, 128.9, 127.8, 129.78, 120.72, 125.98, 138.6, 139.75, 122.82, 124.05, 121.42, 195.17, 198.38, 219.35, 219.91]
    baseForecast = historical_baseload_avg * 2
    shutOffRisk = calculate_shutOffRisk(alerts)

    print("Shutoff risk at {} due to the following alerts: {}.".format(str(shutOffRisk), alerts))



    currentBatteryState = .9519 * batterySize


    costGrid, costRenewableIntegration, excessSolar, excessBattery, utility, temp_battery = computePredictedBatteryChargeAndTotalCost(currentBatteryState, computeEnergyFlow(apr28, historical_baseload_avg), 30 , batterySize)
    # print((temp_battery[95] *1000 )/batterySize)

    user_model = UserProfile(weight1, weight2, weight3, lowerLimit, maximumLimit, shutOffRisk, idealReserveThreshold, solarForecast, baseForecast, currentBatteryState, batterySize, 0, 96)
    TeslaEV = FlexibleLoad("Tesla EV", 1085.491, 20, 70)
    (best_threshold, best_performance, best_sol, best_batt, (cost, schedule, utility, battery), should_charge, solutions)= find_optimal_threshold_and_schedule(user_model, TeslaEV)
    
    #assume user follows recommended schedule
    battStateIfCharged = best_batt[95]*1000
    #assume never charge
    battStateIfNoCharge = battery[-1][95]*1000

    print("Results: Best threshold - {}, Should charge - {}, Best Solution - {}, EOD Battery Level w/ Recommendation - {}%, EOD Battery Level w/o Charge - {}. ".format( best_threshold, should_charge, scheduleToString(best_sol), round(battStateIfCharged  * 100 / batterySize, 2 ), round(battStateIfNoCharge  * 100 / batterySize, 2 )))



    best_batt = [round((item*1000*100) / batterySize, 2) for item in best_batt] #convert to battery percentage
    battery = [round((item*1000*100) / batterySize, 2) for item in battery[-1]] #convert to battery percentage

    print("DATA:")
    print("batt_rec = ", best_batt)
    print("batt_wo_charge = ", battery)
    print("solar_forecast = ", solarForecast)
    print("base_forecast = ", baseForecast)


