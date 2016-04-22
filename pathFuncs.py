'''
Created on Apr 20, 2016

@author: doug
'''


import csv
from datetime import *
from time import strptime

class configs:
    def __init__(self):
        self.losses = 0
        self.txPrice = 0
        self.txCap = 0


def readCSVFile(filePath):
    headings = []
    values = []
    thisConfig = configs()
    with open(filePath) as csvfile:
        firstRow = 0
        fileRead = csv.reader(csvfile, delimiter=',')
        for row in fileRead:
            if firstRow == 0:
                headings = fileRead
            else:
                values.append(fileRead)
    return thisConfig

def readCSVs(fileName, headers, dateCol, timeCol, priceCol, dateF, inDst = 0, exRateSwitch = 0, tzAdj = 0):
    parsedCSV = []    
    format = ""
    
    with open(fileName,'rU') as csvfile:
        csvreader = csv.reader(csvfile,delimiter =',')
        for x in range(headers):
            next(csvreader,None) #skip headers
        for row in csvreader:
            if timeCol == dateCol:
                parsedCSV.append([row[dateCol - 1],row[priceCol - 1]])
            else:
                parsedCSV.append([row[dateCol - 1] + " " + row[timeCol - 1],row[priceCol - 1]])
            format = dateF
            if exRateSwitch == 0:
                parsedCSV[-1][1] = float(parsedCSV[-1][1])
            else:
                parsedCSV[-1][1] = 1/float(parsedCSV[-1][1])
            if parsedCSV[-1][0][-1:] == "*":
                inDst = 1 - inDst
                parsedCSV[-1][0] = parsedCSV[-1][0][:-1]
            parsedCSV[-1][0] = datetime.strptime(parsedCSV[-1][0], format) + timedelta(hours = tzAdj)
            if inDst == 1:
                parsedCSV[-1][0] = parsedCSV[-1][0] - timedelta(hours = 1)
    return parsedCSV

def comparePrices(abPrice, usPrice, losses, txPrice, CADperUSD):
    imex = 0
    
    imValue = abPrice * (1 - losses) - usPrice * CADperUSD
    exValue = usPrice * CADperUSD - abPrice - txPrice
    if (imValue > 0) & (imValue > exValue):
        imex = -1
#         print ("        AESO            " + "$%2f" % imValue)
    elif exValue > 0:
        imex = 1
#         print ("                Frannie " + "$%2f" % exValue)
#     else:
#         print("none")
    return [imex, imValue, exValue]

def findIndex(priceList,minVal):
    list_start = 0
    
    for i in range(len(priceList)):
        if priceList[i][0] > minVal:
            list_start = i - 1
            break
        elif priceList[i][0] == minVal:
            list_start = i
            break
    return list_start

def toCSVals(convVal):
    convStringF = "{:,.2f}".format(convVal)
    return convStringF
