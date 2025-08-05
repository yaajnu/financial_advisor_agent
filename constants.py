from dotenv import load_dotenv
import os

load_dotenv("financial_advisor_agent/.env")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
ZERODHA_API_KEY = os.getenv("ZERODHA_API_KEY")
ZERODHA_API_KEY_SECRET = os.getenv("ZERODHA_API_KEY_SECRET")
ZERODHA_USER_ID = os.getenv("ZERODHA_USER_ID")
ZERODHA_PASSWORD = os.getenv("ZERODHA_PASSWORD")
ZERODHA_TWO_FACTOR_AUTH = os.getenv("ZERODHA_TWO_FACTOR_AUTH")
GOOGLE_SEARCH_API_KEY = os.getenv("GOOGLE_SEARCH_API_KEY")
key_secret = (
    ZERODHA_API_KEY,
    ZERODHA_API_KEY_SECRET,
    ZERODHA_USER_ID,
    ZERODHA_PASSWORD,
    ZERODHA_TWO_FACTOR_AUTH,
)
