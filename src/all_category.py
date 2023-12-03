import pandas as pd

from categories.category import Category
from categories.sub_categories.securities.security import Security
import numpy as np

from constraints import CATEGORY_CONSTRAINTS
from fill_nan_dataframe_knn import fill_nan_dataframe_knn
from pypfopt_optimizer.mean_variance_optimizer import MeanVarianceOptimizer


class AllCategory:
    def __init__(self):
        self.categories = []
        self.__category_df = None

    def find_or_create_category(self, category_name):
        category = next((cat for cat in self.categories if cat.name == category_name), None)
        if not category:
            category = Category(category_name)
            self.categories.append(category)
        return category

    def add_security(self, security):
        category = self.find_or_create_category(type(security).__name__)
        subcategory = category.find_or_create_subcategory(security.sub_category)
        subcategory.add_security(security)

    def add_securities(self, securities):
        for ticker, subcategory_name, category_name, sub_category_weight in securities:
            category = self.find_or_create_category(category_name)
            subcategory = category.find_or_create_subcategory(subcategory_name)
            category.add_security_to_subcategory(Security(ticker, subcategory_name, sub_category_weight),
                                                 subcategory_name)

    def remove_securities(self, tickers_to_remove):
        pass

    def check_subcategory_weights(self):
        for category in self.categories:
            for subcategory in category.subcategories:
                total_weight = sum(security.sub_risk_weight for security in subcategory.securities if
                                   security.sub_risk_weight is not None)

                # Check if the total weight is approximately 1 (100%)
                if not np.isclose(total_weight, 1, atol=0.01):
                    raise ValueError(
                        f"Total weight in sub-category '{subcategory.name}' of category '{category.name}' is not 1 (100%). It's {total_weight * 100:.2f}%.")

        return True  # Only returns True if all checks pass

    def assign_asset_weights_to_subcategories(self):
        for category in self.categories:
            for subcategory in category.subcategories:
                subcategory.calculate_asset_weights()

    def print_security_weight_details(self):
        for category in self.categories:
            print(f"Category: {category.name}")
            for subcategory in category.subcategories:
                print(f"  Sub-Category: {subcategory.name}")
                for security in subcategory.securities:
                    ticker = security.ticker
                    risk_weight = security.sub_risk_weight  # assuming this is an attribute in Security
                    asset_weight = security.sub_asset_weight  # assuming this is an attribute in Security
                    print(f"    Security: {ticker}, Risk Weight: {risk_weight}, Asset Weight: {asset_weight}")

    def print_sub_category_returns_in_series(self):
        for category in self.categories:
            print(f"Category: {category.name}")
            for subcategory in category.subcategories:
                print(f"  Sub-Category: {subcategory.name}")
                print(subcategory.create_returns_dataframe().to_string())

    def print_sub_category_aggregated_returns_in_series(self):
        for category in self.categories:
            print(f"Category: {category.name}")
            for subcategory in category.subcategories:
                print(f"  Sub-Category: {subcategory.name}")
                print(subcategory.calculate_aggregated_returns().to_string())

    def print_sub_category_aggregated_returns_in_dataframe(self):
        for category in self.categories:
            print(f"Category: {category.name}")
            print(category.create_returns_dataframe().to_string())

    def optimize_sub_category(self):
        for category in self.categories:
            print(f"Category: {category.name}")
            category.optimize()

    def create_returns_dataframe(self):
        returns_df = pd.DataFrame()

        for category in self.categories:
            if category.aggregated_returns is not None:
                returns_df[category.name] = category.aggregated_returns

        filled_dataframe = fill_nan_dataframe_knn(returns_df)

        rounded_dataframe = filled_dataframe.round(5)

        return rounded_dataframe

    def optimize(self):
        returns_df = self.category_df

        mvo = MeanVarianceOptimizer()
        expected_returns = mvo.mean_historical_returns_by_returns(returns_df)
        covariance, correlation = mvo.covariance_correlation_matrix_by_returns(returns_df)

        cleaned_weights, portfolio_metrics = mvo.optimize_max_sharpe_ratio(expected_returns, covariance, constraints_dict=CATEGORY_CONSTRAINTS)

        for category in self.categories:
            try:
                if category.name not in cleaned_weights:
                    # Raise an error if the category name doesn't match any key in cleaned_weight
                    raise KeyError(f"No matching weight found for category '{category.name}'.")

                weight = cleaned_weights.get(category.name)
                if weight is None:
                    raise ValueError(f"Weight not found for category: {category.name}")

                category.category_weight = weight
            except KeyError as e:
                print(f"KeyError: {e}")
                raise
            except ValueError as e:
                print(f"Error setting weight for {category.name}: {e}")
                raise
            except Exception as e:
                print(f"Unexpected error occurred while setting weight for {category.name}: {e}")
                raise

        return cleaned_weights

    @property
    def category_df(self):
        if self.__category_df is None:
            self.__category_df = self.create_returns_dataframe()
        return self.__category_df