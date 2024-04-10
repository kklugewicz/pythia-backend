import yfinance as yf
import pandas as pd
import re
import json
from flask import request, Flask
from flask_cors import CORS
import math
from pythia_functions import *
from valuation import *

def getInput():
    input_data=request.get_json()
    ticker_symbol1 = input_data['data']
    ticker_symbol=ticker_symbol1['ticker']
    return ticker_symbol

app = Flask(__name__)
CORS(app)

@app.route('/main', methods=['POST'])
def main():
    ticker_symbol=getInput()
    if ticker_symbol is None:
        return 'Error: Ticker symbol not provided', 400
    ticker_data = yf.Ticker(ticker_symbol)
    info=ticker_data.info
    table={}
    table['Summary']=info['longBusinessSummary']
    table['Company Name']=ticker_data.info['longName']
    table['IS']=final_dict(ticker_data,"income_statement")
    table['ABS']=final_dict(ticker_data,"assets_balance_sheet")
    table['LBS']=final_dict(ticker_data,"liabilities_balance_sheet")
    table['TBS']=final_dict(ticker_data,"treasury_balance_sheet")
    table['CF']=final_dict(ticker_data,"cashflow")
    table['Valuations']=valuation(table,ticker_data)
    table['Basics']=basic_info(table,ticker_data)
    print(table)
    return table

if __name__ == '__main__':
    app.run(debug=True)







