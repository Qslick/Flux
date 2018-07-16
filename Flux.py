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
import os
from pathlib import Path
import csv



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


# Gets currencies from wallet and returns a list of assets
def get_wallet():
    balances = exchanges['Binance'].fetch_balance()['info']['balances']
    assets = []
    for ticker in balances:
        # Sumes the balances of that are liduid and held up in an order
        if float(ticker['free']) > 0 or float(ticker['locked']) > 0:
            new_asset = Asset(ticker['asset'], Decimal(ticker['free']) + Decimal(ticker['locked']))
            new_asset = convert_to_usd(new_asset)
            assets.append(new_asset)
    return assets


for item in get_wallet():
    item.print()


def initialized_files(asset_list):
    # Check is 'data/' directory exist
    if not os.path.exists('data/'):
        os.mkdir('data/')
        print("Created Directory \'data/\'")

    # Checks if files exist, and if not initializes them
    for item in asset_list:
        path = Path('data/' + item.ticker + '_data.csv')
        # print(path)
        if not path.is_file():
            print(path.is_file())
            with open('data/' + item.ticker + '_data.csv', 'w') as csvfile:
                writer = csv.writer(csvfile, delimiter=',')
                writer.writerow(['timestamp', 'quantity', 'value'])
            print("Created File \'" + str(path) + '\'')

    # print("File initialization complete")


def write_data_to_file(asset_list):
    initialized_files(asset_list)
    for item in asset_list:
        with open('data/' + item.ticker + '_data.csv', 'a') as csvfile:
            writer = csv.writer(csvfile, delimiter=',')
            writer.writerow([time.time(), str(item.quantity), str(item.value)])
            # print(item.value)


# Returns a Dictionary list of all the data saved for a specific symbol
def parse_data(asset_ticker):
    asset_data = []
    with open('data/' + asset_ticker + '_data.csv') as csvfile:
        reader = csv.DictReader(csvfile)
        for line in reader:
            asset_data.append(line)
    return asset_data


def plot_data(asset_dict, x_metric, y_metric):
    x_metric_lst = []
    y_metric_lst = []
    for item in asset_dict:
        time = datetime.datetime.fromtimestamp(float(item[x_metric])).strftime('%H:%M')
        x_metric_lst.append(time)
        # x_metric_lst.append(item[x_metric])
        y_metric_lst.append(item[y_metric])

    plt.plot(x_metric)
    plt.plot(x_metric_lst, y_metric_lst)
    # plt.axis([min(x_metric_lst), max(x_metric_lst), min(y_metric_lst), max(y_metric_lst)])

    # date = datetime.datetime.fromtimestamp(float(x_metric_lst[0])).strftime('%Y-%m-%d %H:%M')
    # print(date)
    plt.xlabel(x_metric)
    plt.ylabel(y_metric)
    plt.show()
    return plt
    # plt.show()

while True:
    write_data_to_file(get_wallet())
    print(str(item+1) + ' records saved')
    time.sleep(60)