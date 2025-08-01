import talib
import requests


def check_internal_db(cursor, stock_symbol: str, is_price_data: bool = True) -> bool:
    """
    Check if the stock symbol exists in the internal database.
    """
    if is_price_data:
        query = """
            SELECT COUNT(*) 
            FROM historical_price_data 
            WHERE stock_symbol = ?
            """
    else:
        query = """
            SELECT COUNT(*) 
            FROM indicator_data 
            WHERE stock_symbol = ?"""
    cursor.execute(query, (stock_symbol,))
    result = cursor.fetchone()
    return result[0] > 0


def calculate_indicators(df):
    # RSI
    df["RSI"] = talib.RSI(df["close"], timeperiod=14)

    # EMAs
    df["EMA_5"] = talib.EMA(df["close"], timeperiod=5)
    df["EMA_9"] = talib.EMA(df["close"], timeperiod=9)
    df["EMA_20"] = talib.EMA(df["close"], timeperiod=20)

    # VWAP
    typical_price = (df["high"] + df["low"] + df["close"]) / 3
    df["VWAP"] = (typical_price * df["volume"]).cumsum() / df["volume"].cumsum()

    # MACD
    df["MACD"], df["MACD_Signal"], df["MACD_Histogram"] = talib.MACD(
        df["close"], fastperiod=12, slowperiod=26, signalperiod=9
    )

    # Volume Average and Ratio
    df["Volume_SMA_5"] = talib.SMA(df["volume"], timeperiod=5)
    df["Volume_Ratio"] = df["volume"] / df["Volume_SMA_5"]

    # Pre-market change
    # df['Premarket_Change'] = ((df['premarket_close'] - df['previous_close']) / df['previous_close']) * 100

    return df


def google_search(
    query, google_search_api_key, cx="50dbf62988d304d9d", start_date=None, end_date=None
):
    """Search Google using Programmable Search API"""
    url = "https://www.googleapis.com/customsearch/v1"
    params = {"q": query, "key": google_search_api_key, "cx": cx, "num": 10}
    if start_date and end_date:
        params["sort"] = f"date:r:{start_date}:{end_date}"
    response = requests.get(url, params=params)
    return response.json()
