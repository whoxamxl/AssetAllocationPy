import pandas as pd
from pypfopt import EfficientFrontier, risk_models, expected_returns
class Optimizer:
    def __init__(self):
        pass

    def mean_historical_returns(self, prices):
        return expected_returns.mean_historical_return(prices)

    def covariance_correlation_matrix(self, prices):
        covariance = risk_models.risk_matrix(prices, method='ledoit_wolf')
        correlation = risk_models.cov_to_corr(covariance)

        return covariance, correlation

    # constraints = {
    #     "AAPL_max": 0.10,
    #     "GOOG_min": 0.05
    # }
    def optimize_max_sharp_ratio(self, expected_returns_series, covariance_matrix, risk_free_rate=0.02,
                                 constraints_dict=None):
        # Verifying alignment
        asset_order = covariance_matrix.columns.tolist()
        expected_returns_series = expected_returns_series.reindex(asset_order)

        ef = EfficientFrontier(expected_returns_series, covariance_matrix)

        if constraints_dict is not None:
            for key, weight in constraints_dict.items():
                asset, constraint_type = key.split('_')  # Splitting the key into asset name and constraint type
                asset_index = expected_returns_series.index.get_loc(asset)
                if constraint_type == "max":
                    ef.add_constraint(lambda w, idx=asset_index, wgt=weight: w[idx] <= wgt)
                elif constraint_type == "min":
                    ef.add_constraint(lambda w, idx=asset_index, wgt=weight: w[idx] >= wgt)

        weights = ef.max_sharpe(risk_free_rate=risk_free_rate)
        cleaned_weights = ef.clean_weights()
        print(cleaned_weights)
        expected_annual_return, annual_volatility, sharp_ratio = ef.portfolio_performance(verbose=True,
                                                                                          risk_free_rate=risk_free_rate)
        print(
            f"Expected Annual Return: {round(expected_annual_return * 100, 2)}% Annual Volatility: {round(annual_volatility * 100, 2)}% Sharp Ratio: {round(sharp_ratio, 2)}")
        portfolio_metrics = {
            "Expected Annual Return": expected_annual_return,
            "Annual Volatility": annual_volatility,
            "Sharp Ratio": sharp_ratio
        }
        return dict(cleaned_weights), portfolio_metrics



