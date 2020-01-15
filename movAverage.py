import sys, getopt
import json
import datetime


def convertToDateTime(s):
    return datetime.datetime.strptime(s, '%Y-%m-%d %H:%M:%S.%f')


def getInputArgs(argv):
    input_file = ""
    window = 0

    usage = 'movAverage.py --input_file <inputfile.json> --window_size <window_size (minutes)>'

    try:
        opts, args = getopt.getopt(argv, "h", ["input_file=", "window_size="])
    except getopt.GetoptError:
        sys.exit(usage)

    for opt, arg in opts:
        if opt == '-h':
            sys.exit(usage)
        elif opt in ("--input_file"):
            input_file = arg
        elif opt in ("--window_size"):
            window = float(arg)
            if (window < 0):
                sys.exit('Window_size must be a positive number')

    return input_file, window


class MovingTimeAverage(object):

    def __init__(self, args):
        input_args = getInputArgs(args)

        # set input variables and load json file
        self.input_file = input_args[0]
        self.window = input_args[1]
        self.output = []  # there may be more efficient options rather than save all the data into a variable

        translation_data = json.loads(open(self.input_file).read())

        # set the first timestamp to appear as the floor (minutes) of the first timestamp in the translation data file
        self.firstTimestamp = convertToDateTime(translation_data[0]['timestamp'])
        self.firstTimestamp = self.firstTimestamp.replace(second=0, microsecond=0)

        # set the last timestamp to appear as the ceil (minutes) of the last timestamp in the translation data file
        self.lastTimestamp = convertToDateTime(translation_data[-1]['timestamp']) + datetime.timedelta(0, 60)
        self.lastTimestamp = self.lastTimestamp.replace(second=0, microsecond=0)

        # Create an object that is responsible for calculating the average of the data present in the translation
        # data file along time
        self.averageCalculator = MovingAverageCalculator(translation_data, self.firstTimestamp)

        self.calculateMovingAverage()

    def calculateMovingAverage(self):
        # calculate the total seconds between the first and last samples to process
        total_seconds = self.getTotalSeconds()

        for t in range(0, total_seconds + 1, 60):
            # create a new timestamp sample
            date = self.firstTimestamp + datetime.timedelta(0, t)

            # convert to minute unites for simplification
            minute_ticks = t / 60
            # calculate the moving average given the limits of the current window
            average = self.averageCalculator.getWindowAverage(minute_ticks - self.window, minute_ticks)

            #print(date, average)

            self.saveOutput(str(date), str(average))

        self.writeOutputToDisk()

    def getTotalSeconds(self):
        return int((self.lastTimestamp - self.firstTimestamp).total_seconds())

    def writeOutputToDisk(self):
        with open('output.json', 'w') as outfile:
            json.dump(self.output, outfile)

    def saveOutput(self, date, average):
        self.output.append({
            'date': date,
            'average_delivery_time': average
        })


class MovingAverageCalculator(object):

    def __init__(self, data, referenceTime):
        self.lower = 0  # pointer to the smallest event that is contained in the window
        self.upper = 0  # pointer to the next event to be contained in the window
        self.data = data  # translation events data
        self.refTime = referenceTime  # reference timestamp
        self.average = 0  # current average
        self.N = 0  # number of events that are currently being used to calculate the average

    def getWindowAverage(self, window_lower_bound, window_upper_bound):

        #if the event in with the lower pointer has a relative time (to the start) that is smaller than the lower
        # bound of the window, that means it was surpassed by the moving window and we must remove it from the average
        while (self.lower < len(self.data) and self.getMinuteTicks(self.lower) < window_lower_bound):
            self.removeFromAverage(self.getDelay(self.lower))
            self.lower += 1 #go to the next event

        # if the event in with the upper pointer has a relative time (to the start) that is smaller than the upper
        # bound of the window, that means it introduced in the moving window and we must add it from the average
        while (self.upper < len(self.data)) and self.getMinuteTicks(self.upper) <= window_upper_bound:
            if (self.getMinuteTicks(self.upper) > window_lower_bound): #should be larger than the lower bound in order
                # to not inlude events that are completly skipped by the window
                # (which happen for very small window sizes (< 1 minute) or very sparse data)
                self.addToAverage(self.getDelay(self.upper))
            self.upper += 1 #go to the next event

        return self.average

    def getMinuteTicks(self, indx):
        sampleTime = convertToDateTime(self.data[indx]['timestamp'])
        return ((sampleTime - self.refTime).total_seconds()) / 60

    def getDelay(self, idx):
        return self.data[idx]['duration']

    def removeFromAverage(self, value):
        # Remove a given element from the average in an iteratively way if there are elements in
        # the average set. If there is only one, than simply subtract
        if (self.N > 0):
            if (self.N == 1):
                self.average = self.average - value
            else:
                self.average = ((self.average * self.N) - value) / (self.N - 1)
            self.N -= 1

    def addToAverage(self, value):
        # add element to the average iteratively
        self.average = self.average + (value - self.average) / (self.N + 1)
        self.N += 1


if __name__ == '__main__':
    MovingTimeAverage(sys.argv[1:])
