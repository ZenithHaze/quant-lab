import ccxt
import pandas as pd
import pandas_ta as ta
from datetime import datetime

proxy_url = 'http://127.0.0.1:15236'
exchange = ccxt.okx({'proxies': {'http': proxy_url, 'https': proxy_url}, 'enableRateLimit': True, 'timeout': 30000})

print("Downloading historical data...")

bars = exchange.fetch_ohlcv('SOL/USDT', timeframe='15m', limit=50000, params={'paginate': True})
df = pd.DataFrame(bars, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
df['time'] = pd.to_datetime(df['timestamp'], unit='ms')

df['MA20'] = ta.sma(df['close'], length=20) # close price MA in 20 periods
df['RSI'] = ta.rsi(df['close'], length=14)  # close price RSI in 14 periods
df['VOL_MA5'] = ta.sma(df['volume'], length=5) # volume MA in 5 periods

print("Backtesting strategy...")

cash = 10000.0
hold = 0.0
history = []

# Exit strategy
STOP_LOSS_RATE = 0.02
TAKE_PROFIT_RATE = 0.05

# Correlation
def get_market_sentiment(exchange):
    btc_bars = exchange.fetch_ohlcv('BTC/USDT', timeframe='15m', limit=20)
    btc_df = pd.DataFrame(btc_bars, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    # Consider health if BTC is greater than its 20-period MA
    return btc_df['close'].mean() < btc_df['close'].iloc[-1]

entry_price = 0.0

for i in range(20, len(df)):
    row = df.iloc[i]
    current_price = row['close']
    prev_row = df.iloc[i-3:i] # look back 3 bars for signal confirmation
    
    current_price = row['close']
    current_rsi = row['RSI']
    current_vol = row['volume']
    avg_vol = row['VOL_MA5']
    
    # Exit strategy: stop loss or take profit
    if entry_price > 0 and hold > 0:
        price_change = (current_price - entry_price) / entry_price
        if price_change <= -STOP_LOSS_RATE or price_change >= TAKE_PROFIT_RATE:
            # This line of code is a conditional statement that checks multiple conditions before deciding to
            # execute a buy order in a trading strategy. Here's a breakdown of each condition:
            cash = (hold * current_price) * (1 - 0.0005) # 0.05% trading fee
            hold = 0.0
            profit = cash - 10000
            profit_percent = profit / 10000 * 100
            str = "STOP LOSS" if price_change <= -STOP_LOSS_RATE else "TAKE PROFIT"
            history.append(f"[{row['time']}] {str} @ {current_price:.2f} (RSI: {current_rsi:.1f}) profit: {profit:.2f} USDT ({profit_percent:.2f}%)")
            continue
    
    # Strategy buy and sell signals
    is_above_ma = all(prev_row['close'] > prev_row['MA20']) and (current_price > row['MA20'])
    is_not_overbought = current_rsi < 70
    is_volume_breakout = current_vol > (avg_vol * 1.5)
    if is_above_ma and is_not_overbought and is_volume_breakout and cash > 0 and get_market_sentiment(exchange):
        entry_price = current_price
        hold = cash / current_price
        cash = 0.0
        history.append(f"[{row['time']}] BUY @ {current_price:.2f} (RSI: {current_rsi:.1f})")
    elif current_price < row['MA20'] and hold > 0:
        cash = (hold * current_price) * (1 - 0.0005)
        hold = 0.0
        profit = cash - 10000
        profit_percent = profit / 10000 * 100
        history.append(f"[{row['time']}] SELL @ {current_price:.2f} (RSI: {current_rsi:.1f}) profit: {profit:.2f} USDT ({profit_percent:.2f}%)")
        
final_value = cash if hold == 0 else hold * df.iloc[-1]['close']
profit_percent = (final_value - 10000) / 10000 * 100
print("\nBacktest Results:")
for log in history:# [-10:]:
    print(log)
print(f"Final Value: {final_value:.2f} USDT, Profit: {profit_percent:.2f}%")

