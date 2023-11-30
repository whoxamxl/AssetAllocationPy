import riskfolio as rp
import matplotlib.pyplot as plt


class NestedClusteredOptimizer:

    def __init__(self):
        pass

    def optimize(self, returns_in_series, risk_free_rate=0.02, constraints_dict=None):
        hcp = rp.HCPortfolio(returns_in_series)
        weight = hcp.optimization(model='NCO', covariance='hist', obj='Sharp', rm='MV', rf=risk_free_rate, l=2)

        rp.excel_report(returns_in_series, weight, rf=risk_free_rate,)
