import json
from splinter import Browser
from splinter.exceptions import ElementDoesNotExist
from webdriver_manager.chrome import ChromeDriverManager
import requests
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import pymongo
import os
from twilio.rest import Client
import pandas as pd
import threading, time, signal

from datetime import timedelta


#target = ["BTC","ETH","FIL","BTT","CELR"]
target = ["BTC"]
url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'
parameters = {
  'symbol': ",".join(target)
}
headers = {
  'Accepts': 'application/json',
  'X-CMC_PRO_API_KEY': 'eb6625b7-7916-468d-847f-df043c00fa98',
}

session = requests.Session()
session.headers.update(headers)

try:
    response = session.get(url, params=parameters)
    data = json.loads(response.text)
    
    df = pd.json_normalize(data["data"].values())
    fields = ["id", "name", "symbol", "cmc_rank", "quote.USD.price", "quote.USD.percent_change_24h", "quote.USD.volume_change_24h", "quote.USD.last_updated"]
    df_coins = df[fields].rename(columns={"id": "ID", "name": "Name", "symbol": "Symbol", "cmc_rank":"Rank", "quote.USD.price": "Price", "quote.USD.percent_change_24h": "24H % Changed", "quote.USD.volume_change_24h": "24H Volume Changed", "quote.USD.last_updated": "Update time"}).set_index("Symbol").sort_values(by=['Rank'])
    df_coins['Price'] = df_coins['Price'].map('${:,.5f}'.format)
    df_coins['24H % Changed'] = df_coins['24H % Changed'].map('{:.3}%'.format)
    df_coins['24H Volume Changed'] = df_coins['24H Volume Changed'].map('{:.4}%'.format)
    #df_coins['Update time'] = df_coins['Update time'].map(lambda a: a.replace("T", " ").replace("Z", ""))
    df_coins['Update time'] = pd.to_datetime(df_coins['Update time'])

    # account_sid = "AC594fb8a18edf1f24d2a7bd99d6869c57" 
    # auth_token = "42cafe56ea4357569dcc07f2b0ddb3e4"
    # client = Client(account_sid, auth_token)
    # message = client.messages.create(body= df_coins.to_string() ,from_='+12183216604', to=['+19787279830'])

    print(df_coins)
    #print(json.dumps(data, indent=4, sort_keys=True))
except (ConnectionError, Timeout, TooManyRedirects) as e:
    print(e)


