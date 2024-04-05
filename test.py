import yfinance as yf
import pandas as pd
import re
import json
from flask import request, Flask
from flask_cors import CORS
import math
from pythia_functions import *
from valuation import *
    
ticker_data = yf.Ticker('aapl')
table={}
table['IS']=final_dict(ticker_data,"income_statement")
table['ABS']=final_dict(ticker_data,"assets_balance_sheet")
table['BSL']=final_dict(ticker_data,"liabilities_balance_sheet")
table['BST']=final_dict(ticker_data,"treasury_balance_sheet")
table['CF']=final_dict(ticker_data,'cashflow')
table['Valuation']=valuation(table,ticker_data)
print(table)

'''aapl=yf.Ticker("aapl")
blnce=aapl.financials
blnce.to_csv('finance.csv', index=True)'''