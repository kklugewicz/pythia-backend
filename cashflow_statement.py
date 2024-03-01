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
     output_dict['Capital Expenditures %'] = output_dict.get('Capital Expenditure', 0) / output_dict['Net Income']
     return output_dict

#This function creates the dictionary for every year.
def CF_year_to_stat(statement,ticker_data):
    years=YearMake(statement)
    dict_={}
    val=0
    for year in years:
        dict_[year]=CF_Dict(statement,ticker_data,val)
        val=val+1
    return dict_

#This function creates the dictionaries of categories and values
def CF_Dict(statement,ticker_data,val):
    dict_ = DictMake(statement, val)
    dict_ = add_categories(dict_,ticker_data)
    all_categories = categories_list(statement)
    #This part of code removes unecessary categories
    select_category = ('Net Income','Net Income From Continuing Operations','Capital Expenditures %', 'Net Common Stock Issuance')
    for element in all_categories: 
        if element not in select_category:
            del dict_[element]
    return dict_


def cashflow(ticker_data):
    CF=ticker_data.cashflow
    dict=CF_year_to_stat(CF,ticker_data)
    dict=process_data(dict)
    return dict
   

