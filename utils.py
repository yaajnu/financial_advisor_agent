from kiteconnect import KiteConnect
import sqlite3
from langchain_groq import ChatGroq
from selenium import webdriver
from selenium.webdriver.common.by import By
from pyotp import TOTP
import time


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


def create_sqlite_connection(db_path: str):
    """Create a SQLite database connection."""
    conn = sqlite3.connect(db_path, check_same_thread=False)
    cursor = conn.cursor()
    return conn, cursor


conn, cursor = create_sqlite_connection("portfolio.db")


def init_chat_model(api_key: str):

    llm = ChatGroq(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        api_key=api_key,
    )
    return llm
