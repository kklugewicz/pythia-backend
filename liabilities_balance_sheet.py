import yfinance as yf
import pandas as pd
import re
import json
from flask import request, Flask
from flask_cors import CORS
import math
from dict_make_functions import *

def add_categories(dict,ticker_data):
     output_dict = dict.copy()
     financials=ticker_data.financials
     column_dates = pd.to_datetime(financials.columns)
     latest_date=column_dates[0]
     latest_date = str(latest_date.strftime('%Y-%m-%d'))
     output_dict['Net Income']=financials.loc['Net Income',latest_date]
     output_dict['Current Ratio'] = output_dict.get('Current Assets', 0) / output_dict['Current Liabilities']
     output_dict['Return on Asset Ratio']= output_dict.get('Net Earnings', 0) / output_dict['Total Assets']
     output_dict['Debt to Shareholders Equity Ratio'] = output_dict.get('Total Liabilities Net Minority Interest', 0) / output_dict['Stockholders Equity']
     output_dict['Treasury-adjusted Debt Shareholders Equity Ratio']= output_dict.get('Total Liabilities Net Minority Interest', 0) / (output_dict['Stockholders Equity'] + output_dict['Capital Stock'])
     output_dict['Return on Shareholders Equity'] = output_dict.get('Net Income', 0) / output_dict['Stockholders Equity']
     output_dict['Adjusted Return on Equity'] = output_dict.get('Net Income', 0) / (output_dict['Stockholders Equity'] + output_dict['Capital Stock'])
     return output_dict

#This function creates the dictionary for every year.
def BS_year_to_stat(statement,ticker_data):
    years=YearMake(statement)
    dict_={}
    val=0
    for year in years:
        dict_[year]=BS_Dict(statement,ticker_data,val)
        val=val+1
    return dict_

#This function creates the dictionaries of categories and values
def BS_Dict(statement,ticker_data,val):
    dict_ = DictMake(statement, val)
    dict_ = add_categories(dict_,ticker_data)
    all_categories = categories_list(statement)

    #This part of code removes unecessary categories
    select_category = ('Payables And Accrued Expenses','Current Debt', 'Long Term Debt','Current Liabilities','Total Non Current Liabilities Net Minority Interest','Total Liabilities Net Minority Interest','Debt to Shareholders Equity Ratio','Treasury-Adjusted Debt Shareholders Equity Ratio')

    for element in all_categories.copy():
        if element not in select_category:
            del dict_[element]
    return dict_


def liabilities_balance_sheet(ticker_data):
    BS=ticker_data.balance_sheet
    dict=BS_year_to_stat(BS,ticker_data)
    dict=process_data(dict)
    return dict
   

