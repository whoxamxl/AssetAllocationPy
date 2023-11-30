from matplotlib import pyplot as plt
from category_security_manager import CategorySecurityManager
from excel.excel_reader import ExcelReader
from excel.excel_writer import ExcelWriter
from pypfopt_optimizer.mean_variance_optimizer import MeanVarianceOptimizer
from riskfolio_optimizer.nested_clustered_optimizer import NestedClusteredOptimizer
from security_manager import SecurityManager
from aggregated_data_calculator import AggregatedDataCalculator
import pandas as pd

if __name__ == '__main__':
    sm = SecurityManager()
    file_path = "ETF.xlsx"
    er = ExcelReader(file_path, sm)
    er.read_and_update_securities()
    sm.print_securities()
    sm.group_securities()
    sm.print_grouped_securities()

    optimizer = MeanVarianceOptimizer()

    # TODO: check with foreign security and with asset weight (Form: 0.11)
    # TODO: pypfopt_optimizer constraints
    adc = AggregatedDataCalculator()
    csm = CategorySecurityManager()
    for category in sm.grouped_securities:
        avg_data = adc.calculate_average_historical_data(sm.grouped_securities[category])
        adjsuted_returns = adc.calculate_average_adjusted_returns(sm.grouped_securities[category], avg_data)
        cov_matrix, cor_matrix = optimizer.covariance_correlation_matrix(avg_data)
        weight_dict, metrics_dict = optimizer.optimize_max_sharpe_ratio(adjsuted_returns, cov_matrix, risk_free_rate=sm.risk_free_rate)

        csm.add_category_security(category, weight_dict, avg_data, metrics_dict)

    for category_security in csm.category_securities:
        category_security.print_category_security()

    # avg_data = adc.calculate_average_historical_data(sm.grouped_securities["Alternative"])
    # print(avg_data)
    # print(adc.mean_historical_returns(avg_data))
    # adjusted_returns_alternative = adc.calculate_average_adjusted_returns(sm.grouped_securities["Alternative"], avg_data)
    # print(adjusted_returns_alternative)
    # cov_matrix_alternative, cor_matrix_alternative = pypfopt_optimizer.covariance_correlation_matrix(avg_data)
    # print(cor_matrix_alternative)
    # weight_dict, metrics_dict = pypfopt_optimizer.optimize_max_sharpe_ratio(adjusted_returns_alternative, cov_matrix_alternative, risk_free_rate=sm.risk_free_rate)
    # print(weight_dict)

    all_historical_data, all_returns = csm.group_aggregated_data()
    # print(all_historical_data.to_string())
    # print(all_returns)
    all_cov_matrix, all_cor_matrix = optimizer.covariance_correlation_matrix(all_historical_data)
    all_weight_dict, all_metrics_dict = optimizer.optimize_max_sharpe_ratio(all_returns, all_cov_matrix, risk_free_rate=0, constraints_dict={"Alternative_max": 0.2})

    def plot_category_historical_data(self, historical_data):
        plt.figure(figsize=(10, 6))  # Set the size of the plot

        # Plot each category
        for category in historical_data.columns:
            plt.plot(historical_data.index, historical_data[category], label=category)

        plt.title('Average Historical Data by Category')
        plt.xlabel('Date')
        plt.ylabel('Average Value')
        plt.legend()  # Add a legend to distinguish categories
        plt.grid(True)  # Add a grid for better readability
        plt.show()

    # print(sm.aggregate_returns_in_series())
    print(sm.aggregate_monthly_returns_in_series().to_string())

    nco = NestedClusteredOptimizer()
    nco.optimize(sm.aggregate_monthly_returns_in_series(), risk_free_rate=0)



    ew = ExcelWriter(file_path, sm)
    ew.update_excel()
