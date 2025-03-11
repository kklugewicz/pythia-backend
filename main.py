import yfinance as yf
import pandas as pd
import re
import json
from flask import request, Flask
from flask_cors import CORS
import math
from yearly_pythia_functions import *
from quarterly_pythia_functions import *
from valuation import *

def getInput():
    input_data=request.get_json()
    data = input_data['data']
    return data

app = Flask(__name__)
CORS(app)

@app.route('/main', methods=['POST'])
def main():
    data=getInput()
    ticker_symbol=data['ticker']
    ticker_symbol=ticker_symbol.replace(" ","")
    span=data['timeframe']
    print(data)
    if ticker_symbol is None:
        return 'Error: Ticker symbol not provided', 400
    ticker_data = yf.Ticker(ticker_symbol)
    #info=ticker_data.info
    table={}
    table['Summary']='Sorry not available at this time'
    #table['Summary']=info['longBusinessSummary']
    #table['Company Name']=ticker_data.info['longName']
    table['Company Name']="not available"
    if span=='Yearly':
        table['IS']=yearly_dict(ticker_data,"income_statement")
        table['ABS']=yearly_dict(ticker_data,"assets_balance_sheet")
        table['LBS']=yearly_dict(ticker_data,"liabilities_balance_sheet")
        table['TBS']=yearly_dict(ticker_data,"treasury_balance_sheet")
        table['CF']=yearly_dict(ticker_data,"cashflow")
    if span=='Quarterly':
        table['IS']=quarterly_dict(ticker_data,"income_statement")
        table['ABS']=quarterly_dict(ticker_data,"assets_balance_sheet")
        table['LBS']=quarterly_dict(ticker_data,"liabilities_balance_sheet")
        table['TBS']=quarterly_dict(ticker_data,"treasury_balance_sheet")
        table['CF']=quarterly_dict(ticker_data,"cashflow")
    table['Valuations']=valuation(table,ticker_data)
    table['Basics']=basic_info(table,ticker_data)
    return table

if __name__ == '__main__':
    app.run(debug=True)







