from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    DateTime,
    Numeric,
    BigInteger,
    UniqueConstraint,
)
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func

# --- Boilerplate Setup ---
# Base class for our declarative models
Base = declarative_base()


# --- 1. historical_price_data Table Model ---
class HistoricalPriceData(Base):
    __tablename__ = "historical_price_data"

    id = Column(Integer, primary_key=True)
    # Using DateTime(timezone=True) creates a TIMESTAMPTZ column in PostgreSQL
    # server_default sets the default at the database level
    timestamp = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    stock_symbol = Column(String, nullable=False)
    stock_name = Column(String)
    # Numeric is the best type for prices to avoid floating-point errors
    open = Column(Numeric(19, 4))
    high = Column(Numeric(19, 4))
    low = Column(Numeric(19, 4))
    close = Column(Numeric(19, 4))
    volume = Column(BigInteger)

    # --- Define the multi-column UNIQUE index ---
    __table_args__ = (
        UniqueConstraint(
            "timestamp", "stock_symbol", name="uq_historical_timestamp_symbol"
        ),
    )


# --- 2. indicator_data Table Model ---
class IndicatorData(Base):
    __tablename__ = "indicator_data"

    id = Column(Integer, primary_key=True)
    timestamp = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    stock_symbol = Column(String, nullable=False)
    stock_name = Column(String)
    RSI = Column(Numeric(10, 4))
    EMA_5 = Column(Numeric(10, 4))
    EMA_9 = Column(Numeric(10, 4))
    EMA_20 = Column(Numeric(10, 4))
    VWAP = Column(Numeric(10, 4))
    MACD = Column(Numeric(10, 4))
    MACD_Signal = Column(Numeric(10, 4))
    MACD_Histogram = Column(Numeric(10, 4))
    Volume_SMA_5 = Column(Numeric(18, 4))
    Volume_Ratio = Column(Numeric(10, 4))

    # --- Define the multi-column UNIQUE index ---
    __table_args__ = (
        UniqueConstraint(
            "timestamp", "stock_symbol", name="uq_indicator_timestamp_symbol"
        ),
    )
