from securities.security_type.alternative import Alternative
from securities.security_type.bond import Bond
from securities.security_type.equity import Equity

import pandas as pd
import numpy as np
import yahooquery as yq
import matplotlib.pyplot as plt


class SecurityManager:
    TBILL_3MONTHS = "^IRX"
    def __init__(self):
        self.securities = []
        self.risk_free_rate = self.__fetch_risk_free_rate()

    def add_security(self, ticker, sub_category, type):
        if not self.__security_exists(ticker):
            match type:
                case "Equity":
                    self.securities.append(Equity(ticker, sub_category))
                case "Bond":
                    self.securities.append(Bond(ticker, sub_category))
                case "Alternative":
                    self.securities.append(Alternative(ticker, sub_category))
                case _:
                    print("Unknown type.")
        else:
            print(f"Security with ticker {ticker} already exists.")

    def add_securities(self, securities_info):
        for ticker, sub_category, type in securities_info:
            if not self.__security_exists(ticker):
                match type:
                    case "Equity":
                        self.securities.append(Equity(ticker, sub_category))
                    case "Bond":
                        self.securities.append(Bond(ticker, sub_category))
                    case "Alternative":
                        self.securities.append(Alternative(ticker, sub_category))
                    case _:
                        print(f"Unknown type for ticker {ticker}.")
            else:
                print(f"Security with ticker {ticker} already exists.")

    def __security_exists(self, ticker):
        return any(security.ticker == ticker for security in self.securities)

    def remove_security(self, ticker):
        # Remove security with the specified ticker
        self.securities = [security for security in self.securities if security.ticker != ticker]

    def remove_securities(self, tickers_to_remove):
        self.securities = [security for security in self.securities if security.ticker not in tickers_to_remove]

    def __fetch_risk_free_rate(self):
        try:
            treasury = yq.Ticker(self.TBILL_3MONTHS)
            data = treasury.history(period='1y')

            if not data.empty and 'close' in data.columns:
                return data['close'].iloc[-1]
            else:
                raise ValueError("Data not available or invalid format")
        except Exception as e:
            print(f"Error fetching risk-free rate: {e}")
            return None

    def print_securities(self):
        for security in self.securities:
            print(
                f"Ticker: {security.ticker} Geometric Mean: {security.geometric_mean_5y}% Adjusted Geometric Mean: {security.adjusted_geometric_mean_5y}%")
            print(
                f"Std 5y from yahooquery: {security.std_5y} Std 5t from historical data: {security.std_5y_from_historical_data} VaR 95% in USD: {security.var_95_USD} Traded Currency: {security.traded_currency}")

    def calculate_aggregated_data(self):
        # Initialize dictionaries to store raw data for returns and standard deviations
        category_returns_data = {}
        category_std_dev_data = {}
        category_dividend_yield_data = {}

        for security in self.securities:
            # Get the category from the type of the security
            category = type(security).__name__

            # Initialize the lists for the category if not already done
            if category not in category_returns_data:
                category_returns_data[category] = []
                category_std_dev_data[category] = []
                category_dividend_yield_data[category] = []

            # Append the data for this security to the relevant category
            category_returns_data[category].append(security.adjusted_geometric_mean_5y)
            category_std_dev_data[category].append(security.std_5y)
            category_dividend_yield_data[category].append(security.dividend_yield)

        # Initialize new dictionaries for calculated averages
        category_averages_return = {}
        category_averages_std_dev = {}
        category_averages_dividend = {}

        # Calculate averages for returns and standard deviations for each category
        for category in category_returns_data:
            category_averages_return[category] = sum(category_returns_data[category]) / len(
                category_returns_data[category]) if category_returns_data[category] else 0
            category_averages_std_dev[category] = sum(category_std_dev_data[category]) / len(
                category_std_dev_data[category]) if category_std_dev_data[category] else 0
            category_averages_dividend[category] = sum(category_dividend_yield_data[category]) / len(
                category_dividend_yield_data[category]) if category_dividend_yield_data[category] else 0

        return category_averages_return, category_averages_std_dev, category_averages_dividend

    # TODO: historical data currency conversion
    def calculate_average_historical_data(self):
        category_avg_historical_data = pd.DataFrame()

        for category in set(type(security).__name__ for security in self.securities):
            category_securities = [sec for sec in self.securities if type(sec).__name__ == category]
            if not category_securities:
                continue

            # Standardize to tz-naive before aggregation
            aggregated_data = pd.concat([sec.historical_data.tz_localize(None) for sec in category_securities], axis=1)
            category_avg_historical_data[category] = aggregated_data.mean(axis=1)

        resample_category_avg_historical_data = category_avg_historical_data.resample('D').last()
        resample_category_avg_historical_data = resample_category_avg_historical_data.dropna()
        return resample_category_avg_historical_data

    def plot_category_historical_data(self):
        category_avg_historical_data = self.calculate_average_historical_data()
        plt.figure(figsize=(10, 6))  # Set the size of the plot

        # Plot each category
        for category in category_avg_historical_data.columns:
            plt.plot(category_avg_historical_data.index, category_avg_historical_data[category], label=category)

        plt.title('Average Historical Data by Category')
        plt.xlabel('Date')
        plt.ylabel('Average Value')
        plt.legend()  # Add a legend to distinguish categories
        plt.grid(True)  # Add a grid for better readability
        plt.show()

    def calculate_monthly_returns(self):
        category_avg_historical_data = self.calculate_average_historical_data()

        # Resample to monthly data - taking the last value of each month
        monthly_data = category_avg_historical_data.resample('M').last()

        # Calculate month-over-month percentage change
        monthly_returns = monthly_data.pct_change()

        # Drop the first row which will be NaN
        monthly_returns = monthly_returns.dropna()

        return monthly_returns

    def calculate_adjusted_yearly_returns(self):
        category_avg_historical_data = self.calculate_average_historical_data()

        # Resample to yearly data - taking the last value of each year
        yearly_data = category_avg_historical_data.resample('Y').last()

        # Calculate year-over-year percentage change
        yearly_returns = yearly_data.pct_change()

        dividend_yields = self.calculate_aggregated_data()[2]

        for category in yearly_returns.columns:
            if category in dividend_yields:
                yearly_returns[category] += dividend_yields[category] / 100

        # Drop the first row which will be NaN
        yearly_returns = yearly_returns.dropna()

        return yearly_returns

    def __calculate_downside_risk(self, returns, mar):
        excess_returns = np.minimum(0, returns - mar)
        downside_risk = np.sqrt(np.mean(excess_returns ** 2))
        return downside_risk

    def calculate_downside_risks(self):
        monthly_returns = self.calculate_monthly_returns()
        downside_risks = {}

        annual_MAR = self.risk_free_rate / 100
        monthly_MAR = (1 + annual_MAR) ** (1 / 12) - 1  # Convert annual rate to monthly

        for category in monthly_returns.columns:
            category_returns = monthly_returns[category].dropna()
            downside_risks[category] = self.__calculate_downside_risk(category_returns, monthly_MAR)

        return downside_risks

    def calculate_yearly_downside_risks(self):
        yearly_returns = self.calculate_adjusted_yearly_returns()
        downside_risks = {}

        annual_mar = self.risk_free_rate / 100
        # print(f"Annual MAR: {annual_mar}")

        for category in yearly_returns.columns:
            category_returns = yearly_returns[category].dropna()
            downside_risks[category] = self.__calculate_downside_risk(category_returns, annual_mar)

        return downside_risks

    def calculate_var_monte_carlo(self, base_currency='USD', time_horizon=252, n_simulations=10000,
                                  confidence_level=0.95):
        average_historical_data = self.calculate_average_historical_data()
        if average_historical_data is not None:

            category_averages_return, category_averages_std_dev, _ = self.calculate_aggregated_data()
            var_results = {}

            for category in category_averages_return:
                # Use adjusted geometric mean as the expected return for the category
                mean_return = category_averages_return[category] / 100 / time_horizon

                # Use historical standard deviation for the category
                std_return = category_averages_std_dev[category] / 100 / np.sqrt(time_horizon)

                # Simulate future price paths for the category
                simulated_returns = np.random.normal(mean_return, std_return, (time_horizon, n_simulations))
                last_price = average_historical_data[category].iloc[-1]
                simulated_prices = last_price * np.cumprod(1 + simulated_returns, axis=0)

                # Calculate the VaR for the category
                var_absolute = np.percentile(simulated_prices[-1], (1 - confidence_level) * 100)
                var_in_local_currency = last_price - var_absolute

                var_results[category] = var_in_local_currency

            return var_results

        else:
            return "Unknown"

    def calculate_correlation_matrix(self):
        avg_historical_data = self.calculate_average_historical_data()
        return avg_historical_data.corr()
