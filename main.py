import yfinance as yf
import pandas as pd
import re
import json
from flask import request, Flask
from flask_cors import CORS
import math
from dict_make_functions import *
from income_statement import *
from cashflow_statement import *
from assets_balance_sheet import *
from liabilities_balance_sheet import *
from treasury_balance_sheet import *


app = Flask(__name__)
CORS(app)

@app.route('/main', methods=['POST'])
def main():
    ticker_symbol=getInput()
    if ticker_symbol is None:
        return 'Error: Ticker symbol not provided', 400
    ticker_data = yf.Ticker(ticker_symbol)
    table={}
    table['IS']=income_statement(ticker_data)
    table['ABS']=assets_balance_sheet(ticker_data)
    table['LBS']=liabilities_balance_sheet(ticker_data)
    table['TBS']=treasury_balance_sheet(ticker_data)
    table['CF']=cashflow(ticker_data)
    return table

if __name__ == '__main__':
    app.run(debug=True)







