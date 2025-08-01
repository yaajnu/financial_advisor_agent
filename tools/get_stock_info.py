from langchain_core.tools import tool
from kiteconnect import KiteConnect
from ..utils import (
    create_sqlite_connection,
    autologin_zerodha,
    check_internal_db,
    calculate_indicators,
)
from ..constants import key_secret
import pandas as pd

conn, cursor = create_sqlite_connection("financial_advisor.db")


@tool(
    "get_stock_info",
    description="Get historical information about a stock including historical data",
)
def get_stock_info(stock_symbol: str, from_date: str, to_date: str) -> dict:
    """
    Get information about a stock.

    Args:
        stock_symbol (str): The stock symbol to get information for.
        from_date (str): The start date for the data retrieval.
        to_date (str): The end date for the data retrieval.

    Returns:
        str: Information about the stock.
    """
    # Placeholder for actual stock information retrieval logic
    if check_internal_db(stock_symbol):
        query = """SELECT * 
            FROM historical_price_data 
            WHERE stock_symbol = ? AND timestamp BETWEEN ? AND ?        """
        cursor.execute(query, (stock_symbol, from_date, to_date))
        result = cursor.fetchall()
        if result:
            print("BONDAAAAAAAAAAAA")
            return pd.DataFrame(result).to_dict()
        else:
            return {
                f"No data found for {stock_symbol} between {from_date} and {to_date}."
            }
    else:
        print("extracting from zerodha")
        """ ZERODHA FETCH DATA LOGIC"""
        access_token = autologin_zerodha(key_secret)
        print(f"Access Token: {access_token}")
        print(f"Key Secret: {key_secret}")
        kite = KiteConnect(api_key=key_secret[0])
        kite.set_access_token(access_token)
        all_insts = kite.instruments("BSE")
        all_insts_df = pd.DataFrame(all_insts)
        stock_symbol = stock_symbol.upper()
        if stock_symbol not in all_insts_df["tradingsymbol"].values:
            return {f"Stock symbol {stock_symbol} not found in Zerodha instruments."}
        else:
            instrument_token = all_insts_df[
                all_insts_df["tradingsymbol"] == stock_symbol
            ]["instrument_token"].values[0]
            stock_symbol = all_insts_df[all_insts_df["tradingsymbol"] == stock_symbol][
                "tradingsymbol"
            ].values[0]
            stock_name = all_insts_df[all_insts_df["tradingsymbol"] == stock_symbol][
                "name"
            ].values[0]
        historical_data = kite.historical_data(
            from_date=from_date,
            to_date=to_date,
            interval="minute",
            instrument_token=instrument_token,
        )
        # Convert to DataFrame for easier manipulation
        historical_data_df = pd.DataFrame(historical_data)
        historical_data_df["timestamp"] = historical_data_df["date"].astype("str")
        historical_data_df.drop(columns=["date"], inplace=True)
        calculate_indicators(historical_data_df)
        historical_data_df["stock_symbol"] = stock_symbol
        historical_data_df["stock_name"] = stock_name
        temp = historical_data_df[
            [
                "timestamp",
                "stock_symbol",
                "stock_name",
                "RSI",
                "EMA_5",
                "EMA_9",
                "EMA_20",
                "VWAP",
                "MACD",
                "MACD_Signal",
                "MACD_Histogram",
                "Volume_SMA_5",
                "Volume_Ratio",
            ]
        ]
        try:
            temp.to_sql("indicator_data", conn, if_exists="append", index=False)
            historical_data_df.drop(
                columns=[
                    "RSI",
                    "EMA_5",
                    "EMA_9",
                    "EMA_20",
                    "VWAP",
                    "MACD",
                    "MACD_Signal",
                    "MACD_Histogram",
                    "Volume_SMA_5",
                    "Volume_Ratio",
                ],
                inplace=True,
            )
            return historical_data_df.to_dict()
        except Exception as e:
            print(f"Error occurred while saving to database: {e}")
            historical_data_df.drop(
                columns=[
                    "RSI",
                    "EMA_5",
                    "EMA_9",
                    "EMA_20",
                    "VWAP",
                    "MACD",
                    "MACD_Signal",
                    "MACD_Histogram",
                    "Volume_SMA_5",
                    "Volume_Ratio",
                ],
                inplace=True,
            )
            return historical_data_df.to_dict()
