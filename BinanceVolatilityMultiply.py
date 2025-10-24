#!/usr/bin/env python3
import sys
from binance.client import Client
import pandas as pd
import datetime

# --- Настройки ---
API_KEY = ''
API_SECRET = ''
TIMEFRAME = '15m'  # Таймфрейм свечей
VOL_TYPE = 'rel'   # 'rel' = (high-low)/open, 'abs' = high-low

# --- Проверка аргументов ---
if '-p' not in sys.argv or '-d' not in sys.argv:
    print(f"Использование: {sys.argv[0]} -p <PAIR1,PAIR2,...> -d <DAYS1,DAYS2,...>")
    print("Пример: python3 BinanceVolatility.py -p adaeur,soleur,xrpeur -d 30,90,180")
    sys.exit(1)

pairs_arg = sys.argv[sys.argv.index('-p') + 1]
days_arg = sys.argv[sys.argv.index('-d') + 1]

PAIRS = [p.strip().upper() for p in pairs_arg.split(',')]
DAYS_LIST = [int(d.strip()) for d in days_arg.split(',')]

# --- Инициализация клиента ---
client = Client(API_KEY, API_SECRET)

def calc_median_volatility(pair: str, days: int) -> float:
    """Возвращает медиану волатильности (%) для указанной пары и периода."""
    end_time = datetime.datetime.now()
    start_time = end_time - datetime.timedelta(days=days)

    klines = client.get_historical_klines(
        pair, TIMEFRAME,
        start_time.strftime("%d %b %Y %H:%M:%S"),
        end_time.strftime("%d %b %Y %H:%M:%S")
    )

    df = pd.DataFrame(klines, columns=[
        "open_time", "open", "high", "low", "close", "volume",
        "close_time", "quote_asset_volume", "number_of_trades",
        "taker_buy_base_asset_volume", "taker_buy_quote_asset_volume", "ignore"
    ])
    if df.empty:
        return None

    for col in ['open', 'high', 'low', 'close']:
        df[col] = pd.to_numeric(df[col])
    df['date'] = pd.to_datetime(df['open_time'], unit='ms').dt.date

    if VOL_TYPE == 'rel':
        df['volatility'] = (df['high'] - df['low']) / df['open']
    else:
        df['volatility'] = df['high'] - df['low']

    daily_medians = df.groupby('date')['volatility'].median()
    return daily_medians.median() * 100  # В процентах

# --- Основной цикл ---
results = {}

for pair in PAIRS:
    row = []
    for days in DAYS_LIST:
        vol = calc_median_volatility(pair, days)
        row.append(f"{vol:.3f}%" if vol is not None else "нет данных")
    results[pair] = row

# --- Формирование таблицы ---
header = "Пара  | " + " | ".join([f"{d} дн" for d in DAYS_LIST])
print(header)
print("-" * len(header))
for pair, values in results.items():
    print(f"{pair:<6}| " + " | ".join(values))
