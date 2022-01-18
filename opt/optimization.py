from scipy.optimize import linprog
import numpy as np



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
    print(find_optimal_threshold(weight1, weight2, lowerLimit, maximumLimit, shutOffRisk,idealReserveThreshold))