import json
import os


class UserParams:
    def __init__(self, motionLimit, sensitivity, camFPS, record, drawBoxes):
        self.paramDict = {
            "motionLimit": motionLimit,
            "sensitivity": sensitivity,
            "camFPS": camFPS,
            "record": record,
            "drawBoxes": drawBoxes
        }
        # parameters stored as key-value pairs

    def getParams(self):
        return self.paramDict.values()

    def printParams(self):
        for x, y in self.paramDict.items():
            print(x, ": ", y)

    def importParams(self, inputFile):
        file = open(inputFile)
        data = json.load(file)
        for val in data:
            self.paramDict[val] = data[val]
        file.close()
        # get all the values from serialized json file

    def exportParams(self, outputFile):
        with open(outputFile, 'w') as outfile:
            json.dump(self.paramDict, outfile, indent=4)

        # export json to file path (overwriting file if it exists already)
