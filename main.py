# Twitter bot that updates dogecoin prices.
# https://twitter.com/_DogeBot

# Author: Paulo Farias

from datetime import datetime, timezone
import sys
import threading
import tweepy
import time
import random
import requests
import json


def query_price():
    url_api = 'https://api.wazirx.com/api/v2/tickers/dogeusdt'
    # Get the current price of dogecoin
    try:
        response = requests.get(url_api, timeout=5)
    except requests.exceptions.RequestException as e:
        print(e)
        sys.exit()

    price = float(json.loads(response.text)['ticker']['last'])
    highest_price = float(json.loads(response.text)['ticker']['high'])
    lowest_price = float(json.loads(response.text)['ticker']['low'])

    return price, highest_price, lowest_price


def current_time():
    ct = datetime.now()
    ct = ct.strftime("%d/%m/%Y - %H:%M:%S")
    return ct


def random_delay():
    delay = random.randint(30, 60)
    delay = delay * 60

    for i in range(delay, 0, -1):
        sys.stdout.flush()
        sys.stdout.write(f'\r{i} seconds left to next tweet')
        time.sleep(1)


def first_price_tread():
    while True:
        # Get UTC time
        utc = datetime.now(timezone.utc)
        if utc.strftime('%H:%M') == '00:01':
            first_price, highest_price, lowest_price = query_price()
            print(f'{current_time()} - First price is {first_price}\n')
        time.sleep(60)


# Get keys from json file
with open('keys.json') as f:
    keys = json.load(f)


# Set varriables
price, highest_price, lowest_price = query_price()
first_price = float(input('Enter the first price: '))

# Start first price thread
threading.Thread(target=first_price_tread).start()


while True:

    price, highest_price, lowest_price = query_price()

    # Difference between the current price and the first price
    difference = price - first_price

    # Percentual variation
    percentual_variation = (price / first_price - 1) * 100

    # Authenticate with Twitter API V2
    twitter = tweepy.Client(consumer_key=keys['API Key'], consumer_secret=keys['API Key Secret'],
                            access_token=keys['Access Token'], access_token_secret=keys['Access Token Secret'])

    # Create a tweet
    try:
        response = twitter.create_tweet(
            text=f'\U0001F436 Current price: {round(price, 4)} USD ({"{0:+.02f}".format(percentual_variation)}% | {"{0:+.04f}".format(difference)} today)\n\n \U00002B06Highest price: {round(highest_price,4)} USD\n \U00002B07Lowest price: {round(lowest_price,4)} USD\n\n #Dogecoin #Doge $Doge')
        print(f'{current_time()} - Tweet sent')
    except tweepy.errors.Forbidden as e:
        print(e)

    print(current_time(
    ), f'- Current price: {round(price, 4)} USD ({"{0:+.02f}".format(percentual_variation)}% | {"{0:+.04f}".format(difference)} today)\n')

    random_delay()
