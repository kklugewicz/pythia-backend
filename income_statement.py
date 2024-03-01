import yfinance as yf
import pandas as pd
import re
import json
from flask import request, Flask
from flask_cors import CORS
import math
from dict_make_functions import *

def add_categories(dict):
     output_dict = dict.copy()
     output_dict['Net Earnings'] = (output_dict.get('Operating Revenue', 0) - 
                                   output_dict.get('Cost of Revenue', 0) - 
                                   (output_dict.get('Operating Expense', 0) + 
                                    output_dict.get('Research And Development', 0) + 
                                    output_dict.get('Selling General And Administration', 0)) - 
                                   output_dict.get('Interest Expense', 0) - 
                                   output_dict.get('Tax Provision', 0) - 
                                   output_dict.get('Other Non Operating Income Expenses', 0) + 
                                   output_dict.get('Interest Income Non Operating', 0))
     output_dict['Gross Profit Margin'] = output_dict.get('Gross Profit', 0) / output_dict.get('Total Revenue', 1)
     output_dict['SGA%'] = output_dict.get('Selling General And Administration', 0) / output_dict.get('Gross Profit', 1)
     output_dict['R&D%'] = output_dict.get('Research And Development', 0) / output_dict.get('Gross Profit', 1)
     output_dict['Depreciation %'] = output_dict.get('Reconciled Depreciation', 0) / output_dict.get('Gross Profit', 1)
     output_dict['Operating Expense %'] = output_dict.get('Operating Expense', 0) / output_dict.get('Gross Profit', 1)
     output_dict['Net Earnings to Total'] = output_dict.get('Net Earnings', 0) / output_dict.get('Total Revenue', 1)
     output_dict['Interest Expense %'] = output_dict.get('Interest Expense', 0) / output_dict.get('Total Revenue', 1)
     return output_dict

#This function creates the dictionary for every year.
def IS_year_to_stat(statement):
    years=YearMake(statement)
    dict_={}
    val=0
    for year in years:
        dict_[year]=IS_Dict(statement,val)
        val=val+1
    return dict_

#This function creates the dictionaries of categories and values
def IS_Dict(statement,val):
    dict_ = DictMake(statement, val)
    dict_ = add_categories(dict_)
    all_categories = categories_list(statement)

    #This part of code removes unecessary categories
    select_category = ('SGA%', 'R&D%', 'Depreciation %', 'Operating Expense %', 'Interest Expense %','Total Revenue', 'Cost Of Revenue', 'Gross Profit', 'Gross Profit Margin', 'Pretax Income', 'Net Earnings', 'Basic EPS', 'Net Earnings to Total')
    for element in all_categories: 
        if element not in select_category:
            del dict_[element]

    return dict_


def income_statement(ticker_data):
    IS=ticker_data.income_stmt
    dict=IS_year_to_stat(IS)
    dict=process_data(dict)
    return dict
   

