import riskfolio as rp
import matplotlib.pyplot as plt


class MeanRiskOptimizer:

    def __init__(self):
        pass

    def optimize(self, returns_in_series, risk_free_rate=0.02, constraints_dict=None, plot=False):
        returns_in_series.index = returns_in_series.index.tz_localize(None)
        port = rp.Portfolio(returns=returns_in_series)
        port.assets_stats(method_mu='JS', method_cov='oas')
        weight = port.optimization(model='Classic', rm='MV', obj='Sharpe', rf=risk_free_rate)

        if plot:
            rp.excel_report(returns_in_series, weight, rf=risk_free_rate,)
            fig = rp.plot_table(returns_in_series, weight, MAR=risk_free_rate)
            plt.show()