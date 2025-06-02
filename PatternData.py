import os
import pandas as pd
import json

os.chdir('/Users/amankazi/CongressTradeTracker/historicData/Stocks')

files = os.listdir('.') 

for f in files:
    with open('/Users/amankazi/CongressTradeTracker/historicData/Stocks/' + f , "r") as dir:
        print(dir.read())





