from langchain_core.messages import SystemMessage
from datetime import datetime

market_sentiment_agent_prompt = (
    "You are an expert financial assistant with vast expertise in technical analysis. "
    "Your primary goal is to provide the accurate market sentiment for the stock by using the tools at your disposal. "
    "You can use the tools to find accurate information about the historical and indicator data and give the market sentiment as well as the latest news about the stock in question by using the relevant information from prompt. "
    "But don't use the tools to get data for more than 45 days in the past from the current date. "
    "The response provided should be concise and to the point and in a dictionary format with the keys 'sentiment', 'reasoning' , 'technical analysis' , 'volatility'. "
    "The sentiment should be one of the following: 'bullish', 'bearish', or 'neutral'. "
    "The reasoning should be a brief explanation of the sentiment based on the data and news. "
    "The technical analysis is done on the basis of the technical indicators that are obtained from the tool"
    "Volatility is determined by the price and volume fluctuations of the stock over a specific period of time."
    "If you dont have enough information to provide a sentiment, then return 'neutral' as the sentiment and 'Insufficient data to determine sentiment.' as the reasoning. "
    f"The current date is {datetime.now().strftime('%Y-%m-%d')}."
)
types_of_trading_strategies = {
    "Trend Following": {
        "description": "A strategy that aims to profit by identifying the direction of the market (the 'trend') and establishing a position in the same direction. The philosophy is 'the trend is your friend'.",
        "signals": [
            {
                "name": "Moving Average Crossover",
                "description": "A signal generated when a shorter-term moving average (e.g., 50-day) crosses above a longer-term one (e.g., 200-day). This is known as a 'Golden Cross' and indicates a potential new uptrend. The reverse, a 'Death Cross', signals a potential downtrend.",
            },
            {
                "name": "Price Structure",
                "description": "The classic definition of a trend. An uptrend is confirmed by a consistent pattern of 'Higher Highs and Higher Lows'. A downtrend is confirmed by 'Lower Highs and Lower Lows'.",
            },
            {
                "name": "Average Directional Index (ADX)",
                "description": "An indicator that measures the strength of a trend, not its direction. A reading above 25 suggests a strong trend is in place, making trend-following strategies more reliable.",
            },
        ],
    },
    "Mean Reversion": {
        "description": "A strategy based on the statistical concept that asset prices and historical returns eventually revert to their long-term mean or average level.",
        "signals": [
            {
                "name": "RSI (Overbought/Oversold)",
                "description": "The Relative Strength Index measures the speed and change of price movements. A reading below 30 typically indicates an asset is 'oversold' and may be due for a price increase. A reading above 70 indicates it is 'overbought' and may be due for a price decrease.",
            },
            {
                "name": "Bollinger Bands",
                "description": "These are bands placed two standard deviations above and below a central moving average. A price touching the lower band is considered relatively low and may revert higher, while a price touching the upper band is relatively high and may revert lower.",
            },
        ],
    },
    "Momentum Trading": {
        "description": "A strategy that aims to profit from the continuation of existing strong price movements. Momentum traders buy assets that are rising and sell them when they appear to have peaked.",
        "signals": [
            {
                "name": "MACD Crossover",
                "description": "The Moving Average Convergence Divergence indicator shows the relationship between two moving averages. When the MACD line crosses above its 'signal line', it's a bullish signal of increasing upward momentum. The reverse is a bearish signal.",
            },
            {
                "name": "High Trading Volume",
                "description": "A significant increase in trading volume accompanying a price move confirms the strength and conviction behind the move. It shows high participation and interest at the new price level.",
            },
        ],
    },
    "Breakout Trading": {
        "description": "A strategy used to enter the market when the price of an asset moves outside a defined support or resistance level, often with increased volume.",
        "signals": [
            {
                "name": "Support/Resistance Break",
                "description": "Support is a price level where buying pressure tends to halt a downtrend. Resistance is a level where selling pressure tends to halt an uptrend. A 'break' of these levels signals a potential continuation in that direction.",
            },
            {
                "name": "Volume Surge on Break",
                "description": "A valid breakout is typically accompanied by a significant spike in trading volume. This surge indicates strong conviction from traders and reduces the chance of a 'false breakout' or 'fakeout'.",
            },
        ],
    },
    "Swing Trading": {
        "description": "A style that attempts to capture gains in a stock within a period of a few days to several weeks. Swing traders identify potential price 'swings' and enter trades to profit from them.",
        "signals": [
            {
                "name": "Indicator Combination",
                "description": "Swing traders rarely rely on one signal. They look for confirmation across multiple indicators (e.g., a bullish MACD crossover combined with a rising RSI from an oversold level) to time their entries and exits.",
            },
            {
                "name": "Candlestick Patterns",
                "description": "Patterns like a 'Hammer' or 'Bullish Engulfing' pattern near a support level can signal the start of an up-swing. A 'Shooting Star' or 'Bearish Engulfing' pattern near resistance can signal the start of a down-swing.",
            },
        ],
    },
    "Volatility Trading": {
        "description": "A strategy that profits from the magnitude of price changes rather than the direction. It's often executed using options to bet on whether volatility will increase or decrease.",
        "signals": [
            {
                "name": "Implied vs. Historical Volatility",
                "description": "Implied Volatility (IV) is the market's forecast of future volatility, priced into options. Historical Volatility (HV) is the actual volatility of the past. Traders look for discrepancies, such as buying options when IV is cheap compared to expected HV.",
            },
            {
                "name": "Upcoming Catalysts",
                "description": "Events like company earnings, central bank meetings (e.g., RBI Monetary Policy), or national election results are known to cause significant price swings, leading to increased volatility.",
            },
        ],
    },
    "News-Based Trading": {
        "description": "A strategy that involves making decisions based on the market's reaction to breaking news and economic data releases.",
        "signals": [
            {
                "name": "Earnings Reports",
                "description": "Companies reporting revenue or profit (EPS) significantly above or below analyst expectations often experience a strong and immediate price reaction.",
            },
            {
                "name": "Macroeconomic Data",
                "description": "Key data points for the Indian market, such as CPI (inflation), IIP (Index of Industrial Production), and GDP growth figures, can move the entire market or specific sectors.",
            },
        ],
    },
    "Pairs Trading": {
        "description": "A market-neutral strategy that involves matching a long position with a short position in a pair of highly correlated instruments, such as two stocks in the same sector.",
        "signals": [
            {
                "name": "Price Ratio Deviation",
                "description": "Traders calculate the price ratio between two correlated stocks (e.g., Price of TCS / Price of Infosys). When this ratio deviates significantly from its historical average, they short the outperformer and buy the underperformer, betting the ratio will revert to the mean.",
            }
        ],
    },
    "Scalping": {
        "description": "An extremely short-term trading style where traders aim to make numerous small profits on minor price changes throughout the day.",
        "signals": [
            {
                "name": "Order Flow Imbalance",
                "description": "Using Level 2 market data, scalpers look for a significant imbalance between buy orders (bids) and sell orders (asks) at a specific price point, anticipating a very short-term price move.",
            },
            {
                "name": "Bid-Ask Spread",
                "description": "This is the difference between the highest price a buyer will pay and the lowest price a seller will accept. Scalpers need a very 'tight' spread to minimize their transaction costs on each trade.",
            },
        ],
    },
    "Quantitative (Algo) Trading": {
        "description": "A strategy that uses computer algorithms and statistical models to identify trading opportunities and execute trades automatically.",
        "signals": [
            {
                "name": "Model-Generated Score",
                "description": "An algorithm processes numerous inputs (technical, fundamental, news sentiment, etc.), assigns weights to each, and generates a composite score. A trade is triggered if the score crosses a predefined positive or negative threshold.",
            },
            {
                "name": "Statistical Arbitrage",
                "description": "Algorithms designed to detect and exploit small, temporary pricing inefficiencies between thousands of related securities (e.g., a stock and its futures contract) that are mathematically certain to correct themselves.",
            },
        ],
    },
}

strategy_selector_agent_prompt = (
    "You are a quant trader who has access to the latest market data and a summary of the current market conditions passed on to you by an expert financial analyst"
    "You have a list of strategies which have been proven to be effective in different market conditions along with the conditions in which they have been effective."
    "Your task is to select a strategy to use and give the price at which an entry can be made to the stock along with a stop loss based on how the market is currently behaving."
    # f"The trading strategies available to you are: {types_of_trading_strategies}"
)
