import numpy as np
import pandas as pd
from forex_python.converter import CurrencyRates
from pypfopt import expected_returns

class AggregatedDataCalculator:
    BASE_CURRENCY = "USD"

    def calculate_weighted_average_historical_data(self, categories_dict):
        category_avg_historical_data = pd.DataFrame()

        for category, securities in categories_dict.items():
            if not securities:
                continue

            converted_data = []
            # Convert to USD and standardize to tz-naive before aggregation
            for sec in securities:
                if sec.traded_currency != AggregatedDataCalculator.BASE_CURRENCY:
                    data_in_usd = self.convert_historical_data_currency(sec.historical_data, sec.traded_currency)
                else:
                    data_in_usd = sec.historical_data
                data_in_usd = data_in_usd.tz_localize(None)
                converted_data.append(data_in_usd * sec.asset_weight)

            if converted_data:
                aggregated_data = pd.concat(converted_data, axis=1)
                category_avg_historical_data[category] = aggregated_data.mean(axis=1)

        resample_category_avg_historical_data = category_avg_historical_data.resample('D').last()
        resample_category_avg_historical_data = resample_category_avg_historical_data.dropna()
        return resample_category_avg_historical_data

    def calculate_average_historical_data(self, categories_dict):
        category_avg_historical_data = pd.DataFrame()

        for category, securities in categories_dict.items():
            if not securities:
                continue

            converted_data = []
            # Convert to USD and standardize to tz-naive before aggregation
            for sec in securities:
                if sec.traded_currency != AggregatedDataCalculator.BASE_CURRENCY:
                    data_in_usd = self.convert_historical_data_currency(sec.historical_data, sec.traded_currency)
                else:
                    data_in_usd = sec.historical_data
                data_in_usd = data_in_usd.tz_localize(None)
                converted_data.append(data_in_usd)

            if converted_data:
                # Aggregate data without applying weights
                aggregated_data = pd.concat(converted_data, axis=1)
                # Calculate the mean, which inherently applies equal weight
                category_avg_historical_data[category] = aggregated_data.mean(axis=1)

        resample_category_avg_historical_data = category_avg_historical_data.resample('D').last()
        resample_category_avg_historical_data = resample_category_avg_historical_data.dropna()
        return resample_category_avg_historical_data

    def convert_historical_data_currency(self, df, traded_currency):
        avg_rate = self.get_average_exchange_rate(df.index[0], df.index[-1], traded_currency)
        return df * avg_rate

    def get_average_exchange_rate(self, start_date, end_date, from_currency):
        currency_converter = CurrencyRates()
        rates = []

        # Ensure the index is a DateTimeIndex
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)

        # Iterate over the date range and collect rates
        date_range = pd.date_range(start=start_date, end=end_date, freq='M')
        for date in date_range:
            try:
                rate = currency_converter.get_rate(from_currency, AggregatedDataCalculator.BASE_CURRENCY, date)
                rates.append(rate)
            except Exception as e:
                print(f"Error on date {date}: {e}")

        # Calculate the average rate
        average_rate = sum(rates) / len(rates) if rates else None
        return average_rate

    def mean_historical_returns(self, prices):
        return expected_returns.mean_historical_return(prices)

    def calculate_weighted_average_adjusted_returns(self, categories_dict, historical_data):
        category_avg_dividend = {}

        for category, securities in categories_dict.items():
            if not securities:
                continue

            dividend_yields = [sec.dividend_yield * sec.asset_weight for sec in securities]
            category_avg_dividend[category] = np.mean(dividend_yields)

        category_avg_dividend_series = pd.Series(category_avg_dividend)
        historical_returns = self.mean_historical_returns(historical_data)

        # Aligning the Series
        aligned_dividends, aligned_returns = category_avg_dividend_series.align(historical_returns, fill_value=0)

        return aligned_dividends + aligned_returns

    def calculate_average_adjusted_returns(self, categories_dict, historical_data):
        category_avg_dividend = {}

        for category, securities in categories_dict.items():
            if not securities:
                continue

            # Equal weighted average: Simply take the dividend yield of each security
            dividend_yields = [sec.dividend_yield for sec in securities]
            category_avg_dividend[category] = np.mean(dividend_yields)

        category_avg_dividend_series = pd.Series(category_avg_dividend)
        historical_returns = self.mean_historical_returns(historical_data)

        # Aligning the Series
        aligned_dividends, aligned_returns = category_avg_dividend_series.align(historical_returns, fill_value=0)

        return aligned_dividends + aligned_returns




