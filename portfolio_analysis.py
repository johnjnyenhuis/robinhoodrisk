import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

# Your Robinhood portfolio (edit this with your actual holdings)
my_portfolio = {
    'SPY': 7.58,
    'QQQ': 6.74,
    'GLD': 8.16,
    'NVDA': 10.0
}

class PortfolioRiskAnalyzer:
    def __init__(self, portfolio, risk_free_rate=0.04):  # 4% annual risk-free rate
        self.portfolio = portfolio
        self.risk_free_rate = risk_free_rate / 252  # Convert to daily rate
        self.start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
        self.end_date = datetime.now().strftime('%Y-%m-%d')
        self.ytd_start = datetime(datetime.now().year, 1, 1).strftime('%Y-%m-%d')  # Jan 1 of current year
        
    def get_data(self):
        """Fetch historical price data from yfinance"""
        tickers = list(self.portfolio.keys())
        data = yf.download(tickers, start=self.start_date, end=self.end_date)['Close']
        return data
        
    def calculate_returns(self, data):
        """Calculate daily returns for portfolio and individual stocks"""
        returns = data.pct_change().dropna()
        portfolio_returns = sum(
            returns[ticker] * (self.portfolio[ticker] / sum(self.portfolio.values()))
            for ticker in self.portfolio
        )
        return portfolio_returns, returns  # Returns exactly 2 values
    
    def calculate_portfolio_value(self, data):
        """Calculate daily portfolio value"""
        portfolio_value = sum(
            data[ticker] * self.portfolio[ticker] for ticker in self.portfolio
        )
        return portfolio_value
    
    def analyze(self):
        """Run the risk analysis with YTD and daily gains/losses"""
        data = self.get_data()
        portfolio_returns, stock_returns = self.calculate_returns(data)
        portfolio_values = self.calculate_portfolio_value(data)
        latest_prices = data.iloc[-1]  # Most recent prices
        portfolio_value = sum(latest_prices[ticker] * self.portfolio[ticker] 
                            for ticker in self.portfolio)
        
        # YTD and Daily calculations
        ytd_data = data.loc[self.ytd_start:]  # Data from Jan 1 to now
        ytd_start_prices = ytd_data.iloc[0]   # First prices of the year
        ytd_portfolio_start = sum(ytd_start_prices[ticker] * self.portfolio[ticker] 
                                for ticker in self.portfolio)
        ytd_gain_loss = ((portfolio_value / ytd_portfolio_start) - 1) * 100
        
        daily_prev_prices = data.iloc[-2]  # Previous day's prices
        daily_prev_portfolio = sum(daily_prev_prices[ticker] * self.portfolio[ticker] 
                                 for ticker in self.portfolio)
        daily_gain_loss = ((portfolio_value / daily_prev_portfolio) - 1) * 100
        
        # Annual metrics
        volatility = portfolio_returns.std() * np.sqrt(252)
        annual_return = portfolio_returns.mean() * 252
        
        # Sharpe Ratio
        excess_return = annual_return - (self.risk_free_rate * 252)
        sharpe = excess_return / volatility if volatility != 0 else 0.0
        
        # Sortino Ratio
        downside_returns = portfolio_returns[portfolio_returns < self.risk_free_rate]
        downside_deviation = downside_returns.std() * np.sqrt(252) if not downside_returns.empty else 0.0
        sortino = excess_return / downside_deviation if downside_deviation != 0 else 0.0
        
        # Print portfolio results
        print("\nPortfolio Summary:")
        print(f"Portfolio Value: ${portfolio_value:,.2f}")
        print(f"YTD Gain/Loss: {ytd_gain_loss:.2f}%")
        print(f"Daily Gain/Loss: {daily_gain_loss:.2f}%")
        print(f"Annual Return: {annual_return:.2%}")
        print(f"Annual Volatility: {volatility:.2%}")
        print(f"Sharpe Ratio: {sharpe:.2f}")
        print(f"Sortino Ratio: {sortino:.2f}")
        
        # Print individual stock results
        print("\nIndividual Stocks:")
        for ticker in self.portfolio:
            ytd_stock_start = ytd_start_prices[ticker]
            ytd_stock_end = latest_prices[ticker]
            ytd_stock_gain_loss = ((ytd_stock_end / ytd_stock_start) - 1) * 100
            daily_stock_prev = daily_prev_prices[ticker]
            daily_stock_gain_loss = ((ytd_stock_end / daily_stock_prev) - 1) * 100
            print(f"{ticker} ({self.portfolio[ticker]} shares):")
            print(f"  Current Price: ${ytd_stock_end:.2f}")
            print(f"  YTD Gain/Loss: {ytd_stock_gain_loss:.2f}%")
            print(f"  Daily Gain/Loss: {daily_stock_gain_loss:.2f}%")
        
        # Visualization with 4 subplots
        plt.figure(figsize=(12, 16))
        
        # Plot 1: Portfolio Value Over Time
        plt.subplot(4, 1, 1)
        for ticker in self.portfolio:
            stock_value = data[ticker] * self.portfolio[ticker]
            plt.plot(stock_value.index, stock_value, label=f"{ticker} ({self.portfolio[ticker]} shares)", alpha=0.7)
        plt.plot(portfolio_values.index, portfolio_values, label='Total Portfolio', color='black', linewidth=2)
        plt.title('Portfolio Value Over Time (Individual Stocks)')
        plt.xlabel('Date')
        plt.ylabel('Value ($)')
        plt.legend()
        plt.grid(True)
        
        # Plot 2: Daily Returns
        plt.subplot(4, 1, 2)
        for ticker in self.portfolio:
            plt.plot(stock_returns[ticker].index, stock_returns[ticker], label=f"{ticker}", alpha=0.7)
        plt.plot(portfolio_returns.index, portfolio_returns, label='Portfolio', color='black', linewidth=2)
        plt.axhline(y=0, color='red', linestyle='--', linewidth=0.5)
        plt.title('Daily Returns (Individual Stocks)')
        plt.xlabel('Date')
        plt.ylabel('Return')
        plt.legend()
        plt.grid(True)
        
        # Plot 3: Cumulative Returns
        plt.subplot(4, 1, 3)
        portfolio_cumulative = (1 + portfolio_returns).cumprod() - 1
        for ticker in self.portfolio:
            stock_cumulative = (1 + stock_returns[ticker]).cumprod() - 1
            plt.plot(stock_cumulative.index, stock_cumulative, label=f"{ticker}", alpha=0.7)
        plt.plot(portfolio_cumulative.index, portfolio_cumulative, label='Portfolio', color='black', linewidth=2)
        plt.title('Cumulative Returns (Individual Stocks)')
        plt.xlabel('Date')
        plt.ylabel('Cumulative Return')
        plt.legend()
        plt.grid(True)
        
        # Plot 4: Rolling Volatility (30-day)
        plt.subplot(4, 1, 4)
        portfolio_rolling_vol = portfolio_returns.rolling(window=30).std() * np.sqrt(252)
        for ticker in self.portfolio:
            stock_rolling_vol = stock_returns[ticker].rolling(window=30).std() * np.sqrt(252)
            plt.plot(stock_rolling_vol.index, stock_rolling_vol, label=f"{ticker}", alpha=0.7)
        plt.plot(portfolio_rolling_vol.index, portfolio_rolling_vol, label='Portfolio', color='black', linewidth=2)
        plt.title('30-Day Rolling Volatility (Individual Stocks)')
        plt.xlabel('Date')
        plt.ylabel('Annualized Volatility')
        plt.legend()
        plt.grid(True)
        
        plt.tight_layout()
        plt.show()

# Run the analysis
analyzer = PortfolioRiskAnalyzer(my_portfolio)
analyzer.analyze()