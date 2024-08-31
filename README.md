# LygoBot: Automated Cryptocurrency Trading

## Introduction and Objective
The **LygoBot** project, developed by Riccardo Girgenti and Francesco Ligorio, aims to automate cryptocurrency trading on the Binance platform. Utilizing Python and robust third-party API packages, the bot implements several trading strategies based on market indicators, focusing on maximizing profitability through automated trades. The project spans from September 2022 to June 2024.

For a deeper understanding of the strategies and methodologies, please refer to our detailed report: [LygoBot Project Report](report.pdf).

## Strategies Overview

### First Strategy: RSI-Based Trading
Our initial strategy utilizes the Relative Strength Index (RSI) to determine optimal entry and exit points for trades, operating on a one-minute timeframe to respond rapidly to market changes.

![RSI Strategy](images/RSI.jpg)

### Final Strategy: EMA Crossover
The refined strategy incorporates dual Exponential Moving Averages (EMA), specifically the 100-period and 200-period EMAs, to detect trends and execute trades based on EMA crossovers. This approach is designed to capitalize on longer-term market movements, reducing the impact of market noise.

![EMA Strategy](images/EMA.jpg)

## Optimization and Backtesting
Extensive backtesting over two years of BTC price data has been conducted to optimize the trading parameters. The bot initially coded in Python was later optimized using C++ for performance improvements, addressing large datasets and computation-heavy tasks efficiently.

### Results and Observations
Our results indicate a promising strategy, particularly in a commission-free trading environment. The bot has been actively trading with adjustments based on market conditions and has shown to be profitable under test conditions.

For real-time performance data and further insights into the trading strategies and results, visit: [LygoBot Live Data](https://rikygirg.com/home).

## Conclusion
LygoBot demonstrates the potential for automated trading strategies in the cryptocurrency market. Ongoing adjustments and optimizations ensure the bot remains effective across different market conditions.

For detailed analysis, mathematical models, and code, please refer to our full report: [LygoBot Project Report](report.pdf).
