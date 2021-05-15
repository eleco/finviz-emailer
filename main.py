from finviz.screener import Screener
import requests
from datetime import date
import pandas as pd
import os
import yfinance as yf
import boto3
import pickle
import json



aws_access_key= os.environ.get('AWS_ACCESS_KEY')
aws_secret_key= os.environ.get('AWS_SECRET_KEY')
mailgun_sandbox=os.environ.get('MAILGUN_SANDBOX')
mailgun_key=os.environ.get('MAILGUN_KEY')
to_email=os.environ.get('TO_EMAIL')


stocks_name ={}
s3 = boto3.client(
    's3',
    aws_access_key_id=aws_access_key,
    aws_secret_access_key=aws_secret_key
)
try:
    object = s3.get_object(Bucket='eleco-finviz',Key='EmpId007')
    serializedObject = object['Body'].read()
    stocks_name = pickle.loads(serializedObject)
    print ('stocks name:', stocks_name)
except:
    print ("no such key in bucket")


def send_email(title1, stocks1, title2, stocks2, title3, stocks3, title4, stocks4, title5, stocks5, title6, stocks6):
    try:
        df1 = pd.Series(stocks1).to_frame()
        df2 = pd.Series(stocks2).to_frame()
        df3 = pd.Series(stocks3).to_frame()
        df4 = pd.Series(stocks4).to_frame()
        df5 = pd.Series(stocks5).to_frame()
        df6 = pd.Series(stocks6).to_frame()

        request_url = 'https://api.mailgun.net/v2/{0}/messages'.format(mailgun_sandbox)
        request = requests.post(request_url, auth=('api', mailgun_key), 
        data={
        'from': 'finviz-notifierr@noreply.com',
        'to': to_email,
        'subject':'finviz notifier:' + str(date.today()),
        'html': 
        "<h1>" + title1 + "</h1>\n" + df1.to_html()  + "\n\n"
        "<h1>" + title2 +"</h1>\n" + df2.to_html()        + "\n\n"
        "<h1>" + title3 +"</h1>\n" + df3.to_html()        + "\n\n"
        "<h1>" + title4 +"</h1>\n" + df4.to_html()     + "\n\n"
        "<h1>" + title5 +"</h1>\n" + df5.to_html()     + "\n\n"
        "<h1>" + title6 +"</h1>\n" + df6.to_html()     
        
        
        })
        
        print ('Status: ',format(request.status_code))
        print ('Body: ',format(request.text))
    except Exception as e:
        print('An error occurred whilst sending an email: ',e)

################


def build (filters):
    map = {}
    try:
        stock_list = Screener(filters=filters, table='Performance', order='price')  # Get the performance table and sort it by price ascending

        print(stock_list)
        
        for stock in stock_list:
            
            if stock['Ticker'] in  stocks_name:
                name = stocks_name[stock['Ticker']]
            else:
                print('fetching stock ticker from yahoo:', stock['Ticker'])
                msft = yf.Ticker(stock['Ticker'])
                stocks_name[stock['Ticker']] = msft.info['longName'] 
                name = msft.info['longName']
            
            map[(stock['Ticker'])] = name #+ ' --> ' +stock['Price']
    except Exception as e:
        print(e)

    return map


################

downgraded_on_up = ['f', 'an_recom_sellworse,cap_smallover,fa_epsyoy1_o10,fa_fpe_low,ta_sma20_pa&ft=4&o=marketcap' ]
breakout = ['f', 'cap_midover,fa_debteq_u1,fa_roe_o20,sh_avgvol_o200,ta_changeopen_u,ta_highlow50d_nh,ta_sma20_pa,ta_sma200_pa,ta_sma50_pa&ft=4&o=-perf1w']
low_pe = ['f', 'cap_smallover,fa_pb_low,fa_pe_low,fa_peg_low,fa_roa_pos,fa_roe_pos,sh_price_o5,ta_sma50_pa&ft=4&o=-perfytd']
canslim = ['f', 'fa_eps5years_o20,fa_epsqoq_o20,fa_epsyoy_o20,fa_sales5years_o20,fa_salesqoq_o20,sh_curvol_o200,ta_sma200_pa&ft=4&r=21']
trend_and_hammer = ['f','sh_avgvol_o500,sh_short_o5,ta_candlestick_h,ta_changeopen_u,ta_pattern_wedge,ta_sma20_pa,ta_sma200_pa,ta_sma50_pa&ft=3']
trendline_support= ['f','sh_avgvol_o500,sh_short_o5,ta_changeopen_u,ta_pattern_tlsupport,ta_rsi_nob60,ta_sma20_pa,ta_sma200_pa,ta_sma50_pa&ft=4&r=21']

stocks_downgraded_on_up = build(downgraded_on_up)
stocks_breakout = build(breakout)
stocks_low_pe = build(low_pe)
stocks_canslim = build(canslim)
stocks_trend_hammer = build(trend_and_hammer)
stocks_trendline = build(trendline_support)


#Write to S3 using unique key - EmpId007
print('write stocks name into s3')
serializedMyData = pickle.dumps(stocks_name)
s3.put_object(Bucket='eleco-finviz',Key='EmpId007', Body=serializedMyData)

#write finviz results to s3
s3.put_object(Bucket='eleco-finviz',Key='downgraded_on_up', Body=downgraded_on_up)
s3.put_object(Bucket='eleco-finviz',Key='breakout', Body=stocks_breakout)
s3.put_object(Bucket='eleco-finviz',Key='low_pe', Body=stocks_low_pe)
s3.put_object(Bucket='eleco-finviz',Key='canslim', Body=stocks_canslim)
s3.put_object(Bucket='eleco-finviz',Key='trend_hammer', Body=stocks_trend_hammer)
s3.put_object(Bucket='eleco-finviz',Key='trend_hammer', Body=stocks_trend_hammer)



print('sending email')
send_email(
    'downgraded on the up', stocks_downgraded_on_up , 
    'breaking out', stocks_breakout, 
    'low PE value', stocks_low_pe,
    'CANSLIM', stocks_canslim,
    'trend_hammer', stocks_trend_hammer,
    'trendline', stocks_trendline
    )


