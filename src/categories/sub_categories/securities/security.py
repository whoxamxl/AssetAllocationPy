import yahooquery as yq
import pandas as pd
import numpy as np
from functools import lru_cache
from retrying import retry

from src.global_settings import RISK_FREE_RATE, TOTAL_PORTFOLIO_VALUE, DIVIDEND_TYPE


class DataFetchError(Exception):
    """ Custom exception for data fetch errors """
    pass


class NaNDataError(DataFetchError):
    """ Exception raised when data has too many NaN values """
    pass


class DuplicatedDataError(DataFetchError):
    """ Exception raised when data has too many duplicated values """
    pass


class Security:
    TBILL_3MONTHS = "^IRX"
    NAN_THRESHOLD = 0.1
    DUPLICATED_THRESHOLD = 0.1
    _risk_free_rate = None

    @classmethod
    def get_risk_free_rate(cls):
        if cls._risk_free_rate is None:
            if RISK_FREE_RATE is None:
                cls._risk_free_rate = cls.__fetch_risk_free_rate(cls.TBILL_3MONTHS)
            else:
                cls._risk_free_rate = RISK_FREE_RATE
        return cls._risk_free_rate

    @classmethod
    def __fetch_risk_free_rate(cls, ticker):
        try:
            treasury = yq.Ticker(ticker)
            data = treasury.history(period='1y')

            if not data.empty and 'close' in data.columns:
                return round(data['close'].iloc[-1] / 100, 5)
            else:
                raise ValueError("Data not available or invalid format")
        except Exception as e:
            print(f"Error fetching risk-free rate: {e}")
            return None

    def __init__(self, ticker, sub_category, sub_asset_weight):
        self.__ticker = ticker
        self.__sub_category = sub_category
        self.__sub_asset_weight = sub_asset_weight / 100
        self.__etf = yq.Ticker(self.__ticker)
        self.__name = None
        self.__category_name = None
        self.__exchange_name = None
        self.__traded_currency = None
        self.__expense_ratio = None
        self.__dividend_yield = None
        self.__avg_dividend_yield = None
        self.__historical_data = None
        self.__geometric_mean_5y = None
        self.__adjusted_geometric_mean_5y = None
        self.__adjusted_returns_in_series_5y = None
        self.__standard_deviation_5y = None
        self.__downside_deviation_5y = None
        self.__var_95 = None
        self.__sharpe_ratio = None
        self.__portfolio_asset_weight = None
        self.__portfolio_asset_allocation = None
        self.__number_of_shares = None

    def __fetch_name(self):
        try:
            ticker_quote_type = self.__etf.quote_type.get(self.__ticker, {})
            if isinstance(ticker_quote_type, dict):
                return ticker_quote_type.get('longName', "Unknown")
            return "Unknown"
        except Exception as e:
            print(f"Error fetching name for {self.__ticker}: {e}")
            return None

    def __fetch_category_name(self):
        try:
            ticker_fund_profile = self.__etf.fund_profile.get(self.__ticker, {})
            if isinstance(ticker_fund_profile, dict):
                return ticker_fund_profile.get('categoryName', "Unknown")
            return "Unknown"
        except Exception as e:
            print(f"Error fetching category name for {self.__ticker}: {e}")
            return None

    def __fetch_exchange_name(self):
        try:
            ticker_price = self.__etf.price.get(self.__ticker, {})
            if isinstance(ticker_price, dict):
                return ticker_price.get('exchangeName', "Unknown")
            return "Unknown"
        except Exception as e:
            print(f"Error fetching exchange name for {self.__ticker}: {e}")
            return None

    def __fetch_traded_currency(self):
        try:
            ticker_price = self.__etf.price.get(self.__ticker, {})
            if isinstance(ticker_price, dict):
                return ticker_price.get('currency', "Unknown")
            return "Unknown"
        except Exception as e:
            print(f"Error fetching traded currency for {self.__ticker}: {e}")
            return None

    def __fetch_expense_ratio(self):
        try:
            ticker_fund_profile = self.__etf.fund_profile.get(self.__ticker, {})
            if isinstance(ticker_fund_profile, dict):
                expense_ratio = (ticker_fund_profile.get("feesExpensesInvestment", {})
                                 .get("annualReportExpenseRatio"))
                if expense_ratio is not None and not isinstance(expense_ratio, str):
                    try:
                        return round(float(expense_ratio), 5)
                    except (TypeError, ValueError):
                        print(f"Expense ratio value for {self.__ticker} is not a valid number.")
                        return None
            return None
        except Exception as e:
            print(f"Error fetching expense ratio for {self.__ticker}: {e}")
            return None

    def __fetch_dividend_yield(self):
        try:
            summary_detail = self.__etf.summary_detail.get(self.__ticker, {})
            # print(f"{self.__ticker}: {summary_detail}")
            if isinstance(summary_detail, dict):
                dividend_yield = summary_detail.get("dividendYield")
                if dividend_yield is None:
                    dividend_yield = summary_detail.get("yield")
                if dividend_yield is not None and not isinstance(dividend_yield, str):
                    try:
                        dividend_yield = round(float(dividend_yield), 5)
                        # print(f"Fetched dividend yield for {self.__ticker}: {dividend_yield}")
                        return dividend_yield
                    except (TypeError, ValueError):
                        print(f"Dividend yield value for {self.__ticker} is not a valid number.")
                        return None
                else:
                    return 0
            return None
        except Exception as e:
            print(f"Error fetching dividend yield for {self.__ticker}: {e}")
            return None

    def __fetch_dividends_history(self):
        try:
            historical_data = self.__check_historical_data()
            # Extract the first date from the historical_data DataFrame
            start_date = historical_data.index.min()

            # Convert the date to the required format (yyyy-mm-dd)
            start_date_str = start_date.strftime('%Y-%m-%d')

            # Use this date to obtain the dividend history
            dividends_history = self.__etf.dividend_history(start_date_str)

            # Check if dividends_history is empty
            if dividends_history.empty:
                return 0.0

            # Reset the index of dividends_history to make 'date' a column
            dividends_history.reset_index(inplace=True)

            # Ensure 'date' column is in the correct format
            dividends_history['date'] = pd.to_datetime(dividends_history['date'])
            # print(dividends_history)

            # Resample the historical data to get the year-end prices
            yearly_prices = historical_data.resample('Y').last()
            # print(yearly_prices)

            # Calculate the total annual dividends
            dividends_history['year'] = pd.to_datetime(dividends_history['date']).dt.year
            total_dividends_per_year = dividends_history.groupby('year')['dividends'].sum()
            # print(total_dividends_per_year)

            # Convert the index of yearly_prices to just the year (as integers)
            yearly_prices.index = yearly_prices.index.year

            # Ensure both series are aligned by year
            aligned_years = set(total_dividends_per_year.index).intersection(set(yearly_prices.index))
            total_dividends_per_year = total_dividends_per_year[total_dividends_per_year.index.isin(aligned_years)]
            yearly_prices = yearly_prices[yearly_prices.index.isin(aligned_years)]

            # Calculate the dividend yields
            dividend_yields = total_dividends_per_year / yearly_prices

            # Calculate the average dividend yield
            average_dividend_yield = dividend_yields.mean()

            return round(average_dividend_yield, 5)
        except Exception as e:
            print(f"Error in calculating average dividend yield for {self.__ticker}: {e}")
            return None


    def __is_data_valid(self, data, ticker):
        # Check for a significant amount of NaN values
        if data.isna().sum() / len(data) > Security.NAN_THRESHOLD:  # Example threshold for NaN values
            raise NaNDataError(f"{ticker} contains too many NaN values: {data.isna().sum()} out of {len(data)}")

        # Check for duplicated values
        if data.duplicated().sum() / len(data) > Security.DUPLICATED_THRESHOLD:
            raise DuplicatedDataError(
                f"{ticker} contains too many duplicated values: {data.duplicated().sum()} out of {len(data)}")

        return True

    @lru_cache(maxsize=None)
    @retry(stop_max_attempt_number=3, wait_fixed=1000, retry_on_exception=lambda e: isinstance(e, DataFetchError))
    def __fetch_historical_data(self):
        try:
            historical_data = self.__etf.history(period="5y").xs(self.__ticker, level='symbol')
            historical_data.index = pd.to_datetime(historical_data.index)  # Convert index to DatetimeIndex
            resample_historical_data = historical_data['close'].resample('D').last()
            resample_historical_data.interpolate(method='pchip', inplace=True)

            # This will now raise specific exceptions if the data is invalid
            # self.__is_data_valid(resample_historical_data, self.__ticker)

            return resample_historical_data.dropna()
        except (NaNDataError, DuplicatedDataError) as e:
            print(f"Validation failed for {self.__ticker}: {e}")
            raise  # Reraise the specific validation exception to trigger a retry
        except Exception as e:
            print(f"Error fetching historical data for {self.__ticker}: {e}")
            raise  # Reraise any other exceptions

    def __check_historical_data(self):
        historical_data = self.historical_data
        if historical_data is None or historical_data.empty:
            raise ValueError("Historical data is missing or empty")
        return historical_data

    def __calculate_geometric_mean_5y(self):
        try:
            historical_data = self.__check_historical_data()

            yearly_prices = historical_data.resample('Y').last()
            yearly_returns = yearly_prices.pct_change().dropna()

            if len(yearly_returns) == 0:
                raise ValueError("No yearly returns data available for calculation")

            geometric_mean = (yearly_returns + 1).prod() ** (1 / len(yearly_returns)) - 1
            return round(geometric_mean, 5)
        except Exception as e:
            print(f"Error in calculating geometric mean for {self.__ticker}: {e}")
            return None

    def __calculate_adjusted_geometric_mean_5y(self):
        try:
            historical_data = self.__check_historical_data()

            yearly_prices = historical_data.resample('Y').last()
            yearly_returns = yearly_prices.pct_change().dropna()

            if len(yearly_returns) == 0:
                raise ValueError("No yearly returns data available for calculation")

            dividend_yield = self.dividend_yield
            if dividend_yield is None:
                raise ValueError("Dividend yield data is missing")

            adjusted_yearly_returns = yearly_returns + dividend_yield
            geometric_mean = (adjusted_yearly_returns + 1).prod() ** (1 / len(adjusted_yearly_returns)) - 1
            return round(geometric_mean, 5)
        except Exception as e:
            print(f"Error in calculating adjusted geometric mean for {self.__ticker}: {e}")
            return None

    def __calculate_adjusted_returns_in_series_5y(self):
        try:
            historical_data = self.__check_historical_data()

            daily_prices = historical_data.resample('D').last()
            daily_returns = daily_prices.pct_change().dropna()

            if len(daily_returns) == 0:
                raise ValueError("No daily returns data available for calculation")

            dividend_yield = self.avg_dividend_yield if DIVIDEND_TYPE == "avg" else self.dividend_yield
            if dividend_yield is None:
                raise ValueError("Dividend yield data is missing")


            adjusted_daily_returns = daily_returns + (dividend_yield / 252)
            return round(adjusted_daily_returns, 5)
        except Exception as e:
            print(f"Error in calculating adjusted returns in series for {self.__ticker}: {e}")
            return None

    def __calculate_std_5y(self):
        try:
            historical_data = self.__check_historical_data()

            yearly_prices = historical_data.resample('Y').last()
            yearly_returns = yearly_prices.pct_change().dropna()

            if len(yearly_returns) == 0:
                raise ValueError("No yearly returns data available for calculation")

            return round(yearly_returns.std(), 5)
        except Exception as e:
            print(f"Error in calculating standard deviation for {self.__ticker}: {e}")
            return None

    def __calculate_downside_deviation_5y(self):
        try:
            historical_data = self.__check_historical_data()

            yearly_prices = historical_data.resample('Y').last()
            yearly_returns = yearly_prices.pct_change().dropna()

            if len(yearly_returns) == 0:
                raise ValueError("No yearly returns data available for calculation")

            mar = Security.get_risk_free_rate()
            if mar is None:
                raise ValueError("Risk-free rate is missing")

            excess_returns = np.minimum(0, yearly_returns - mar)
            downside_risk = np.sqrt(np.mean(excess_returns ** 2))
            return downside_risk
        except Exception as e:
            print(f"Error in calculating downside deviation for {self.__ticker}: {e}")
            return None

    def __calculate_var_monte_carlo(self, n_simulations=10000, confidence_level=0.95):
        try:
            historical_data = self.__check_historical_data()

            mean_return = self.adjusted_geometric_mean_5y
            std_return = self.standard_deviation_5y

            if mean_return is None or std_return is None:
                raise ValueError("Mean return or standard deviation is missing")

            simulated_returns = np.random.normal(mean_return, std_return, n_simulations)
            simulated_prices = historical_data.iloc[-1] * (1 + simulated_returns)

            var_absolute = np.percentile(simulated_prices, (1 - confidence_level) * 100)
            last_price = historical_data.iloc[-1]
            var_percent = (var_absolute - last_price) / last_price
            return round(var_percent, 5)
        except Exception as e:
            print(f"Error in calculating VaR for {self.__ticker}: {e}")
            return None

    def __calculate_sharpe_ratio(self):
        try:
            investment_return = self.adjusted_geometric_mean_5y
            standard_deviation = self.standard_deviation_5y
            risk_free_rate = Security.get_risk_free_rate()

            if investment_return is None or standard_deviation is None or risk_free_rate is None:
                raise ValueError("Required data for Sharpe ratio calculation is missing")

            sharpe_ratio = (investment_return - risk_free_rate) / standard_deviation
            return round(sharpe_ratio, 2)
        except Exception as e:
            print(f"Error in calculating Sharpe ratio for {self.__ticker}: {e}")
            return None

    def __calculate_number_of_shares(self):
        try:
            historical_data = self.__check_historical_data()
            last_price = historical_data.iloc[-1]
            return round(self.portfolio_asset_allocation / last_price, 2)
        except Exception as e:
            print(f"Error in calculating number of shares for {self.__ticker}: {e}")
            return None

    @property
    def ticker(self):
        return self.__ticker

    @property
    def sub_category(self):
        return self.__sub_category

    @property
    def sub_asset_weight(self):
        return self.__sub_asset_weight

    @property
    def name(self):
        if self.__name is None:
            self.__name = self.__fetch_name()
        return self.__name

    @property
    def category_name(self):
        if self.__category_name is None:
            self.__category_name = self.__fetch_category_name()
        return self.__category_name

    @property
    def exchange_name(self):
        if self.__exchange_name is None:
            self.__exchange_name = self.__fetch_exchange_name()
        return self.__exchange_name

    @property
    def traded_currency(self):
        if self.__traded_currency is None:
            self.__traded_currency = self.__fetch_traded_currency()
        return self.__traded_currency

    @property
    def expense_ratio(self):
        if self.__expense_ratio is None:
            self.__expense_ratio = self.__fetch_expense_ratio()
        return self.__expense_ratio

    @property
    def dividend_yield(self):
        if self.__dividend_yield is None:
            self.__dividend_yield = self.__fetch_dividend_yield()
        return self.__dividend_yield

    @property
    def avg_dividend_yield(self):
        if self.__avg_dividend_yield is None:
            self.__avg_dividend_yield = self.__fetch_dividends_history()
        return self.__avg_dividend_yield

    @property
    def historical_data(self):
        if self.__historical_data is None:
            self.__historical_data = self.__fetch_historical_data()
        return self.__historical_data

    @property
    def geometric_mean_5y(self):
        if self.__geometric_mean_5y is None:
            self.__geometric_mean_5y = self.__calculate_geometric_mean_5y()
        return self.__geometric_mean_5y

    @property
    def adjusted_geometric_mean_5y(self):
        if self.__adjusted_geometric_mean_5y is None:
            self.__adjusted_geometric_mean_5y = self.__calculate_adjusted_geometric_mean_5y()
        return self.__adjusted_geometric_mean_5y

    @property
    def adjusted_returns_in_series_5y(self):
        if self.__adjusted_returns_in_series_5y is None:
            self.__adjusted_returns_in_series_5y = self.__calculate_adjusted_returns_in_series_5y()
        return self.__adjusted_returns_in_series_5y

    @property
    def standard_deviation_5y(self):
        if self.__standard_deviation_5y is None:
            self.__standard_deviation_5y = self.__calculate_std_5y()
        return self.__standard_deviation_5y

    @property
    def downside_deviation_5y(self):
        if self.__downside_deviation_5y is None:
            self.__downside_deviation_5y = self.__calculate_downside_deviation_5y()
        return self.__downside_deviation_5y

    @property
    def var_95(self):
        if self.__var_95 is None:
            self.__var_95 = self.__calculate_var_monte_carlo()
        return self.__var_95

    @property
    def sharpe_ratio(self):
        if self.__sharpe_ratio is None:
            self.__sharpe_ratio = self.__calculate_sharpe_ratio()
        return self.__sharpe_ratio

    @property
    def portfolio_asset_weight(self):
        return self.__portfolio_asset_weight

    @property
    def portfolio_asset_allocation(self):
        if self.__portfolio_asset_allocation is None:
            if self.portfolio_asset_weight is not None:
                self.__portfolio_asset_allocation = TOTAL_PORTFOLIO_VALUE * self.portfolio_asset_weight
        return self.__portfolio_asset_allocation

    @property
    def number_of_shares(self):
        if self.__number_of_shares is None:
            self.__number_of_shares = self.__calculate_number_of_shares()
        return self.__number_of_shares

    @portfolio_asset_weight.setter
    def portfolio_asset_weight(self, weight):
        if weight < 0 or weight > 1:
            raise ValueError("Portfolio asset weight must be between 0 and 1")
        self.__portfolio_asset_weight = weight
