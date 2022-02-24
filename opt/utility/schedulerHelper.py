def findRange(arr): 
    continuous = False
    ranges = []
    for index, i in enumerate(arr):
        if i == 1:
            if continuous == False:
                continuous = True 
                ranges.append([index, index+1])
        elif len(ranges) != 0 and continuous == True:
            continuous = False
            ranges[-1][-1] = index
    return ranges

def convertIndexToTime(index): #0-96, 0 being 00:00, 96 being 24:00
	if (index == 96):
		return "11:59 PM"

	hours = index // 4
	minutes = (index % 4)*15
	if minutes == 0:
		minutes = "00"

	time = "AM"
	if hours >= 12:
		hours -= 12
		time = "PM"

	if hours == 0:
		hours = 12

	return "{}:{} {}".format(hours, minutes, time)


def convertRangeToTimes(arr):
	length = len(arr)
	output = ""
	for index, ele in enumerate(arr):
		if (ele[0] == ele[1]):
			output += convertIndexToTime(ele[0])
		else:
			output += convertIndexToTime(ele[0]) + " to " + convertIndexToTime(ele[1])

		if (index == length - 2):
			output += ", and "
		else: 
			output += ", "

	return output[:-2]

if __name__ == "__main__":
	# arr = [1,1,0,1,0,1,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,1,1,1]
	arr = [0]*96 + [0]
	arr[95] = 1
	print(findRange(arr))
	print(convertRangeToTimes(findRange(arr)))