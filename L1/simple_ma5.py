import ccxt
import time
from datetime import datetime

'''
# Find VPN port
lsof -i -P | grep -i "LISTEN"

# Verify
curl -x http://127.0.0.1:15236 http://www.google.com
'''

proxy_url = 'http://127.0.0.1:15236'

exchange = ccxt.okx({
'proxies': {
'http': proxy_url,
'https': proxy_url,
},
'timeout': 30000,
'enableRateLimit': True,
})

symbol = 'BTC/USDT'
price_history = []  # most recent price history
window_size = 5     # ma window size

while True:
    try:
        # get price
        ticker = exchange.fetch_ticker(symbol)
        current_price = ticker['last']
        now = datetime.now().strftime('%H:%M:%S')
        # update price history
        price_history.append(current_price)
        if len(price_history) > window_size:
            price_history.pop(0)
        if len(price_history) == window_size:
            # calculate MA
            ma_price = sum(price_history) / window_size
            diff_percent = (current_price - ma_price) / ma_price * 100
            # compare price with MA
            if diff_percent > 0.05: # price is 0.05% above MA
                print(f"Above signal")
            elif diff_percent < -0.05: # price is 0.05% below
                print(f"Below signal")
            else:
                print(f"No signal")
            print(f"CP = {current_price}, MAP = {ma_price}, Diff = {diff_percent:.2f}%")
        else:
            print(f"[{now}] Getting initial... ({len(price_history)}/{window_size})")
        time.sleep(5)  # wait before next price fetch
    except Exception as e:
        print(f"Error fetching price: {e}")
        time.sleep(10)  # wait before retrying
