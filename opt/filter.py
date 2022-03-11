
FILE_NAME = "data/meterdata214.csv"

def checkNextFour(data, ind, cutoff):
  for i in range(1,8):
    if (data[ind + i] < cutoff):
      return False
  return True
  
def filter(data, cutoff, noiseCutoff):
  #returns filtered base load and flex load 
  baseload = [0]*len(data)
  flexibleload = [0]*len(data)

  #base load should not be above 
  baseAcc= 0.5 #divide by index+1 to get avg
  flexAcc = 1.5
  currentlyFlexible = False #whether or not last datapoint was classified as flex

  for index, e in enumerate(data):
    lastHourAvg = sum(data[index-4:index]) / 4
    isFlex = (e >= cutoff and (currentlyFlexible or ( (e - lastHourAvg > noiseCutoff) and checkNextFour(data, index, cutoff) ) )) #check to see if greater than our cutoff, then make sure that either we're already looking at a flex or that the increase is sufficient to classify this as flex
    #isFlex = e >= cutoff
    if isFlex:
      #flex load occuring
      currentlyFlexible = True
      flexAcc += (e - baseAcc/(index+1))
      estimatedbaseload = baseAcc / (index+1)
      baseAcc += estimatedbaseload
      baseload[index] = estimatedbaseload
      flexibleload[index] = e-estimatedbaseload


    
    else:
      #only base load
      currentlyFlexible = False
      baseload[index] = e
      baseAcc += e




  return baseload, flexibleload, (baseAcc / (len(data) + 1))


file = open(FILE_NAME, "r").read()
lyst = list()
time_list = list()
consumed = list()
produced = list()

for line in file.split("\n")[:-1]:
    t = line.strip("\r").split(",")
    time_list.append(t[0])
    consumed.append(float(t[1]))
    produced.append(float(t[2]))


print(produced)         