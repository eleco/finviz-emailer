from finviz.screener import Screener
import requests
from datetime import date
import pandas as pd
import os


mailgun_sandbox=os.environ.get('MAILGUN_SANDBOX')
mailgun_key=os.environ.get('MAILGUN_KEY')
to_email=os.environ.get('TO_EMAIL')

def send_email(stocks):
    try:
        df = pd.Series(stocks).to_frame()
        
        request_url = 'https://api.mailgun.net/v2/{0}/messages'.format(mailgun_sandbox)
        request = requests.post(request_url, auth=('api', mailgun_key), 
        data={
        'from': 'finviz-notifierr@noreply.com',
        'to': to_email,
        'subject':'finviz notifier:' + str(date.today()),
        'html': df.to_html()        })
        
        print ('Status: ',format(request.status_code))
        print ('Body: ',format(request.text))
    except Exception as e:
        print('An error occurred whilst sending an email: ',e)

################

filters = ['f', 'an_recom_sellworse,cap_smallover,fa_fpe_low,ta_sma20_pa' ]  
stock_list = Screener(filters=filters, table='Performance', order='price')  # Get the performance table and sort it by price ascending

# Export the screener results to .csv
stock_list.to_csv("stock.csv")

print(stock_list)

################

filters = ['f', 'fa_eps5years_pos,fa_epsqoq_o20,fa_epsyoy_o10,fa_epsyoy1_o15,fa_estltgrowth_pos,sh_instown_o10,ta_highlow52w_a90h,ta_rsi_nos50,ta_sma20_pa,ta_sma50_pa' ]  
stock_list = Screener(filters=filters, table='Performance', order='price')  # Get the performance table and sort it by price ascending

# Export the screener results to .csv
stock_list.to_csv("stock.csv")

print(stock_list)

map = {}
for stock in stock_list:
    map[(stock['Ticker'])] = stock['Price']

send_email(map)

