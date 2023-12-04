import pandas as pd

from src.categories.sub_categories.securities.security import Security
from src.categories.sub_categories.sub_category import SubCategory
from src.fill_nan_dataframe_knn import fill_nan_dataframe_knn
from src.global_settings import SUB_CATEGORY_CONSTRAINTS
from src.pypfopt_optimizer.mean_variance_optimizer import MeanVarianceOptimizer


class Category:
    def __init__(self, name):
        self.name = name
        self.subcategories = []
        self.__sub_category_df = None
        self.__aggregated_returns = None
        self.__category_weight = None

    def add_subcategory(self, subcategory):
        pass

    def find_or_create_subcategory(self, subcategory_name):
        subcategory = next((sc for sc in self.subcategories if sc.name == subcategory_name), None)
        if not subcategory:
            subcategory = SubCategory(subcategory_name)
            self.subcategories.append(subcategory)
        return subcategory

    def add_security_to_subcategory(self, security, subcategory_name):
        subcategory = self.find_or_create_subcategory(subcategory_name)
        subcategory.add_security(security)

    def create_returns_dataframe(self):
        returns_df = pd.DataFrame()

        for subcategory in self.subcategories:
            if subcategory.aggregated_returns is not None:
                returns_df[subcategory.name] = subcategory.aggregated_returns

        filled_dataframe = fill_nan_dataframe_knn(returns_df)

        rounded_dataframe = filled_dataframe.round(5)

        return rounded_dataframe

    def optimize(self):
        returns_df = self.sub_category_df

        mvo = MeanVarianceOptimizer()
        expected_returns = mvo.mean_historical_returns_by_returns(returns_df)
        covariance, correlation = mvo.covariance_correlation_matrix_by_returns(returns_df)

        cleaned_weights, portfolio_metrics = mvo.optimize_max_sharpe_ratio(expected_returns, covariance, risk_free_rate=Security.get_risk_free_rate(), constraints_dict=SUB_CATEGORY_CONSTRAINTS.get(self.name))

        for subcategory in self.subcategories:
            try:
                if subcategory.name not in cleaned_weights:
                    # Raise an error if the subcategory name doesn't match any key in cleaned_weight
                    raise KeyError(f"No matching weight found for subcategory '{subcategory.name}'.")

                weight = cleaned_weights.get(subcategory.name)
                if weight is None:
                    raise ValueError(f"Weight not found for subcategory: {subcategory.name}")

                subcategory.sub_category_weight = weight
            except KeyError as e:
                print(f"KeyError: {e}")
                raise
            except ValueError as e:
                print(f"Error setting weight for {subcategory.name}: {e}")
                raise
            except Exception as e:
                print(f"Unexpected error occurred while setting weight for {subcategory.name}: {e}")
                raise

        return cleaned_weights

    def calculate_aggregated_returns(self):
        self.optimize()
        filled_returns_df = self.sub_category_df

        # Initialize an empty Series to store aggregated returns
        aggregated_returns = pd.Series(index=filled_returns_df.index, dtype=float)

        for subcategory in self.subcategories:
            if subcategory.name in filled_returns_df.columns:
                # Multiply the returns by the security's sub-asset weight
                weighted_returns = filled_returns_df[subcategory.name] * subcategory.sub_category_weight
                # Sum the weighted returns to the aggregated returns
                aggregated_returns = aggregated_returns.add(weighted_returns, fill_value=0)

        return pd.DataFrame({self.name: aggregated_returns})

    @property
    def sub_category_df(self):
        if self.__sub_category_df is None:
            self.__sub_category_df = self.create_returns_dataframe()
        return self.__sub_category_df

    @property
    def aggregated_returns(self):
        if self.__aggregated_returns is None:
            self.__aggregated_returns = self.calculate_aggregated_returns()
        return self.__aggregated_returns

    @property
    def category_weight(self):
        return self.__category_weight
    @category_weight.setter
    def category_weight(self, weight):
        if weight < 0 or weight > 1:
            raise ValueError("Category weight must be between 0 and 1")
        self.__category_weight = weight