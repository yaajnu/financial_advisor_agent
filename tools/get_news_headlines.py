from typing import Dict
import pandas as pd
from newspaper import Article
from langchain.tools import tool
from .utils import google_search
from financial_advisor_agent.constants import GOOGLE_SEARCH_API_KEY


@tool(
    "get_news_headlines", description="Get recent news headlines for a specific stock"
)
def get_news_headlines(stock_symbol: str, from_date: str) -> dict:
    """
    Get recent news headlines for a specific stock.

    Args:
        stock_symbol (str): The stock symbol to get news headlines for.

    Returns:
        str: Recent news headlines related to the stock.
    """
    start_date = pd.to_datetime(from_date) - pd.DateOffset(days=30)
    google_search_api_key = GOOGLE_SEARCH_API_KEY
    temp = google_search(
        f"{stock_symbol} indian stock market news",
        google_search_api_key,
        start_date="".join(start_date.strftime("%Y-%m-%d").split("-")),
        end_date="".join(pd.to_datetime(from_date).strftime("%Y-%m-%d").split("-")),
    )
    articles = {}
    for index, item in enumerate(temp.get("items", [])):
        try:
            article = Article(item["link"])
            article.download()
            article.parse()
            articles[index] = article.text
            break
        except Exception as e:
            print(f"Error processing article {item['link']}: {e}")
            continue
    return articles
