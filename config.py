import os

PRODUCTION = "production"
DEVELOPMENT = "development"

COIN_TARGET = "BTC"
COIN_REFER = "USDT"

ENV = os.getenv("ENVIRONMENT", PRODUCTION)
DEBUG = True

BINANCE = {
  "key": "uH8PsZSdTDENZteqpAhtaWbQivk6LHTcxt5BlifHKcUOoI7ngPYdFZS1FCyDIj30",
  "secret": "tswqduwMhzMMDpjYRgZM8wKQEfjctBIk1C9RUnL2hbOMnPxvwMwuHzJSss4tpN1M"
}

TELEGRAM = {
  "channel": "5097110543",
  "bot": "5341109352:AAGr5IoXS35hQwU1zCM0gHe7GVK_64BJZwk"
}

print("ENV = ", ENV)