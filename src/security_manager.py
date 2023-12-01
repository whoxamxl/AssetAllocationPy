from securities.security_type.alternative import Alternative
from securities.security_type.bond import Bond
from securities.security_type.equity import Equity

import pandas as pd
import numpy as np
import yahooquery as yq
import matplotlib.pyplot as plt
from sklearn.impute import KNNImputer


class SecurityManager:
    def __init__(self):
        self.securities = []
        self.grouped_securities = {}

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
    def group_securities(self):
        grouped = {}
        for security in self.securities:
            category = type(security).__name__
            sub_category = security.sub_category

            if category not in grouped:
                grouped[category] = {}
            if sub_category not in grouped[category]:
                grouped[category][sub_category] = []
            grouped[category][sub_category].append(security)

        self.grouped_securities = grouped

    def print_grouped_securities(self):
        formatted_output = {}
        for category, sub_categories in self.grouped_securities.items():
            formatted_output[category] = {}
            for sub_category, securities in sub_categories.items():
                formatted_output[category][sub_category] = [security.ticker for security in securities]
        print(formatted_output)


    def aggregate_returns_in_series(self):
        aggregated_returns = pd.DataFrame()
        for security in self.securities:
            aggregated_returns[security.ticker] = security.adjusted_returns_in_series_5y

        filled_returns = self.fill_missing_dataframe_knn(aggregated_returns)


        return filled_returns

    def fill_missing_dataframe_knn(self, returns_dataframe):
        # Identify columns that are entirely NaN
        nan_columns = returns_dataframe.columns[returns_dataframe.isnull().all()].tolist()

        # Check if there are any such columns and raise an error with their names
        if nan_columns:
            raise ValueError(f"Columns entirely NaN: {', '.join(nan_columns)}")

        # Initialize the KNN Imputer
        imputer = KNNImputer(n_neighbors=5)

        # Impute the missing values
        returns_filled = imputer.fit_transform(returns_dataframe)

        # Convert the filled array back to a DataFrame
        returns_filled_df = pd.DataFrame(returns_filled, columns=returns_dataframe.columns,
                                         index=returns_dataframe.index)

        return returns_filled_df
