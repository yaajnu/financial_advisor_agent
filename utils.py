from kiteconnect import KiteConnect
import sqlite3
from financial_advisor_agent.constants import POSTGRES_URI
from langchain_groq import ChatGroq
from selenium import webdriver
from selenium.webdriver.common.by import By
from pyotp import TOTP
import time


import sqlalchemy
from sqlalchemy.orm import sessionmaker


def create_connection():
    engine = sqlalchemy.create_engine(POSTGRES_URI)
    Session = sessionmaker(bind=engine)
    session = Session()

    return session, engine


session, engine = create_connection()

# conn, cursor = create_sqlite_connection("portfolio.db")


def init_chat_model(api_key: str):

    llm = ChatGroq(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        api_key=api_key,
    )
    return llm
