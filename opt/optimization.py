from scipy.optimize import linprog
import numpy as np


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
    return min(1,(numberOfHours * avgBaseload) / batterySize)

def find_optimal_threshold(weight1, weight2, lowerLimit, maximumLimit, shutOffRisk, idealReserveThreshold):
    #obj = [weight1, weight2]
    availableRange = maximumLimit-lowerLimit
    cost = weight1*(1/(availableRange)) + weight2*( - shutOffRisk/idealReserveThreshold)

    obj = [cost]
    lhs_ineq = [[ -1], 
            [1]]  

    rhs_ineq = [-lowerLimit,  
            idealReserveThreshold]  
    lhs_eq = [[0]]     # eq constraint left side
    rhs_eq = [ weight2*(shutOffRisk) - weight1*(lowerLimit/availableRange)]       # eq constraint right side

    bnd = [(0, maximumLimit)]  # Bounds of x
    opt = linprog(c=obj, A_ub=lhs_ineq, b_ub=rhs_ineq, bounds=bnd, method="revised simplex")

    return opt["x"]



if __name__ == "__main__":
    weight1 = 0.4
    weight2 = 0.6
    lowerLimit = 10
    maximumLimit = 90
    shutOffRisk = 0.9
    idealReserveThreshold = 80
    print(calculate_shutOffRisk([1,2,"Warning"]))
    print(find_optimal_threshold(weight1, weight2, lowerLimit, maximumLimit, shutOffRisk,idealReserveThreshold))