from securities.security_type.alternative import Alternative
from securities.security_type.bond import Bond
from securities.security_type.equity import Equity

import pandas as pd


class SecurityManager:
    def __init__(self):
        self.securities = []

    def add_security(self, ticker, type):
        if not self.__security_exists(ticker):
            match type:
                case "Equity":
                    self.securities.append(Equity(ticker))
                case "Bond":
                    self.securities.append(Bond(ticker))
                case "Alternative":
                    self.securities.append(Alternative(ticker))
                case _:
                    print("Unknown type.")
        else:
            print(f"Security with ticker {ticker} already exists.")

    def __security_exists(self, ticker):
        return any(security.ticker == ticker for security in self.securities)

    def remove_security(self, ticker):
        # Remove security with the specified ticker
        self.securities = [security for security in self.securities if security.ticker != ticker]

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

        for security in self.securities:
            # Get the category from the type of the security
            category = type(security).__name__

            # Initialize the lists for the category if not already done
            if category not in category_returns_data:
                category_returns_data[category] = []
                category_std_dev_data[category] = []

            # Append the data for this security to the relevant category
            category_returns_data[category].append(security.adjusted_geometric_mean_5y)
            category_std_dev_data[category].append(security.std_5y)

        # Initialize new dictionaries for calculated averages
        category_averages_return = {}
        category_averages_std_dev = {}

        # Calculate averages for returns and standard deviations for each category
        for category in category_returns_data:
            category_averages_return[category] = sum(category_returns_data[category]) / len(
                category_returns_data[category]) if category_returns_data[category] else 0
            category_averages_std_dev[category] = sum(category_std_dev_data[category]) / len(
                category_std_dev_data[category]) if category_std_dev_data[category] else 0

        return category_averages_return, category_averages_std_dev

    def calculate_average_historical_data(self):
        category_avg_historical_data = pd.DataFrame()

        for category in set(type(security).__name__ for security in self.securities):
            category_securities = [sec for sec in self.securities if type(sec).__name__ == category]
            if not category_securities:
                continue

            # Standardize to tz-naive before aggregation
            aggregated_data = pd.concat([sec.historical_data.tz_localize(None) for sec in category_securities], axis=1)
            category_avg_historical_data[category] = aggregated_data.mean(axis=1)

        return category_avg_historical_data

    def calculate_correlation_matrix(self):
        avg_historical_data = self.calculate_average_historical_data()
        return avg_historical_data.corr()
