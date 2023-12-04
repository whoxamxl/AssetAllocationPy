import pandas as pd

from src.categories.sub_categories.securities.security import Security
from src.fill_nan_dataframe_knn import fill_nan_dataframe_knn


class SubCategory:
    def __init__(self, name):
        self.name = name
        self.securities = []
        self.__aggregated_returns = None
        self.__sub_category_weight = None

    def add_security(self, security):
        if isinstance(security, Security):
            self.securities.append(security)
        else:
            raise TypeError("Only Security instances can be added")

    def calculate_asset_weights(self):
        total_inverse_risk = sum(
            1 / security.standard_deviation_5y for security in self.securities if security.standard_deviation_5y > 0)

        if total_inverse_risk == 0:
            raise ValueError("Total inverse risk is zero. Cannot calculate asset weights.")

        for security in self.securities:
            if security.standard_deviation_5y > 0:
                inverse_risk = 1 / security.standard_deviation_5y
                security.sub_asset_weight = inverse_risk / total_inverse_risk
            else:
                security.sub_asset_weight = 0  # Handle securities with zero standard deviation if necessary

    def create_returns_dataframe(self):
        returns_df = pd.DataFrame()

        for security in self.securities:
            if security.adjusted_returns_in_series_5y is not None:
                returns_df[security.ticker] = security.adjusted_returns_in_series_5y

        filled_dataframe = fill_nan_dataframe_knn(returns_df)

        # Round all numbers in the DataFrame to 5 decimal places
        rounded_dataframe = filled_dataframe.round(5)

        return rounded_dataframe

    # TODO: sub_asset_weight -> sub_risk_weight
    def calculate_aggregated_returns(self):
        filled_returns_df = self.create_returns_dataframe()

        # Initialize an empty Series to store aggregated returns
        aggregated_returns = pd.Series(index=filled_returns_df.index, dtype=float)

        for security in self.securities:
            if security.ticker in filled_returns_df.columns:
                # Multiply the returns by the security's sub-asset weight
                weighted_returns = filled_returns_df[security.ticker] * security.sub_asset_weight
                # Sum the weighted returns to the aggregated returns
                aggregated_returns = aggregated_returns.add(weighted_returns, fill_value=0)

        # Return the aggregated returns as a DataFrame with the sub-category name as the column name
        return pd.DataFrame({self.name: aggregated_returns})

    @property
    def aggregated_returns(self):
        if self.__aggregated_returns is None:
            self.__aggregated_returns = self.calculate_aggregated_returns()
        return self.__aggregated_returns

    @property
    def sub_category_weight(self):
        return self.__sub_category_weight

    @sub_category_weight.setter
    def sub_category_weight(self, weight):
        if weight < 0 or weight > 1:
            raise ValueError("Sub-category weight must be between 0 and 1")
        self.__sub_category_weight = weight