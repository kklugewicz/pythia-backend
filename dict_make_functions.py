import yfinance as yf
import pandas as pdaapl
import re
import json
import math
from flask import request, Flask
from flask_cors import CORS

def YearMake(statement):
    years = []
    pattern=r'\b\d{4}\b'
    num_rows=statement.shape[1]
    for i in range(num_rows):
        Year=str(statement.columns[i])
        Year=re.findall(pattern,Year)
        years.append(int(Year[0]))
    return years

def DictMake(statement,val):
    dict={}
    for index, row in statement.iterrows():
        dict[index] = row[statement.columns[val]]
    return dict

def categories_list(statement):
    row_names = statement.index.tolist()
    return row_names

def YeartoStat(statement):
    years=YearMake(statement)
    dict={}
    val=0
    for year in years:
        dict[year]=DictMake(statement,val)
        val=val+1
    return dict

def getInput():
    input_data=request.get_json()
    ticker_symbol1 = input_data['data']
    ticker_symbol=ticker_symbol1['ticker']
    return ticker_symbol

def process_data(data):
    processed_data = {}
    for year, values in data.items():
        processed_values = {}
        for key, value in values.items():
            if isinstance(value, float) and math.isnan(value):
                processed_values[key] = 0
            else:
                processed_values[key] = value
        processed_data[year] = processed_values
    return processed_data