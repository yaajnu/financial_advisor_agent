import pandas as pd
from typing import Dict
from langchain.tools import tool
from financial_advisor_agent.utils import check_internal_db, conn, cursor


@tool(
    "get_indicator_data",
    description="Get financial indicator data for a specific stock",
)
def get_indicator_data(stock_symbol: str, from_date: str, to_date: str) -> dict:
    """
    Get historical data for a specific indicator.

    Args:
        stock_symbol (str): The name of the stock to retrieve data for.
        from_date (str): The start date for the data retrieval.
        to_date (str): The end date for the data retrieval.

    Returns:
        str: Historical data for the specified stock.
    """
    if check_internal_db(cursor, stock_symbol, is_price_data=False):
        query = """SELECT * 
           FROM indicator_data 
           WHERE stock_symbol = ? AND timestamp BETWEEN ? AND ?"""

        df = pd.read_sql_query(query, conn, params=(stock_symbol, from_date, to_date))
        if not df.empty:
            return df[
                [
                    "timestamp",
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
            ].to_dict()
        else:
            return {
                f"No indicator data found for {stock_symbol} between {from_date} and {to_date} in the internal database."
            }
    else:
        # Placeholder for fetching indicator data from an external source if not in the DB.
        # This part would be similar to get_stock_info's Zerodha logic but adapted for indicators.
        return {
            f"Indicator data for {stock_symbol} not found in the internal database. External fetching is not yet implemented."
        }
