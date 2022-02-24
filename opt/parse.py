import csv
from datetime import datetime
def convert5minKWintoWattHours(power):
    return (power*1000)/12

def parse(fileName):
    file = open(fileName)
    csvreader = list(csv.reader(file))

    response = []

    for i in range (1, len(csvreader)):

        if (i-1)%3 == 0:
            time = int((datetime.strptime(csvreader[i][0], '%Y-%m-%dT%H:%M:%S-08:00') - datetime(1970,1,1)).total_seconds())
            response.append([time, convert5minKWintoWattHours(float(csvreader[i][1])), convert5minKWintoWattHours(float(csvreader[i][2])), convert5minKWintoWattHours(float(csvreader[i][3])), convert5minKWintoWattHours(float(csvreader[i][4])), int(csvreader[i][5])])
        else:
            index = int((i-1)/3)
            for j in range(1,5):
                response[index][j] = round(response[index][j] + convert5minKWintoWattHours(float(csvreader[i][j])), 2)

    home = [x[1] for x in response]
    solar = [x[2] for x in response]
    powerwall = [x[3] for x in response]
    grid = [x[4] for x in response]
    battery_level = [x[5] for x in response]

    return (home, solar, powerwall, grid, battery_level)