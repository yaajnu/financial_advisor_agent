import os
from langchain_core.tools import tool, BaseTool
from financial_advisor_agent.utils import session
from financial_advisor_agent.sql_utils import HistoricalPriceData, IndicatorData
from sqlalchemy.dialects.postgresql import insert
from langchain_core.tools import InjectedToolArg, tool
from typing_extensions import Annotated
from langgraph.prebuilt.chat_agent_executor import AgentState

from .utils import calculate_indicators
from financial_advisor_agent.constants import key_secret
import pandas as pd

from pydantic import BaseModel, Field
from typing import Optional


# This class defines the "form" the LLM needs to fill out.
class StockInfoInput(BaseModel):
    stock_symbol: str = Field(
        ...,
        description="The stock ticker symbol, for example 'RELIANCE' or 'ANGELONE'.",
    )
    from_date: str = Field(
        ...,
        description="The start date for the data in YYYY-MM-DD format. The current year is 2025 if not specified.",
    )
    to_date: str = Field(
        ...,
        description="The end date for the data in YYYY-MM-DD format. The current year is 2025 if not specified.",
    )
    kite: Annotated[object, InjectedToolArg] = Field(
        ...,
        description="The Kite Connect client instance for accessing stock data.",
    )


class State(AgentState):
    kite: object  # = Field(
    #     ...,
    #     description="The Kite Connect client instance for accessing stock data.",
    # )


from langgraph.prebuilt import InjectedState


@tool(
    "get_stock_info",
    description="Get historical information about a stock including historical data",
    # args_schema=StockInfoInput,
)
def get_stock_info(
    stock_symbol: str,
    from_date: str,
    to_date: str,
    kite: Annotated[dict, InjectedState],
) -> dict:
    """
        Get information about a stock.

    Args:
        stock_symbol (str): The stock symbol to get information for.
        from_date (str): The start date for the data retrieval.
        to_date (str): The end date for the data retrieval.
        kite (object): Kite Connect instance for accessing stock data.

    Returns:
        str: Information about the stock.
    """
    # Placeholder for actual stock information retrieval logic
    # print(f"Received args: {args}")
    # stock_symbol = args.stock_symbol
    # from_date = args.from_date
    # to_date = args.to_date
    access_token = os.environ.get("KITE_ACCESS_TOKEN")
    query = (
        session.query(HistoricalPriceData)
        .filter(
            HistoricalPriceData.stock_symbol == stock_symbol,
            HistoricalPriceData.timestamp.between(from_date, to_date),
        )
        .order_by(HistoricalPriceData.timestamp)
    )
    result = pd.read_sql(query.statement, query.session.bind)
    if not result.empty:
        print("BONDAAAAAAAAAAAA")
        return result.to_dict()
    else:
        print("extracting from zerodha")
        """ ZERODHA FETCH DATA LOGIC"""

        if not access_token:
            print("Access token not found, please AUTHENTICATE first.")
            return {f"Access token not found for accessing the {stock_symbol} data."}
        kite = kite["kite"]
        all_insts = kite.instruments("NSE")
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
            interval="60minute",
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
            table_model = IndicatorData.__table__
            records_to_insert = temp.to_dict(orient="records")
            insert_stmt = insert(table_model).values(records_to_insert)
            # Define the final "upsert" statement
            upsert_stmt = insert_stmt.on_conflict_do_nothing(
                index_elements=["timestamp", "stock_symbol"]
            )

            session.execute(upsert_stmt)
            session.commit()
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
