from __future__ import annotations
import httpx

BASE_URL = "https://www.tradingview.com"
SCANNER_URL = "https://scanner.tradingview.com/{market}/scan"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
    "Origin": BASE_URL,
    "Referer": BASE_URL,
    "Content-Type": "application/json",
}

# Columns supported by all markets (stocks, crypto, forex, commodities, indices)
COLUMNS_COMMON = [
    "name", "description", "type", "subtype",
    "close", "open", "high", "low",
    "change", "change_abs", "change_from_open",
    "volume", "volume_change", "relative_volume_10d_calc",
    "Recommend.All",
    "RSI", "RSI[1]",
    "MACD.macd", "MACD.signal",
    "EMA20", "EMA50", "EMA200",
    "SMA20", "SMA50", "SMA200",
    "BB.upper", "BB.lower",
    "VWAP",
    "ATR",
    "High.All", "Low.All",
    "price_52_week_high", "price_52_week_low",
    "average_volume_10d_calc", "average_volume_30d_calc",
    "exchange",
]

# Extra columns only available on the stocks/america scanner
COLUMNS_STOCKS_EXTRA = [
    "market_cap_basic", "price_earnings_ttm",
    "earnings_per_share_basic_ttm", "dividends_yield_current",
    "sector", "industry",
    "beta_1_year",
    "gap", "premarket_change", "postmarket_change",
]

COLUMNS = COLUMNS_COMMON + COLUMNS_STOCKS_EXTRA

COLUMN_NAMES_COMMON = [
    "symbol", "description", "type", "subtype",
    "price", "open", "high", "low",
    "change_%", "change_abs", "change_from_open_%",
    "volume", "volume_change_%", "relative_volume",
    "technical_rating",
    "rsi", "rsi_prev",
    "macd", "macd_signal",
    "ema20", "ema50", "ema200",
    "sma20", "sma50", "sma200",
    "bb_upper", "bb_lower",
    "vwap",
    "atr",
    "52w_high", "52w_low",
    "price_52w_high", "price_52w_low",
    "avg_vol_10d", "avg_vol_30d",
    "exchange",
]

COLUMN_NAMES_STOCKS_EXTRA = [
    "market_cap", "pe_ratio",
    "eps", "dividend_yield_%",
    "sector", "industry",
    "beta",
    "gap_%", "pre_market_change_%", "after_hours_change_%",
]

COLUMN_NAMES = COLUMN_NAMES_COMMON + COLUMN_NAMES_STOCKS_EXTRA

STOCK_SYMBOLS = [
    # Mega-cap Tech
    "NASDAQ:AAPL", "NASDAQ:MSFT", "NASDAQ:NVDA", "NASDAQ:GOOGL",
    "NASDAQ:AMZN", "NASDAQ:META", "NASDAQ:TSLA", "NASDAQ:AVGO",
    # Finance
    "NYSE:JPM", "NYSE:BAC", "NYSE:GS", "NYSE:MS",
    # Healthcare
    "NYSE:JNJ", "NYSE:UNH", "NASDAQ:MRNA",
    # Energy
    "NYSE:XOM", "NYSE:CVX",
    # Consumer
    "NYSE:WMT", "NYSE:KO", "NYSE:PG",
    # ETFs
    "AMEX:SPY", "AMEX:QQQ", "AMEX:IWM",
]

CRYPTO_SYMBOLS = [
    "BINANCE:BTCUSDT", "BINANCE:ETHUSDT", "BINANCE:BNBUSDT",
    "BINANCE:SOLUSDT", "BINANCE:XRPUSDT", "BINANCE:DOGEUSDT",
    "BINANCE:ADAUSDT", "BINANCE:MATICUSDT", "BINANCE:DOTUSDT",
    "BINANCE:LINKUSDT", "BINANCE:AVAXUSDT", "BINANCE:UNIUSDT",
    "BINANCE:LTCUSDT", "BINANCE:ATOMUSDT", "BINANCE:NEARUSDT",
]

FOREX_SYMBOLS = [
    "FX:EURUSD", "FX:GBPUSD", "FX:USDJPY", "FX:USDCHF",
    "FX:AUDUSD", "FX:USDCAD", "FX:NZDUSD", "FX:EURGBP",
]

COMMODITY_SYMBOLS = [
    "TVC:GOLD", "TVC:SILVER", "TVC:USOIL", "TVC:UKOIL",
    "TVC:NATURALGAS", "TVC:COPPER",
]

INDEX_SYMBOLS = [
    "TVC:SPX", "TVC:NDX", "TVC:DJI", "TVC:RUT",
    "TVC:VIX", "TVC:DXY", "TVC:NI225", "TVC:FTSE", "TVC:DAX",
]


def _build_payload(symbols: list[str], columns: list[str]) -> dict:
    return {
        "symbols": {"tickers": symbols, "query": {"types": []}},
        "columns": columns,
    }


def _parse(data: dict, column_names: list[str]) -> list[dict]:
    results = []
    for row in data.get("data", []):
        vals = row.get("d", [])
        entry = {}
        for i, key in enumerate(column_names):
            val = vals[i] if i < len(vals) else None
            if isinstance(val, float):
                val = round(val, 4)
            entry[key] = val
        # derive technical signal label
        rating = entry.get("technical_rating")
        if rating is not None:
            if rating >= 0.5:
                entry["signal"] = "STRONG BUY"
            elif rating >= 0.1:
                entry["signal"] = "BUY"
            elif rating <= -0.5:
                entry["signal"] = "STRONG SELL"
            elif rating <= -0.1:
                entry["signal"] = "SELL"
            else:
                entry["signal"] = "NEUTRAL"
        results.append(entry)
    return results


async def fetch(market: str, symbols: list[str], client: httpx.AsyncClient) -> list[dict]:
    is_stocks = market == "america"
    cols      = COLUMNS        if is_stocks else COLUMNS_COMMON
    col_names = COLUMN_NAMES   if is_stocks else COLUMN_NAMES_COMMON
    try:
        resp = await client.post(
            SCANNER_URL.format(market=market),
            json=_build_payload(symbols, cols),
            headers=HEADERS,
            timeout=30,
        )
        resp.raise_for_status()
        return _parse(resp.json(), col_names)
    except Exception as e:
        print(f"  [!] Scanner error ({market}): {e}")
        return []
