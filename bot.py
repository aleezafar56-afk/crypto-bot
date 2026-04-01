import requests
import pandas as pd
import numpy as np
import time

TOKEN = "8656839617:AAFIH_bR45piwZWnDmQkrMlFjyWcinrQN7I"
CHAT_ID = "5415032810"

SYMBOLS = ["SUIUSDT","LINKUSDT","ADAUSDT","SOLUSDT","ETHUSDT","XRPUSDT","DOGEUSDT"]

def send_message(msg):
url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

def get_data(symbol):
url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=15m&limit=100"
data = requests.get(url).json()

df = pd.DataFrame(data)
df = df.iloc[:, :5]
df.columns = ["time","open","high","low","close"]

df["high"] = df["high"].astype(float)
df["low"] = df["low"].astype(float)
df["close"] = df["close"].astype(float)

return df

def vidya(df):
close = df["close"]
diff = close.diff()

up = diff.clip(lower=0)
down = -diff.clip(upper=0)

cmo = (up.rolling(20).sum() - down.rolling(20).sum()) / (up.rolling(20).sum() + down.rolling(20).sum())
cmo = cmo.fillna(0)

alpha = 2/(34+1)
v = [close.iloc[0]]

for i in range(1,len(close)):
val = alpha*abs(cmo.iloc[i])*close.iloc[i] + (1-alpha*abs(cmo.iloc[i]))*v[i-1]
v.append(val)

df["vidya"] = v
return df

last = {}

while True:
for s in SYMBOLS:
try:
df = vidya(get_data(s))

prev = df.iloc[-2]
curr = df.iloc[-1]

signal = None

# BUY
if prev["high"] < prev["vidya"] and curr["high"] >= curr["vidya"]:
signal = "BUY"

# SELL
elif prev["low"] > prev["vidya"] and curr["low"] <= curr["vidya"]:
signal = "SELL"

if signal and last.get(s) != signal:
last[s] = signal

price = curr["close"]

message = f"""🚨 VIDYA SIGNAL 🚨
Pair: {s}
Type: {signal}
Timeframe: 15m
Price: {price}
"""

send_message(message)

time.sleep(2)

except Exception as e:
print("Error:", e)

time.sleep(20)
