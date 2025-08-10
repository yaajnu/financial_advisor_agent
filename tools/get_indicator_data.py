import pandas as pd
from typing import Dict
from langchain.tools import tool
from financial_advisor_agent.utils import session
from financial_advisor_agent.sql_utils import IndicatorData


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

    query = session.query(IndicatorData).filter(
        IndicatorData.stock_symbol == stock_symbol,
        IndicatorData.timestamp.between(from_date, to_date),
    )
    df = pd.read_sql_query(query.statement, session.bind)
    df.fillna(0, inplace=True)  # Fill NaN values with "N/A"
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
        # Placeholder for fetching indicator data from an external source if not in the DB.
        # This part would be similar to get_stock_info's Zerodha logic but adapted for indicators.
        return {
            f"Indicator data for {stock_symbol} not found in the internal database. External fetching is not yet implemented."
        }
