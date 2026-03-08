import ccxt

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

ticker = exchange.fetch_ticker('BTC/USDT')

last_price = ticker['last']

print(f"Current BTC price: {last_price} USDT")
