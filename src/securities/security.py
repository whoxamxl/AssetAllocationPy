import yahooquery as yq
import pandas as pd
import numpy as np
from forex_python.converter import CurrencyRates

class Security:

    def __init__(self, ticker):
        self.__ticker = ticker
        self.__name = self.__fetch_name()
        self.__exchange_name = self.__fetch_exchange_name()
        self.__category_name = self.__fetch_category_name()
        self.__expense_ratio = self.__fetch_expense_ratio()
        self.__dividend_yield = self.__fetch_dividend_yield()
        self.__historical_data = self.__fetch_historical_data()
        self.__std_5y = self.__fetch_std_5y()
        self.__std_5y_from_historical_data = self.__fetch_std_5y_from_historical_data()
        self.__geometric_mean_5y = self.__fetch_geometric_mean_5y()
        self.__adjusted_geometric_mean_5y = self.__fetch_adjusted_geometric_mean_5y()
        self.__traded_currency = self.__fetch_traded_currency()
        self.__var_95_USD = self.__calculate_var_monte_carlo()
        self.__risk_weight = None
        self.__asset_weight = None

    def __fetch_name(self):
        etf = yq.Ticker(self.__ticker)
        return etf.quote_type.get(self.__ticker, {}).get("longName", "Unknown")

    def __fetch_exchange_name(self):
        etf = yq.Ticker(self.__ticker)
        return etf.price.get(self.__ticker, {}).get("exchangeName", "Unknown")

    def __fetch_category_name(self):
        etf = yq.Ticker(self.__ticker)
        ticker_fund_profile = etf.fund_profile.get(self.__ticker, {})
        if isinstance(ticker_fund_profile, dict):
            return ticker_fund_profile.get('categoryName', "Unknown")
        return "Unknown"

    def __fetch_expense_ratio(self):
        etf = yq.Ticker(self.__ticker)
        ticker_fund_profile = etf.fund_profile.get(self.__ticker, {})
        if isinstance(ticker_fund_profile, dict):
            expense_ratio = (ticker_fund_profile.get("feesExpensesInvestment", {})
                             .get("annualReportExpenseRatio", "Unknown"))
            if expense_ratio is not None and not isinstance(expense_ratio, str):
                # Convert the yield to percentage
                return round(expense_ratio * 100, 2)
        return "Unknown"

    def __fetch_dividend_yield(self):
        etf = yq.Ticker(self.__ticker)
        dividend_yield = etf.summary_detail.get(self.__ticker, {}).get("dividendYield", "Unknown")
        if dividend_yield == "Unknown":
            dividend_yield = etf.summary_detail.get(self.__ticker, {}).get("yield", "Unknown")
        if dividend_yield is not None and not isinstance(dividend_yield, str):
            # Convert the yield to percentage
            return round(dividend_yield * 100, 2)
        return dividend_yield

    def __fetch_historical_data(self):
        ticker_data = yq.Ticker(self.__ticker)
        historical_data = ticker_data.history(period="5y").xs(self.__ticker, level='symbol')
        historical_data.index = pd.to_datetime(historical_data.index)  # Convert index to DatetimeIndex
        return historical_data['close']

    def __fetch_std_5y(self):
        etf = yq.Ticker(self.__ticker)
        fund_performance = etf.fund_performance.get(self.__ticker, {})
        if isinstance(fund_performance, dict):
            risk_stats = fund_performance.get("riskOverviewStatistics").get("riskStatistics")
            return risk_stats[0].get("stdDev", "Unknown")
        return "Unknown"

    def __fetch_std_5y_from_historical_data(self):
        if self.__historical_data is not None:
            yearly_prices = self.__historical_data.resample('Y').last()
            yearly_returns = yearly_prices.pct_change().dropna()
            return round(yearly_returns.std() * 100, 2)
        return "Unknown"

    def __fetch_geometric_mean_5y(self):
        # Resample the data to get the last price of each year
        yearly_prices = self.__historical_data.resample('Y').last()

        # Calculate yearly returns
        yearly_returns = yearly_prices.pct_change().dropna()

        # Calculate the geometric mean of the returns
        geometric_mean = (yearly_returns + 1).prod() ** (1 / len(yearly_returns)) - 1

        return round(geometric_mean * 100, 2)

    def __fetch_adjusted_geometric_mean_5y(self):
        # Resample the data to get the last price of each year
        yearly_prices = self.__historical_data.resample('Y').last()

        # Calculate yearly returns
        yearly_returns = yearly_prices.pct_change().dropna()

        # Adjust yearly returns by adding the dividend yield
        # Assuming self.__dividend_yield is the average annual dividend yield for the security
        adjusted_yearly_returns = yearly_returns + self.__dividend_yield / 100

        # Calculate the geometric mean of the adjusted returns
        geometric_mean = (adjusted_yearly_returns + 1).prod() ** (1 / len(adjusted_yearly_returns)) - 1

        return round(geometric_mean * 100, 2)

    def __fetch_traded_currency(self):
        etf = yq.Ticker(self.__ticker)
        return etf.summary_detail.get(self.__ticker, {}).get("currency", "Unknown")

    def __calculate_var_monte_carlo(self, base_currency='USD', time_horizon=252, n_simulations=10000, confidence_level=0.95):
        if self.__historical_data is not None:
            # Use adjusted geometric mean as the expected return
            mean_return = self.__adjusted_geometric_mean_5y / 100 / time_horizon

            # Use historical standard deviation
            std_return = self.__std_5y_from_historical_data / 100 / np.sqrt(time_horizon)

            # Simulate future price paths
            simulated_returns = np.random.normal(mean_return, std_return, (time_horizon, n_simulations))
            simulated_prices = self.__historical_data.iloc[-1] * np.cumprod(1 + simulated_returns, axis=0)

            # Calculate the VaR
            var_absolute = np.percentile(simulated_prices[-1], (1 - confidence_level) * 100)
            var_in_local_currency = self.__historical_data.iloc[-1] - var_absolute

            # Fetch the trading currency of the security
            trading_currency = self.__traded_currency

            # Convert the VaR to the base currency
            return self.__convert_currency(var_in_local_currency, trading_currency, base_currency)

        else:
            return "Unknown"

    def __convert_currency(self, amount, from_currency, to_currency):
        if from_currency != to_currency:
            currency_converter = CurrencyRates()
            exchange_rate = currency_converter.get_rate(from_currency, to_currency)
            return amount * exchange_rate
        else:
            return amount

    def set_std_5y(self):
        self.__std_5y = self.__fetch_std_5y()

    def set_geometric_mean_5y(self):
        self.__geometric_mean_5y = self.__fetch_geometric_mean_5y()

    @property
    def ticker(self):
        return self.__ticker

    @property
    def name(self):
        return self.__name

    @property
    def exchange_name(self):
        return self.__exchange_name

    @property
    def category_name(self):
        return self.__category_name

    @property
    def expense_ratio(self):
        return self.__expense_ratio

    @property
    def dividend_yield(self):
        return self.__dividend_yield

    @property
    def historical_data(self):
        return self.__historical_data

    @property
    def std_5y(self):
        return self.__std_5y

    @property
    def std_5y_from_historical_data(self):
        return self.__std_5y_from_historical_data

    @property
    def geometric_mean_5y(self):
        return self.__geometric_mean_5y

    @property
    def adjusted_geometric_mean_5y(self):
        return self.__adjusted_geometric_mean_5y

    @property
    def var_95_USD(self):
        return self.__var_95_USD

    @property
    def traded_currency(self):
        return self.__traded_currency

    @property
    def risk_weight(self):
        return self.__risk_weight

    @property
    def asset_weight(self):
        return self.__asset_weight