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

__author__ = 'doug allen'

import csv
import pandas
import os
import math
from time import strftime
import filecmp
from pathFuncs import *

outputDir = raw_input("Enter the directory where the output files are located: ")

currNames = []
for (dirpath, dirnames, filenames) in os.walk(outputDir):
    currNames = filenames
    break

compiled = [[]]

for file in currNames:
    if file[-3:] != "csv":
        continue
    else:
        file = outputDir + "\\" + file
        thisFile = readCSVFile(file)
        