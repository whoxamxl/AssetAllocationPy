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

    def __fetch_risk_free_rate(self):
        try:
            treasury = yq.Ticker(self.TBILL_3MONTHS)
            data = treasury.history(period='1y')

            if not data.empty and 'close' in data.columns:
                return round(data['close'].iloc[-1] / 100, 2)
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
                f"Std 5y from yahooquery: {security.std_5y} Std 5t from historical data: {security.std_5y_from_historical_data} Dividend: {security.dividend_yield} VaR 95% in USD: {security.var_95_USD} Traded Currency: {security.traded_currency}")

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
            aggregated_returns[security.ticker] = security.returns_in_series_5y

        interpolated_returns = aggregated_returns.interpolate()
        filled_returns = interpolated_returns.apply(lambda x: x.fillna(x.mean()), axis=0)

        return filled_returns

    def aggregate_monthly_returns_in_series(self):
        aggregated_returns = pd.DataFrame()
        for security in self.securities:
            aggregated_returns[security.ticker] = security.monthly_returns_in_series_5y

        interpolated_returns = aggregated_returns.interpolate()
        filled_returns = interpolated_returns.apply(lambda x: x.fillna(x.mean()), axis=0)

        return filled_returns