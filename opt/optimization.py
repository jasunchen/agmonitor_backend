from scipy.optimize import linprog
import numpy as np



def find_optimal_threshold(weight1, weight2, lowerLimit, maximumLimit, shutOffRisk, idealReserveThreshold):
    #obj = [weight1, weight2]
    availableRange = maximumLimit-lowerLimit

    lhs_ineq = [[-1, 0]]
    rhs_ineq = [-lowerLimit]

    cost = weight1*(1/(availableRange)) - weight2*(shutOffRisk/idealReserveThreshold)

    obj = [cost]
    lhs_ineq = [[ -1], 
            [1]]  

    rhs_ineq = [-lowerLimit,  
            maximumLimit]  
    # lhs_eq = [[-1]]     # eq constraint left side
    # rhs_eq = [15]       # eq constraint right side

    bnd = [(0, maximumLimit)]  # Bounds of x
    opt = linprog(c=obj, A_ub=lhs_ineq, b_ub=rhs_ineq, bounds=bnd, method="revised simplex")

    return opt["x"]



if __name__ == "__main__":
    weight1 = 0.5
    weight2 = 0.5
    lowerLimit = 10
    maximumLimit = 90
    shutOffRisk = 1
    idealReserveThreshold = 80
    print(find_optimal_threshold(weight1, weight2, lowerLimit, maximumLimit, shutOffRisk,idealReserveThreshold))