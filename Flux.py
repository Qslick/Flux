import ccxt
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta, timezone
import math
import argparse
from decimal import *
import requests
import json
from pprint import pprint
import datetime
import time


with open('credentials.json') as cred_file:
        credentials = json.load(cred_file)


coinbase_pro = ccxt.coinbasepro({
    'apiKey': credentials['coinbase']['apiKey'],
    'secret': credentials['coinbase']['secret'],
    'password': credentials['coinbase']['password']
    })

binance = ccxt.binance({
    'apiKey': credentials['binance']['apiKey'],
    'secret': credentials['binance']['secret'],
    })

exchanges = {'Coinbase Pro': coinbase_pro, 'Binance':binance}

for exchange in exchanges:
    exchanges[exchange].enableRateLimit = True
    print("Rate limiter enabled for " + exchange)


class Asset:
    ticker = ''
    quantity = Decimal(0)
    value = Decimal(0)
    timestamp = datetime.time

    def __init__(self, ticker='', quantity=Decimal(0), value=Decimal(0), date=datetime.datetime.now()):
        self.ticker = ticker
        self.quantity = quantity
        self.value = value
        self.timestamp = date
        # print(self.timestamp)

    def print_all(self):
        if self.value != None:
            print(self.ticker + "\t Quantity: " + str(self.quantity) + "\t Value: $" + str(self.value))
        else:
            print(self.ticker + "\t Quantity: " + str(self.quantity) + "\t Value: " + str(self.value))

    def print(self):
        if self.value != None:
            print(self.ticker + "\t Quantity: " + str(self.quantity) + "\t Value: $" + str(self.value))

    def to_json(self):
        return "{\"ticker\":\"" + self.ticker + "\",\"quantity\":\"" + str(self.quantity) + "\",\"value\":\"" + str(
            self.value) + "\",\"timestamp\":\"" + str(self.timestamp) + "\"}"


# Returns the dollar equivalent of a given symbol
def convert_to_usd(asset):
    # asset.print()
    request_url = "https://api.coinmarketcap.com/v2/ticker/623/?convert="+asset.ticker
    try:
        exchange_rate_request = requests.get(request_url).json()
        exchange_rate = Decimal(exchange_rate_request['data']['quotes'][asset.ticker]['price'])
        usd = Decimal(asset.quantity) / exchange_rate
        asset.value = usd
    except KeyError:
        # print("Symbol " + ticker + " is either incorrect or could not be found\n"+exchange_rate_request+"\n")
        asset.value = 0
    return asset


# Converts entire wallet into dollar equivalent
def get_wallet():
    balances = exchanges['Binance'].fetch_balance()['info']['balances']
    assets = []
    for ticker in balances:
        # Sumes the balances of that are liduid and held up in an order
        if float(ticker['free']) > 0 or float(ticker['locked']) > 0:
            new_asset = Asset(ticker['asset'], Decimal(ticker['free']) + Decimal(ticker['locked']))
            assets.append(new_asset)

    # pprint(assets)
    failed_lookup = []
    for index in range(len(assets)):
        # Check if return type is the number or fail ticker symbol
        if assets[index].value != 0:
            assets[index] = convert_to_usd(assets[index])
        else:
            failed_lookup.append(convert_to_usd(assets[index]))
    print(str(len(failed_lookup)) + " currencies could not be found" + str(failed_lookup))
    return assets


def write_assets_to_file(list_of_assets, time_delay=0):
    now = datetime.datetime.now()
    save_location = 'data/balance_data_' + str(now.strftime("%Y-%m-%d")) + '.json'
    print(now)

    balances_data = open(save_location, "w+")
    balances_data.write("{")
    for i in range(1):
        for asset in list_of_assets:
            if asset.value > 0:
                balances_data.write("\"" + str(asset.ticker) + "\":{\"" + str(asset.timestamp) + "\":\"{"+ asset.to_json() + "\"},\n")
                # balances_data.write("\"" + str(asset.timestamp) + "\":" + asset.to_json() + ",\n")
                time.sleep(time_delay)
    balances_data.write("}")


for item in get_wallet():
    item.print()

write_assets_to_file(get_wallet())
