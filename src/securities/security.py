import yahooquery as yq
import pandas as pd

class Security:

    def __init__(self, ticker):
        self.__ticker = ticker
        self.__name = self.__fetch_name()
        self.__exchange_name = self.__fetch_exchange_name()
        self.__category_name = self.__fetch_category_name()
        self.__expense_ratio = self.__fetch_expense_ratio()
        self.__dividend_yield = self.__fetch_dividend_yield()
        self.__std_5y = self.__fetch_std_5y()
        self.__geometric_mean_5y = self.__fetch_geometric_mean_5y()
        self.__adjusted_geometric_mean_5y = self.__fetch_adjusted_geometric_mean_5y()
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

    def __fetch_std_5y(self):
        etf = yq.Ticker(self.__ticker)
        fund_performance = etf.fund_performance.get(self.__ticker, {})
        if isinstance(fund_performance, dict):
            risk_stats = fund_performance.get("riskOverviewStatistics").get("riskStatistics")
            return risk_stats[0].get("stdDev", "Unknown")
        return "Unknown"

    def __yearly_return_5y(self):
        # Create a Ticker object
        ticker_data = yq.Ticker(self.__ticker)

        # Fetch historical data for 5 years
        historical_data = ticker_data.history(period="5y")

        # Selecting the 'close' price for the IAU ticker
        iau_data = historical_data.xs(self.__ticker, level='symbol')['close']

        # Ensure the index is in a consistent datetime format
        iau_data.index = pd.to_datetime(iau_data.index)

        # Resample the data to get the last price of each year
        yearly_prices = iau_data.resample('Y').last()

        # Calculate yearly returns
        yearly_returns = yearly_prices.pct_change().dropna()

        return yearly_returns
    def __fetch_geometric_mean_5y(self):
        yearly_returns = self.__yearly_return_5y()

        # Calculate the geometric mean of the returns
        geometric_mean = (yearly_returns + 1).prod() ** (1 / len(yearly_returns)) - 1

        return round(geometric_mean * 100, 2)

    def __fetch_adjusted_geometric_mean_5y(self):
        yearly_returns = self.__yearly_return_5y()

        # Adjust yearly returns by adding the dividend yield
        # Assuming self.__dividend_yield is the average annual dividend yield for the security
        adjusted_yearly_returns = yearly_returns + self.__dividend_yield / 100

        # Calculate the geometric mean of the adjusted returns
        geometric_mean = (adjusted_yearly_returns + 1).prod() ** (1 / len(adjusted_yearly_returns)) - 1

        return round(geometric_mean * 100, 2)

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
    def std_5y(self):
        return self.__std_5y

    @property
    def geometric_mean_5y(self):
        return self.__geometric_mean_5y

    @property
    def adjusted_geometric_mean_5y(self):
        return self.__adjusted_geometric_mean_5y

    @property
    def risk_weight(self):
        return self.__risk_weight

    @property
    def asset_weight(self):
        return self.__asset_weight