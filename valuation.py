import yfinance as yf
import pandas as pd
import re
import json
from flask import request, Flask
from flask_cors import CORS
import math
from pythia_functions import *

def aprocess_data(data):
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

def discounted_cashflow(table, ticker_data):
    discount_rate = 0.095
    perpetual_growth_rate = 0.025
    yearly_free_cash_flows = []
    data = table["CF"]
    keys = list(data.keys()) 
    keys.remove("YoY(past year)")  
    company_growth_rate = []

    for key in keys:
        year = data[key]
        free_cash_flow = year["Free Cash Flow"]
        yearly_free_cash_flows.append(free_cash_flow)

    print(yearly_free_cash_flows)

    for i in range(len(yearly_free_cash_flows) - 1):
        this_year = yearly_free_cash_flows[i]
        last_year = yearly_free_cash_flows[i + 1]
        growth_rate = (this_year - last_year) / last_year
        company_growth_rate.append(growth_rate)

    print(company_growth_rate)

    average_growth_rate = sum(company_growth_rate) / len(company_growth_rate)
    print(average_growth_rate)
    FFCF = []
    this_year_FCF = yearly_free_cash_flows[0]

    for i in range(9):  
        year_FFCF = this_year_FCF + (average_growth_rate * this_year_FCF)
        FFCF.append(year_FFCF)
        this_year_FCF = year_FFCF

    FFCF_terminal_value = (FFCF[8] * (1 + perpetual_growth_rate)) / (perpetual_growth_rate + discount_rate)
    print("FFCF8")
    print (FFCF[8])
    FFCF.append(FFCF_terminal_value)

    print("FFCF")
    print(FFCF)

    PV_FFCF = []
    for i in range(9):  
        PV = FFCF[i] / ((1 + discount_rate) ** (i + 1))
        PV_FFCF.append(PV)

    print(PV_FFCF)
    
    sum_PV_FFCF = sum(PV_FFCF)

    balance_sheet = ticker_data.balance_sheet
    balance_sheet = DictMake(balance_sheet, 0)  
    cash_and_equivalents = balance_sheet['Cash And Cash Equivalents']
    total_debt = balance_sheet['Total Debt']
    total_shares_outstanding = ticker_data.info.get('sharesOutstanding')
    equity_value = sum_PV_FFCF + cash_and_equivalents - total_debt
    dcf = equity_value / total_shares_outstanding
    print (dcf)
    return dcf
    
def growth_rate(table):
    data = table["IS"]
    keys = list(data.keys()) 
    earnings=[]
    keys.remove("YoY(past year)")  
    company_growth_rate = []

    for key in keys:
        year = data[key]
        year_earnings = year["Net Earnings"]
        earnings.append(year_earnings)

    for i in range(len(earnings) - 1):
        this_year = earnings[i]
        last_year = earnings[i + 1]
        growth_rate = (this_year - last_year) / last_year
        company_growth_rate.append(growth_rate)


    average_growth_rate = sum(company_growth_rate) / len(company_growth_rate)
    return average_growth_rate

def valuation(table,ticker_data):
    valuation_table={}
    valuation_table["Current Stock Price"]=ticker_data.info.get('currentPrice')
    valuation_table["Market Cap"]=ticker_data.info.get('marketCap')
    valuation_table["Trailing P/E"]=ticker_data.info.get('trailingPE')
    valuation_table["Forward P/E"]=ticker_data.info.get('forwardPE')
    valuation_table["Trailing PEG Ratio"]=ticker_data.info.get('trailingPegRatio')
    if type(ticker_data.info.get('freeCashflow')) == float:
        valuation_table["P/FCF"]=ticker_data.info.get('freeCashflow')/ticker_data.info.get('currentPrice')
    #valuation_table["Discounted CashFlow"]=discounted_cashflow(table,ticker_data)
    #earnings_growth_rate=growth_rate(table)
    #valuation_table["Peter Lynch's Valuation"]=(earnings_growth_rate+ticker_data.info.get('dividendYield'))/ticker_data.info.get('trailingPE')
    current_valuation_table={}
    current_valuation_table["current"]=valuation_table
    processed_data=aprocess_data(current_valuation_table)
    corrected_dict=keys_to_strings(processed_data)
    return corrected_dict
