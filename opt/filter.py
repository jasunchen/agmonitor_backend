
FILE_NAME = "data/filter.csv"

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