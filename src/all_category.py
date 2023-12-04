import pandas as pd

from categories.category import Category
import numpy as np

from global_settings import CATEGORY_CONSTRAINTS
from fill_nan_dataframe_knn import fill_nan_dataframe_knn
from pypfopt_optimizer.mean_variance_optimizer import MeanVarianceOptimizer
from riskfolio_optimizer.mean_risk_optimizer import MeanRiskOptimizer
from src.categories.sub_categories.securities.security import Security


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

        cleaned_weights, portfolio_metrics = mvo.optimize_max_sharpe_ratio(expected_returns, covariance, risk_free_rate=Security.get_risk_free_rate(), constraints_dict=CATEGORY_CONSTRAINTS)

        # mro = MeanRiskOptimizer()
        # mro.optimize(returns_df, risk_free_rate=0, plot=True)

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

    def optimize_with_subcategory(self):
        returns_df = pd.DataFrame()

        for category in self.categories:
            for subcategory in category.subcategories:
                returns_df[subcategory.name] = subcategory.aggregated_returns

        filled_dataframe = fill_nan_dataframe_knn(returns_df)

        # Round all numbers in the DataFrame to 5 decimal places
        rounded_dataframe = filled_dataframe.round(5)

        mvo = MeanVarianceOptimizer()
        expected_returns = mvo.mean_historical_returns_by_returns(rounded_dataframe)
        covariance, correlation = mvo.covariance_correlation_matrix_by_returns(rounded_dataframe)

        cleaned_weights, portfolio_metrics = mvo.optimize_max_sharpe_ratio(expected_returns, covariance, risk_free_rate=Security.get_risk_free_rate())


        return cleaned_weights

    def assign_final_asset_weights(self):
        for category in self.categories:
            for subcategory in category.subcategories:
                for security in subcategory.securities:
                    final_weight = (security.sub_asset_weight *
                                    subcategory.sub_category_weight *
                                    category.category_weight)
                    security.portfolio_asset_weight = final_weight

    @property
    def category_df(self):
        if self.__category_df is None:
            self.__category_df = self.create_returns_dataframe()
        return self.__category_df