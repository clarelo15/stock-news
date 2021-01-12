import requests
from twilio.rest import Client
import os
from dotenv import load_dotenv

load_dotenv()

STOCK_ENDPOINT = os.getenv('STOCK_ENDPOINT')
NEWS_ENDPOINT = os.getenv('NEWS_ENDPOINT')

STOCK_API_KEY = os.getenv('STOCK_API_KEY')
NEWS_API_KEY = os.getenv('NEWS_API_KEY')

TWILIO_SID = os.getenv('TWILIO_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')

FROM_WHERE = os.getenv('FROM_WHERE')
TO_WHERE = os.getenv('TO_WHERE')

my_stocks = {
    'TSLA': 'Tesla Inc',
    'AAPL': 'Apple Inc',
    'AMZN': 'Amazon.com Inc',
    'GOOGL': 'Alphabet Inc',
    'FB': 'Facebook Inc'
}

print(my_stocks.keys())
# Get yesterday's closing stock price from https://www.alphavantage.co/documentation/#daily
for (key, value) in my_stocks.items():
    stock_params = {
        "function": "TIME_SERIES_DAILY",
        "symbol": key,
        "apikey": STOCK_API_KEY,
    }

    res = requests.get(STOCK_ENDPOINT, params=stock_params)
    print(res.json())
    data = res.json()["Time Series (Daily)"]
    data_list = [value for (key, value) in data.items()]
    yesterday_data = data_list[0]
    yesterday_closing_price = yesterday_data["4. close"]
    print(yesterday_closing_price)

    # Get the day before yesterday's closing stock price
    previous_day_data = data_list[1]
    previous_day_closing_price = previous_day_data["4. close"]
    print(previous_day_closing_price)

    # Find the positive difference between yesterday closing price and closing price the day before yesterday
    diff = float(yesterday_closing_price) - float(previous_day_closing_price)
    sign = None
    if diff > 0:
        sign = "⬆️"
    else:
        sign = "⬇️"

    # Work out the percentage difference in price between closing price yesterday and closing price the day before yesterday
    percentage_diff = round((diff / float(yesterday_closing_price) * 100), 2)
    print(percentage_diff)

    # If percentage is greater than 5 then use the News API to get articles related to the stock
    percentage_diff = abs(percentage_diff)
    if percentage_diff > 5:
        news_params = {
            "qInTitle": value,
            "apiKey": NEWS_API_KEY,
        }

        news_res = requests.get(NEWS_ENDPOINT, params=news_params)
        print(news_res.json())
        news_data = news_res.json()["articles"]
        # Use Python slice operator to create a list that contains the first articles
        articles = news_data[:1]
        print(articles)

        # Use twilio to send a separate message with each article's title and description to the phone number
        # Create a new list of the article's headline and description using list comprehension
        msg = [f"{key} : {sign}{percentage_diff}%\nHeadline: {article ['title']}. \nBreif: {article ['description']}" for article in articles]
        client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)
        # Send each article as a separate message via Twilio
        for article in msg:
            message = client.messages.create(
                body=article,
                from_=FROM_WHERE,
                to=TO_WHERE,
            )


