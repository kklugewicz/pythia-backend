import yfinance as yf
import pandas as pd
import re
import json
from flask import request, Flask
from flask_cors import CORS
import math

categories = {
    "SGA%": "%",
    "R&D%": "%",
    "Depreciation %": "%",
    "Operating Expense %": "%",
    "Interest Expense %": "%",
    "Operating Margin": "%",
    "Total Revenue": "$",
    "Cost Of Revenue": "$",
    "Gross Profit": "$",
    "Gross Profit Margin": "%",
    "Pretax Income": "$",
    "Net Earnings": "$",
    "Basic EPS": "$",
    "Net Earnings to Total": "%",
    "Cash And Cash Equivalents": "$",
    "Inventory": "$",
    "Receivables": "$",
    "Current Assets": "$",
    "Current Ratio": 'None',  # No symbol provided
    "Fixed Asset Turnover Ratio": 'None',  # No symbol provided
    "Total Non-Current Assets": "$",
    "Total Assets": "$",
    "Return on Asset Ratio": "%",
    "Payables And Accrued Expenses": "$",
    "Current Debt": "$",
    "Long Term Debt": "$",
    "Current Liabilities": "$",
    "Total Non Current Liabilities Net Minority Interest": "$",
    "Total Liabilities Net Minority Interest": "$",
    "Net Debt": "$",
    "Total Debt": "$",
    "Debt to Shareholders Equity Ratio": "%",
    "Common Stock": "$",
    "Retained Earnings": "$",
    "Treasury Shares Number": 'None',  # No symbol provided
    "Stockholders Equity": "$",
    "Return on Shareholders Equity": "%",
    "Free Cash Flow": "$",
    "Market Cap": "$",
    "EBITDA": "$",
    "Net Income": "$",
    "Net Income From Continuing Operations": "$",
    "Capital Expenditures %": "%",
    "Net Common Stock Issuance": "$",
    "Current Stock Price": "$",
    "Trailing P/E": "$",
    "Forward P/E": "$",
    "Trailing PEG Ratio": "$",
    "P/FCF": "$",
    "Discounted Cash Flow Model": "$",
    "Peter Lynch's Valuation": "$",
    "Benjamin Graham's Valuation": "$",
    "Multiples Valuation": "$",
    "Dividend Discount Mode":"$",
    "Total Non Current Assets":"$",
    "Treasury-adjusted Debt Shareholders Equity Ratio":"$"
}

def statement_create(ticker_data,statement_type):
    if statement_type=="income_statement":
        return ticker_data.income_stmt
    elif statement_type=="cashflow":
        return ticker_data.cashflow
    else:
        return ticker_data.balance_sheet

def select_list(statement_type):
    if statement_type=="income_statement":
        return ('SGA%', 'R&D%', 'Depreciation %', 'Operating Expense %', 'Interest Expense %','Operating Margin','Total Revenue', 'Cost Of Revenue', 'Gross Profit', 'Gross Profit Margin', 'Pretax Income', 'EBITDA','Net Earnings', 'Basic EPS', 'Net Earnings to Total')
    if statement_type=="cashflow":
        return ('Free Cash Flow','Net Income','Net Income From Continuing Operations','Capital Expenditures %', 'Net Common Stock Issuance')
    if statement_type=="assets_balance_sheet":
        return ('Cash And Cash Equivalents','Inventory', 'Receivables','Current Assets','Current Ratio','Fixed Asset Turnover Ratio','Total Non Current Assets','Total Assets','Return on Asset Ratio')
    if statement_type=="liabilities_balance_sheet":
        return ('Payables And Accrued Expenses','Current Debt', 'Long Term Debt','Current Liabilities','Total Non Current Liabilities Net Minority Interest','Total Liabilities Net Minority Interest','Net Debt','Total Debt','Debt to Shareholders Equity Ratio')
    if statement_type=="treasury_balance_sheet":
        return ('Common Stock','Capital Expenditures %','Retained Earnings','Treasury Shares Number','Stockholders Equity','Return on Shareholders Equity','Adjusted Return on Equity')
     
def add_categories(ticker_data,dict,statement_type,datestring):
    output_dict = dict.copy()
    financials=ticker_data.financials
    column_dates = pd.to_datetime(financials.columns)
    year=datestring.split('/')[2]
    for date in column_dates:
        if str(date.year) == year:
            use_year = date
    use_year = str(use_year.strftime('%Y-%m-%d'))
    output_dict['Net Income']=financials.loc['Net Income',use_year]
    if statement_type=="income_statement":
        output_dict['Net Earnings'] = (output_dict.get('Operating Revenue', 0) - 
                                    output_dict.get('Cost of Revenue', 0) - 
                                    (output_dict.get('Operating Expense', 0) + 
                                        output_dict.get('Research And Development', 0) + 
                                        output_dict.get('Selling General And Administration', 0)) - 
                                    output_dict.get('Interest Expense', 0) - 
                                    output_dict.get('Tax Provision', 0) - 
                                    output_dict.get('Other Non Operating Income Expenses', 0) + 
                                    output_dict.get('Interest Income Non Operating', 0))
        if type(output_dict.get('Operating Income'))== float:
            output_dict['Operating Margin']=output_dict.get('Operating Income')/output_dict.get('Total Revenue')
        if ("Gross Profit" in output_dict.keys()):
            output_dict['Gross Profit Margin'] = output_dict.get('Gross Profit', 0) / output_dict.get('Total Revenue', 1)
            output_dict['SGA%'] = output_dict.get('Selling General And Administration', 0) / output_dict.get('Gross Profit', 1)
            output_dict['R&D%'] = output_dict.get('Research And Development', 0) / output_dict.get('Gross Profit', 1)
            output_dict['Depreciation %'] = output_dict.get('Reconciled Depreciation', 0) / output_dict.get('Gross Profit', 1)
            output_dict['Operating Expense %'] = output_dict.get('Operating Expense', 0) / output_dict.get('Gross Profit', 1)
        output_dict['Net Earnings to Total'] = output_dict.get('Net Earnings', 0) / output_dict.get('Total Revenue', 1)
        output_dict['Interest Expense %'] = output_dict.get('Interest Expense', 0) / output_dict.get('Total Revenue', 1)
        return output_dict
    elif statement_type=="cashflow":
        output_dict['Capital Expenditures %'] = (output_dict.get('Capital Expenditure', 0) *-1) / output_dict['Net Income']
        return output_dict
    else:
        output_dict['Fixed Asset Turnover Ratio']=financials.loc['Total Revenue',use_year]/output_dict.get('Net PPE')
        if type(output_dict.get('Current Liabilities'))== float:
            output_dict['Current Ratio'] = output_dict.get('Current Assets', 0) / output_dict['Current Liabilities']
        output_dict['Return on Asset Ratio']= output_dict.get('Net Income', 0) / output_dict['Total Assets']
        output_dict['Debt to Shareholders Equity Ratio'] = output_dict.get('Total Debt', 0) / output_dict['Stockholders Equity']
        output_dict['Treasury-adjusted Debt Shareholders Equity Ratio']= output_dict.get('Total Liabilities Net Minority Interest', 0) / (output_dict['Stockholders Equity'] + output_dict['Capital Stock'])
        output_dict['Return on Shareholders Equity'] = output_dict.get('Net Income', 0) / output_dict['Stockholders Equity']
        return output_dict

def categories_list(statement):
    row_names = statement.index.tolist()
    return row_names

def dates_list(statement):
    years = []
    '''pattern=r'\b\d{4}\b'
    num_rows=statement.shape[1]
    for i in range(num_rows):
        Year=str(statement.columns[i])
        Year=re.findall(pattern,Year)
        years.append(int(Year[0]))'''
    pattern = r'\b(\d{4})-(\d{2})-(\d{2})\b'  # Regular expression pattern to match YYYY-MM-DD
    num_rows = statement.shape[1]
    for i in range(num_rows):
        year_month_day = str(statement.columns[i])  # Convert column name to string
        match = re.search(pattern, year_month_day)  # Search for the pattern in the column name
        if match:
            year = match.group(1)
            month = match.group(2)
            day = match.group(3)
            date_string = f"{month}/{day}/{year}"  # Construct the date string in MM/DD/YYYY format
            years.append(date_string)
    return years

def DictMake(statement,val):
    dict={}
    for index, row in statement.iterrows():
        dict[index] = row[statement.columns[val]]
    return dict

def yoy(dict,select_categories):
    yoy_dict={}
    years=list(dict.keys())
    thisyear=years[0]
    thisyear_dict=dict[thisyear]
    lastyear=years[1]
    lastyear_dict=dict[lastyear]
    for element in select_categories:
        if element not in lastyear_dict or element not in thisyear_dict:
            yoy_dict[element]=0
        elif lastyear_dict[element]==0:
            yoy_dict[element]=0
        elif lastyear_dict=='nan' or thisyear_dict=='nan': 
            yoy_dict[element]=0
        else:
            yoy_dict[element]=(thisyear_dict[element]-lastyear_dict[element])/lastyear_dict[element]
    return yoy_dict

def keys_to_strings(dict):
    return {str(key): value for key, value in dict.items()}

def process_data(dict,full_categories):
    processed_data={}
    for year in dict.keys():
        processed_year={}
        this_year=dict[year]
        for category in this_year.keys():
            if category in full_categories.keys():
                value_type=full_categories[category]
            else:
                value_type='None'
            val=this_year[category]
            if val == 0:
                val = 0
            elif value_type=='$':
                if val >= 1_000_000_000 or val <= -1_000_000_000:
                    val = f"{val / 1_000_000_000:.1f}B"
                elif val >= 1_000_000 or val <= -1_000_000:
                    val = f"{val / 1_000_000:.1f}M"
                elif val >= 1_000 or val <= -1_000:
                    val = f"{val / 1_000:.1f}K"
                else:
                    val = f"{val:.3f}"
                val='$'+val
                processed_year[category]=val
            elif value_type=='None':
                val = str("{:.2f}".format(val))
                processed_year[category]=val
            elif value_type=='%':
                val=float(val)
                val=val*100
                val= f"{val:.1f}%"
                processed_year[category]=val
        processed_data[year]=processed_year
    yoydict=dict["YoY"]
    processed_year={}
    for category in yoydict.keys():
        val=yoydict[category]
        if val==0:
            val=0
        else:
            val=float(val)
            val=val*100
            val= f"{val:.2f}%"
            processed_year[category]=val
    processed_data["YoY"]=processed_year
    return processed_data

def add_quarterly(dict,ticker_data,statement_type):
    if statement_type=="income_statement":
        statement = ticker_data.quarterly_income_stmt
    elif statement_type=="cashflow":
        statement = ticker_data.quarterly_cashflow
    else:
        statement = ticker_data.quarterly_balance_sheet
    years = []
    pattern = r'\b(\d{4})-(\d{2})-(\d{2})\b'  # Regular expression pattern to match YYYY-MM-DD
    num_rows = statement.shape[1]
    for i in range(num_rows):
        year_month_day = str(statement.columns[i])  # Convert column name to string
        match = re.search(pattern, year_month_day)  # Search for the pattern in the column name
        if match:
            year = match.group(1)
            month = match.group(2)
            day = match.group(3)
            date_string = f"{month}/{day}/{year}"  # Construct the date string in MM/DD/YYYY format
            years.append(date_string)
    final_quarter=years[len(years)-4]
    formated_quarter=format_date(final_quarter)
    quarter_dict=DictMake(statement,len(years)-4)
    quarter_dict=add_categories(ticker_data,quarter_dict,statement_type,final_quarter)
    dict[formated_quarter]=quarter_dict
    return dict

def format_date(date_string):
    # Split the date string into month, day, and year components
    month, day, year = date_string.split('/')

    # Convert the month component to an integer
    month = int(month)

    # Determine the quarter based on the month
    if 1 <= month <= 3:
        quarter = 'Q1'
    elif 4 <= month <= 6:
        quarter = 'Q2'
    elif 7 <= month <= 9:
        quarter = 'Q3'
    else:
        quarter = 'Q4'

    # Return the formatted quarter and year
    return f"{quarter} {year}"

def yearly_dict(ticker_data,statement_type):
    statement=statement_create(ticker_data,statement_type)
    dates=dates_list(statement)
    if len(dates)>4:
        dates=dates[:-1]
    complete_dict={}
    val=0
    for date in dates:
        basic_dict=DictMake(statement,val)
        full_dict=add_categories(ticker_data,basic_dict,statement_type,date)
        formated_date=format_date(date)
        complete_dict[formated_date]=full_dict
        val=val+1
    complete_dict["YoY"]=yoy(complete_dict,full_dict.keys())
    processed_data=process_data(complete_dict,categories)
    corrected_dict=keys_to_strings(processed_data)
    return corrected_dict

