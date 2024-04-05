import yfinance as yf
import pandas as pd
import re
import json
from flask import request, Flask
from flask_cors import CORS
import math
from pythia_functions import *
    

aapl=yf.Ticker("aapl")
blnce=aapl.info
print(blnce)
#blnce.to_csv('info.csv', index=True)