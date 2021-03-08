from finviz.screener import Screener
import requests
from datetime import date
import pandas as pd
import os


mailgun_sandbox=os.environ.get('MAILGUN_SANDBOX')
mailgun_key=os.environ.get('MAILGUN_KEY')
to_email=os.environ.get('TO_EMAIL')

def send_email(title1, stocks1, title2, stocks2):
    try:
        df1 = pd.Series(stocks1).to_frame()
        df1.style.set_caption(title1)
        df2 = pd.Series(stocks2).to_frame()
        df2.style.set_caption(title2)


        request_url = 'https://api.mailgun.net/v2/{0}/messages'.format(mailgun_sandbox)
        request = requests.post(request_url, auth=('api', mailgun_key), 
        data={
        'from': 'finviz-notifierr@noreply.com',
        'to': to_email,
        'subject':'finviz notifier:' + str(date.today()),
        'html': df1.to_html()  + "\n\n" + df2.to_html()       
        })
        
        print ('Status: ',format(request.status_code))
        print ('Body: ',format(request.text))
    except Exception as e:
        print('An error occurred whilst sending an email: ',e)

################


def build (filters):
    stock_list = Screener(filters=filters, table='Performance', order='price')  # Get the performance table and sort it by price ascending

    # Export the screener results to .csv
    stock_list.to_csv("stock.csv")

    print(stock_list)
    map = {}
    for stock in stock_list:
        map[(stock['Ticker'])] = stock['Price']

    return map

   

################

filters1 = ['f', 'an_recom_sellworse,cap_smallover,fa_epsyoy1_o10,fa_fpe_low,ta_sma20_pa&ft=4&o=marketcap' ]
filters2 = ['f', 'fa_eps5years_pos,fa_epsqoq_o20,fa_epsyoy_o25,fa_epsyoy1_o15,fa_estltgrowth_pos,fa_roe_o15,sh_instown_o10,sh_price_o15,ta_highlow52w_a90h,ta_rsi_nos50&ft=4' ]

send_email('downgraded', build(filters1), 'dunno', build(filters2))


