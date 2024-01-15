import requests
import time

def get_crypto_price(crypto):
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={crypto}&vs_currencies=usd"
    response = requests.get(url)
    data = response.json()
    return data[crypto]['usd']

def check_price(crypto, threshold):
    price = get_crypto_price(crypto)
    if price < threshold:
        print(f"ALERT: {crypto} is below ${threshold}! Current price: ${price}")
    else:
        print(f"{crypto} is above ${threshold}. Current price: ${price}")

def main():
    crypto = "bitcoin"
    threshold = 20000  # Set your threshold price here

    while True:
        check_price(crypto, threshold)
        time.sleep(60)  # Checks the price every 60 seconds

if __name__ == "__main__":
    main()
