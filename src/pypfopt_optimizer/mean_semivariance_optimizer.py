
from pypfopt import EfficientSemivariance, expected_returns
class MeanSemivarianceOptimizer:
    def __init__(self):
        pass

    def mean_historical_returns(self, prices):
        return expected_returns.mean_historical_return(prices)

    def returns_form_prices(self, prices):
        return expected_returns.returns_from_prices(prices)

    def optimize_max_quadratic_utility(self, expected_returns, returns_df, risk_free_rate=0.02, constraints_dict=None):

        # TODO: Align the expected returns with the returns_df

        es = EfficientSemivariance(expected_returns, returns_df)

        if constraints_dict is not None:
            for key, weight in constraints_dict.items():
                asset, constraint_type = key.split('_')  # Splitting the key into asset name and constraint type
                asset_index = expected_returns.index.get_loc(asset)
                if constraint_type == "max":
                    es.add_constraint(lambda w, idx=asset_index, wgt=weight: w[idx] <= wgt)
                elif constraint_type == "min":
                    es.add_constraint(lambda w, idx=asset_index, wgt=weight: w[idx] >= wgt)

        weights = es.max_quadratic_utility()
        cleaned_weights = es.clean_weights()
        print(cleaned_weights)
        expected_annual_return, semideviation, sortino_ratio = es.portfolio_performance(verbose=True,
                                                                                          risk_free_rate=risk_free_rate)
        print(
            f"Expected Annual Return: {round(expected_annual_return * 100, 2)}% Semideviation: {round(semideviation * 100, 2)}% Sortino Ratio: {round(sortino_ratio, 2)}")
        portfolio_metrics = {
            "Expected Annual Return": expected_annual_return,
            "Semideviation": semideviation,
            "Sortino Ratio": sortino_ratio
        }
        return dict(cleaned_weights), portfolio_metrics
