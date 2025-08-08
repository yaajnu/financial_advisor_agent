import pyodbc
from financial_advisor_agent.constants import AZURE_SQL_CONNECTIONSTRING


def create_connection():
    conn = pyodbc.connect(AZURE_SQL_CONNECTIONSTRING)
    cursor = conn.cursor()
    return conn, cursor
