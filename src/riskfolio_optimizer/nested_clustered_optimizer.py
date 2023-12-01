import riskfolio as rp
import matplotlib
matplotlib.use('TkAgg')  # Example for the TkAgg backend
import matplotlib.pyplot as plt


class NestedClusteredOptimizer:

    def __init__(self):
        pass

    def optimize(self, returns_in_series, risk_free_rate=0.02, constraints_dict=None):
        hcp = rp.HCPortfolio(returns_in_series)
        weight = hcp.optimization(model='HRP', covariance='ledoit', obj='MinRisk', rm='CVaR', rf=risk_free_rate)
        returns_in_series.index = returns_in_series.index.tz_localize(None)
        rp.excel_report(returns_in_series, weight, rf=risk_free_rate,)
        # fig = rp.plot_table(returns_in_series, weight, MAR=risk_free_rate)
        # plt.show()