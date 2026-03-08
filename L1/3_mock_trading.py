import ccxt
import time
from datetime import datetime

proxy_url = 'http://127.0.0.1:15236'

exchange = ccxt.okx({
'proxies': {
'http': proxy_url,
'https': proxy_url,
},
'timeout': 30000,
'enableRateLimit': True,
})


# mock account initial state
symbol = 'BTC/USDT'
cash = 10000  # initial cash in USDT
btc_hold = 0       # initial BTC holdings
price_history = []  # most recent price history
window_size = 10     # ma window size

print(f"Initial state: Cash = {cash} USDT, BTC = {btc_hold} BTC")

while True:
    try:
        ticker = exchange.fetch_ticker(symbol)
        current_price = ticker['last']
        now = datetime.now().strftime('%H:%M:%S')
        price_history.append(current_price)
        if len(price_history) > window_size:
            price_history.pop(0)
            ma_price = sum(price_history) / window_size
            # buy: price is 0.1% above MA and no BTC holdings
            if current_price > ma_price * 1.001 and btc_hold == 0:
                btc_hold = cash / current_price
                entry_price = current_price
                cash = 0
                print(f"[{now}] Buy at {current_price:.2f} USDT, Cash = {cash:.2f} USDT, BTC = {btc_hold:.6f} BTC")
            # sell: price is 0.1% below MA and have BTC holdings
            elif current_price < ma_price * 0.999 and btc_hold > 0:
                cash = btc_hold * current_price
                profit = cash - 10000
                profit_percent = profit / (btc_hold * entry_price) * 100
                btc_hold = 0
                print(f"[{now}] Sell at {current_price:.2f} USDT, Cash = {cash:.2f} USDT, Profit = {profit:.2f} USDT ({profit_percent:.2f}%)")
            else:
                current_value = cash if btc_hold == 0 else btc_hold * current_price
                print(f"[{now}] Hold, Price = {current_price:.2f} USDT, Value = {current_value:.2f} USDT")
        time.sleep(5)  # wait before next price fetch
    except Exception as e:
        print(f"Error fetching price: {e}")
        time.sleep(10)  # wait before retrying
