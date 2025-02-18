from flask import Flask, jsonify, request
import requests
import pandas as pd
from twilio.rest import Client
import os

app = Flask(__name__)

# Alpha Vantage API key
API_KEY = "RQ4FJSUDARVJODQK"

# Twilio credentials (from Render environment variables)
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
YOUR_PHONE_NUMBER = os.getenv("YOUR_PHONE_NUMBER")

# Top 10 trading pairs (example list, replace with actual pairs)
TRADING_PAIRS = [
    ("USD", "KES"),
    ("EUR", "USD"),
    ("GBP", "JPY"),
    # Add more pairs here...
]

# Fetch forex data from Alpha Vantage
def fetch_forex_data(from_currency, to_currency):
    url = f"https://www.alphavantage.co/query?function=FX_DAILY&from_symbol={from_currency}&to_symbol={to_currency}&apikey={API_KEY}"
    response = requests.get(url)
    return response.json()

# Generate moving average crossover signal
def generate_signal(data, pair):
    try:
        df = pd.DataFrame.from_dict(data["Time Series FX (Daily)"], orient="index").astype(float)
        df.index = pd.to_datetime(df.index)
        df.sort_index(inplace=True)

        # Calculate moving averages
        df['SMA_50'] = df['4. close'].rolling(window=50).mean()
        df['SMA_200'] = df['4. close'].rolling(window=200).mean()

        # Generate signal
        df['Signal'] = 0
        df['Signal'][50:] = ((df['SMA_50'][50:] > df['SMA_200'][50:]) & (df['SMA_50'].shift(1)[50:] <= df['SMA_200'].shift(1)[50:]))
        df['Position'] = df['Signal'].diff()

        latest_date = df.index[-1]
        latest_price = df['4. close'][-1]

        if df['Position'][-1] == 1:
            return {"pair": f"{pair[0]}/{pair[1]}", "signal": "buy", "price": latest_price, "date": latest_date}
        elif df['Position'][-1] == -1:
            return {"pair": f"{pair[0]}/{pair[1]}", "signal": "sell", "price": latest_price, "date": latest_date}
        else:
            return None
    except Exception as e:
        print(f"Error generating signal for {pair}: {e}")
        return None

# Send SMS notification using Twilio
def send_sms(signal):
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        message = client.messages.create(
            body=f"Trading Signal: {signal['pair']} - {signal['signal'].upper()} at {signal['price']} ({signal['date']})",
            from_=TWILIO_PHONE_NUMBER,
            to=YOUR_PHONE_NUMBER
        )
        print(f"SMS sent successfully! Message SID: {message.sid}")
    except Exception as e:
        print(f"Error sending SMS: {e}")

# Routes
@app.route('/signals', methods=['GET'])
def get_signals():
    signals = []
    for pair in TRADING_PAIRS:
        try:
            data = fetch_forex_data(pair[0], pair[1])
            signal = generate_signal(data, pair)

            if signal:
                signals.append(signal)
                # Send SMS notification
                send_sms(signal)
        except Exception as e:
            print(f"Error processing pair {pair}: {e}")

    if signals:
        return jsonify(signals), 200
    else:
        return jsonify({"message": "No signals generated"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
