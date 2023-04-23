# Twitter bot that updates dogecoin prices.
# https://twitter.com/_DogeBot

# Author: Paulo Farias

from datetime import datetime, timedelta, timezone
from decimal import Decimal
import sys
import tweepy
import time
import random
import requests
import ujson
import concurrent.futures


def query_price():
    url_api = 'https://api.wazirx.com/api/v2/tickers/dogeusdt'
    try:
        response = requests.get(url_api, timeout=5)
        response.raise_for_status()
        data = response.json()['ticker']
        return float(data['last']), float(data['high']), float(data['low'])
    except requests.exceptions.RequestException as e:
        print(e)
        sys.exit()


def current_time():
    return datetime.now().strftime("%d/%m/%Y - %H:%M:%S")


def random_delay():
    delay = random.randint(30, 60) * 60
    for i in range(delay, 0, -1):
        print(f'{i} seconds left to next tweet', end='\r')
        time.sleep(1)
    print('Time to tweet!')


def first_price_tread():
    while True:
        # Get UTC time
        utc = datetime.now(timezone.utc)
        target_time = utc.replace(hour=0, minute=1, second=0, microsecond=0)
        delay = (target_time - utc).total_seconds()

        if delay <= 0:
            first_price, highest_price, lowest_price = query_price()
            print(f'{current_time()} - First price is {first_price}\n')

            # Reset target time to next day
            target_time = target_time + timedelta(days=1)

        time.sleep(delay)


def format_tweet_text(price, percentual_variation, difference, highest_price, lowest_price):
    decimal_price = Decimal(str(price))
    decimal_percentual_variation = Decimal(str(percentual_variation))
    decimal_difference = Decimal(str(difference))
    decimal_highest_price = Decimal(str(highest_price))
    decimal_lowest_price = Decimal(str(lowest_price))

    text = (f'\U0001F436 Current price: {decimal_price:.4f} USD '
            f'({decimal_percentual_variation:+.2f}% | {decimal_difference:+.4f} today)\n\n '
            f'\U00002B06Highest price: {decimal_highest_price:.4f} USD\n '
            f'\U00002B07Lowest price: {decimal_lowest_price:.4f} USD\n\n #Dogecoin #Doge $Doge')
    return text


with open("/home/paulofarias/Documents/DogeBot/keys.json") as f:
    keys = ujson.load(f)


# Get the initial prices
price, highest_price, lowest_price = query_price()
first_price = float(input('Enter the first price: '))

# Start first price thread
with concurrent.futures.ThreadPoolExecutor() as executor:
    executor.submit(first_price_tread)


while True:

    price, highest_price, lowest_price = query_price()

    # Difference between the current price and the first price
    difference = price - first_price

    # Percentual variation
    percentual_variation = (price / first_price - 1) * 100

    # Authenticate with Twitter API V2
    twitter = tweepy.Client(consumer_key=keys['API Key'], consumer_secret=keys['API Key Secret'],
                            access_token=keys['Access Token'], access_token_secret=keys['Access Token Secret'])

    '''
    # Create a tweet
    try:
        tweet_text = format_tweet_text(
            price, percentual_variation, difference, highest_price, lowest_price)
        response = twitter.create_tweet(text=tweet_text)
        print(f'{current_time()} - Tweet sent')
    except tweepy.Forbidden as e:
        print(e)
    '''

    print(current_time(
    ), f'- Current price: {round(price, 4)} USD ({"{0:+.02f}".format(percentual_variation)}% | {"{0:+.04f}".format(difference)} today)\n')

    random_delay()
