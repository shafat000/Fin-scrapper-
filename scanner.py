import httpx

BASE_URL = "https://www.tradingview.com"
SCANNER_URL = "https://scanner.tradingview.com/{market}/scan"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
    "Origin": BASE_URL,
    "Referer": BASE_URL,
    "Content-Type": "application/json",
}

COLUMNS = [
    "name", "description", "type", "subtype",
    "close", "open", "high", "low",
    "change", "change_abs", "change_from_open",
    "volume", "volume_change", "relative_volume_10d_calc",
    "market_cap_basic", "price_earnings_ttm",
    "earnings_per_share_basic_ttm", "dividends_yield_current",
    "sector", "industry",
    "Recommend.All",                    # overall technical rating (-1 to 1)
    "RSI", "RSI[1]",
    "MACD.macd", "MACD.signal",
    "EMA20", "EMA50", "EMA200",
    "SMA20", "SMA50", "SMA200",
    "BB.upper", "BB.lower",
    "VWAP",
    "ATR", "beta_1_year",
    "52_week_high", "52_week_low",
    "price_52_week_high", "price_52_week_low",
    "average_volume_10d_calc", "average_volume_30d_calc",
    "gap", "pre_change", "after_change",
    "exchange",
]

COLUMN_NAMES = [
    "symbol", "description", "type", "subtype",
    "price", "open", "high", "low",
    "change_%", "change_abs", "change_from_open_%",
    "volume", "volume_change_%", "relative_volume",
    "market_cap", "pe_ratio",
    "eps", "dividend_yield_%",
    "sector", "industry",
    "technical_rating",
    "rsi", "rsi_prev",
    "macd", "macd_signal",
    "ema20", "ema50", "ema200",
    "sma20", "sma50", "sma200",
    "bb_upper", "bb_lower",
    "vwap",
    "atr", "beta",
    "52w_high", "52w_low",
    "price_52w_high", "price_52w_low",
    "avg_vol_10d", "avg_vol_30d",
    "gap_%", "pre_market_change_%", "after_hours_change_%",
    "exchange",
]

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


def _build_payload(symbols: list[str]) -> dict:
    return {
        "symbols": {"tickers": symbols, "query": {"types": []}},
        "columns": COLUMNS,
    }


def _parse(data: dict) -> list[dict]:
    results = []
    for row in data.get("data", []):
        vals = row.get("d", [])
        entry = {}
        for i, key in enumerate(COLUMN_NAMES):
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
    resp = await client.post(
        SCANNER_URL.format(market=market),
        json=_build_payload(symbols),
        headers=HEADERS,
        timeout=30,
    )
    resp.raise_for_status()
    return _parse(resp.json())
