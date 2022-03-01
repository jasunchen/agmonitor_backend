import csv
from datetime import datetime
import xlrd

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


def parseExcel(fileName):
    workbook = xlrd.open_workbook(fileName)

    results = []


    for sheet in workbook.sheets():
        temp = []

        row_count = sheet.nrows
        col_count = sheet.ncols
        for i in range(1, row_count):
            if (i-1)%3 == 0:
                time = int((datetime.strptime((sheet.cell(i,0).value), '%Y-%m-%dT%H:%M:%S-08:00') - datetime(1970,1,1)).total_seconds())
                temp.append([time, convert5minKWintoWattHours(float(sheet.cell(i,1).value)), convert5minKWintoWattHours(float(sheet.cell(i,2).value)), convert5minKWintoWattHours(float(sheet.cell(i,3).value)), convert5minKWintoWattHours(float(sheet.cell(i,4).value))])

            else:
                index = int((i-1)/3)
                for j in range(1,5):
                    temp[index][j] = round(temp[index][j] + convert5minKWintoWattHours(float(sheet.cell(i,j).value)), 2)
        results.append(temp)

    return results