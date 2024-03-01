import yfinance as yf

aapl=yf.Ticker("aapl")
blnce=aapl.income_stmt
blnce.to_csv('data3.csv', index=True)