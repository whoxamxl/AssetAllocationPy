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

    def optimize_max_sharp_ratio(self, expected_returns_series, covariance_matrix, risk_free_rate=0.02, constraints_dict=None):
        # verifying alignment
        asset_order = covariance_matrix.columns.tolist()
        expected_returns_series = expected_returns_series.reindex(asset_order)

        ef = EfficientFrontier(expected_returns_series, covariance_matrix)
        if constraints_dict is not None:
            for asset, weight in constraints_dict.items():
                asset_index = expected_returns_series.index.get_loc(asset)
                if "max" in asset:
                    ef.add_constraint(lambda w, idx=asset_index, wgt=weight: w[idx] <= wgt)
                elif "min" in asset:
                    ef.add_constraint(lambda w, idx=asset_index, wgt=weight: w[idx] >= wgt)
        weights = ef.max_sharpe(risk_free_rate=risk_free_rate)
        cleaned_weights = ef.clean_weights()
        print(cleaned_weights)
        ef.portfolio_performance(verbose=True, risk_free_rate=risk_free_rate)
        return cleaned_weights

