# This script takes two price streams and compares them for arbitrage opportunities. 
#
# To operate properly, it requires two CSV files with price and timing information, where the timestamp represents 
# the TIME AT WHICH THAT PRICE TAKES EFFECT (not to be confused with the hour-ending time). These times must be in a python-readable
# format (see https://docs.python.org/2/library/datetime.html#strftime-and-strptime-behavior). The script needs information on the 
# location (column) of the price and date data (within the CSV).
#
# readCSVs(file_to_read as String, number_of_header_rows as Integer, date_column as Integer, time_column as Integer, price_column as Integer
#
#
#

__author__ = 'luke.lavin'

import csv
import os
from readConfig import *
import math
from time import strftime

circleBack = ""

while circleBack=="":
    wenasFile = 'wenas_da.csv'
    goshenFile = 'Gosheni_cleaned_pacific_time_da.csv'
    sheridanFile = 'Sheridan_da.csv'
    monaFile = 'Mona_da.csv'
    allFiles = [wenasFile, goshenFile, sheridanFile, monaFile]
    thisWest = 0
    thisWestFile = ""
    
    AB_hourly = 'AB_Price_formatted.csv'
    AB_minutely = 'AB_SMP_formatted.csv'
    AB_prices = [AB_hourly, AB_minutely]
    thisAB = 0
    thisABFile = ""
    AB_prompt = "Select case: "
    print "Would you like to do an hourly or a minute-by-minute analysis?"
    print "    1: Hourly"
    print "    2: Minutely"
    while thisAB not in range(1,3):
        thisAB = int(input(AB_prompt))
        AB_prompt = "Invalid Entry. Select again: "
    
    thisABFile = AB_prices[thisAB - 1]
    print "---------------"
    
    W_prompt = "Select case: "
                       
    print "Which WEST hub would you like to use as a comparison point?"
    print "    1: Wenatchee"
    print "    2: Goshen"
    print "    3: Sheridan"
    print "    4: Mona"
    while thisWest not in range(1,5):
        thisWest = int(input(W_prompt))
        W_prompt = "Invalid Entry. Select again: "
    
    thisWestFile = allFiles[thisWest - 1]
    print "---------------"
    
    configFile = 'config_2way.csv'
    AESO_file = thisABFile
    WEST_file = thisWestFile
    Exchange_rate_file = 'CAD_US_ExchangeRate_2015.csv'
    directory = os.getcwd()
    
    to_config = directory+"\\"+configFile
    to_read = directory+"\\"+AESO_file
    to_compare = directory+"\\"+WEST_file
    Exchange_rate_doc = directory+"\\"+Exchange_rate_file
    
    AESO_price_list = []
    WEST_price_list = []
    Exchange_rate_list = []
    Exchange_adjusted_AESO_price_list = []
    
    if thisAB == 1:
        AESO_file_headers = 5 #number of rows to skip to get to data
        AB_time = 5
        AB_date = 5
        AB_price = 2
    else:
        AESO_file_headers = 3
        AB_time = 2
        AB_date = 1
        AB_price = 3
    WEST_file_headers = 1 #ibid
    Exchange_rate_headers = 1
    
    thisConfig = readConfigFile(to_config)
    
    ###READ CSVs and establish the time frame over which we have all three data points
    
    AESO_price_list = readCSVs(to_read, AESO_file_headers, AB_date, AB_time, AB_price, "%m/%d/%Y %H:%M", 0, 0, 0)
    minData = AESO_price_list[0][0]
    lowConstraint = "AESO Prices"
    maxData = AESO_price_list[-1][0]
    highConstraint = "AESO Prices"
    
    WEST_price_list = readCSVs(to_compare, WEST_file_headers, 17, 17, 14, "%m/%d/%Y %H:%M", 0, 0, 1)
    if WEST_price_list[0][0] > minData:
        minData = WEST_price_list[0][0]
        lowConstraint = "WEST Prices"
    if WEST_price_list[-1][0] < maxData:
        maxData = WEST_price_list[-1][0]
        highConstraint = "WEST Prices"
        
    Exchange_rate_list = readCSVs(Exchange_rate_doc, Exchange_rate_headers, 3, 3, 2, "%m/%d/%Y", 0, 0, 0)
    if Exchange_rate_list[0][0] > minData:
        minData = Exchange_rate_list[0][0]
        lowConstraint = "Exchange Rates"
    if Exchange_rate_list[-1][0] < maxData:
        maxData = Exchange_rate_list[-1][0]
        highConstraint = "Exchange Rates"
    
    maxData = datetime(maxData.year,maxData.month,maxData.day) + timedelta(days = 1)
    
    # allows user to change the duration of the analysis (i.e. focus on a single day)
    
    print "earliest start date for analysis: " + minData.strftime("%m/%d/%Y %H:%M") + " (" + lowConstraint + ")"
    newCons = raw_input("    would you like to start on a later date? input in mm/dd/yy form: ")
    if newCons != "":
        minData = datetime.strptime(newCons, "%m/%d/%y")
    print "------"
    print "latest end date for analysis: " + maxData.strftime("%m/%d/%Y %H:%M") + " (" + highConstraint + ")"
    newCons = raw_input("    would you like to end on an earlier date? input in mm/dd/yy form: ")
    if newCons != "":
        maxData = datetime.strptime(newCons, "%m/%d/%y")
    
    
    # figures out where in each data set the first applicable data point is located
    
    AESO_Pos = findIndex(AESO_price_list, minData)
    WEST_Pos = findIndex(WEST_price_list, minData)
    EX_Pos = findIndex(Exchange_rate_list, minData)
    
    thisStep = minData
    valueCalc = 0
    totalVal = 0
    fullRecord = []
    nullHrs = 0
    imHrs = 0
    exHrs = 0
    imVal = 0
    exVal = 0
    
    print("--------")
    print ("running analysis...")
    print("--------")
    
    while thisStep < maxData:
        valueCalc = comparePrices(AESO_price_list[AESO_Pos][1], WEST_price_list[WEST_Pos][1], thisConfig.losses, thisConfig.txPrice, Exchange_rate_list[EX_Pos][1])
        if AESO_Pos == len(AESO_price_list) - 1:
            nextAESO = maxData
        else:
            nextAESO = AESO_price_list[AESO_Pos+1][0]
        if WEST_Pos == len(WEST_price_list) - 1:
            nextWEST = maxData
        else:
            nextWEST = WEST_price_list[WEST_Pos+1][0]
        if EX_Pos == len(Exchange_rate_list) - 1:
            nextEX = maxData
        else:
            nextEX = Exchange_rate_list[EX_Pos+1][0]
        nextStep = min(nextAESO,nextWEST,nextEX, maxData)
        if nextStep == nextAESO:
            AESO_Pos += 1
        if nextStep == nextWEST:
            WEST_Pos += 1
        if nextStep == nextEX:
            EX_Pos += 1
        valDuration =  nextStep - thisStep
        hrDuration = valDuration.total_seconds() / 3600
        if valueCalc[0] != 0:
            thisVal = valueCalc[int(1.5+float(valueCalc[0])/2)] * hrDuration * thisConfig.txCap
            totalVal += thisVal
            if valueCalc[0] == 1:
                exHrs += hrDuration
                exVal += thisVal
            else:
                imHrs += hrDuration
                imVal += thisVal
        else:
            thisVal = 0
            nullHrs += hrDuration
        fullRecord.append([thisStep,nextStep,valueCalc[0],thisVal])
        thisStep = nextStep
        
    
    imValF = toCSVals(imVal)
    imHrsF = toCSVals(imHrs)
    if imHrs > 0:
        aveImVal = toCSVals (imVal / (imHrs * thisConfig.txCap))
    else:
        aveImVal = "n/a"
    exValF = toCSVals(exVal)
    exHrsF = toCSVals(exHrs)
    if exHrs > 0:
        aveExVal = toCSVals (exVal / (exHrs * thisConfig.txCap))
    else:
        aveExVal = "n/a"
    actHrsF = toCSVals(imHrs + exHrs)
    nullHrsF = toCSVals(nullHrs)
    totValF = toCSVals(totalVal)
    totHoursF = toCSVals(imHrs + exHrs + nullHrs)
    
    print "Import Value: $" + imValF + " in " + imHrsF + " hours ($" + aveImVal + " / MWh)"
    print "Export Value: $" + exValF + " in " + exHrsF + " hours ($" + aveExVal + " / MWh)"
    print "    Null Value in " + nullHrsF + " hours"
    print "--------"
    print "Total Value: $" + totValF + " in " + actHrsF + " hours of transacting"
    print "Total Hours Checked: " + totHoursF + " hours"
    print "--------"
    circleBack = raw_input("Press \"Enter\" to run another analysis or \"q\" to quit: ")
