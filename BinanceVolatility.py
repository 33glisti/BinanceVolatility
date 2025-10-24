#!/usr/bin/env python3
import sys
from binance.client import Client
import pandas as pd
import datetime

# --- Настройки ---
API_KEY = ''      # Публичные данные, можно оставить пустым
API_SECRET = ''
TIMEFRAME = '15m'  # Таймфрейм свечей
VOL_TYPE = 'rel'   # 'rel' = (high-low)/open, 'abs' = high-low

# --- Получение параметров из командной строки ---
if len(sys.argv) != 3:
    print(f"Использование: {sys.argv[0]} <PAIR> <DAYS>")
    print("Пример: python3 volat.py BTCUSDT 365")
    sys.exit(1)

PAIR = sys.argv[1].upper()
DAYS = int(sys.argv[2])

# --- Инициализация клиента ---
client = Client(API_KEY, API_SECRET)

# --- Получение исторических данных ---
end_time = datetime.datetime.now()
start_time = end_time - datetime.timedelta(days=DAYS)

klines = client.get_historical_klines(
    PAIR, TIMEFRAME,
    start_time.strftime("%d %b %Y %H:%M:%S"),
    end_time.strftime("%d %b %Y %H:%M:%S")
)

# --- Преобразуем в DataFrame ---
df = pd.DataFrame(klines, columns=[
    "open_time", "open", "high", "low", "close", "volume",
    "close_time", "quote_asset_volume", "number_of_trades",
    "taker_buy_base_asset_volume", "taker_buy_quote_asset_volume", "ignore"
])
for col in ['open', 'high', 'low', 'close']:
    df[col] = pd.to_numeric(df[col])

# --- Добавляем дату ---
df['date'] = pd.to_datetime(df['open_time'], unit='ms').dt.date

# --- Волатильность каждой свечи ---
if VOL_TYPE == 'rel':
    df['volatility'] = (df['high'] - df['low']) / df['open']
else:
    df['volatility'] = df['high'] - df['low']

# --- Медиана по дням ---
daily_medians = df.groupby('date')['volatility'].median()

# --- Итоговая медиана за период ---
period_median = daily_medians.median()

# --- Вывод ---
print(f"Общая медиана волатильности пары {PAIR} за {DAYS} дней: {period_median*100:.3f}%")
