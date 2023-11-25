from matplotlib import pyplot as plt

from category_optimizer.optimizer.sharp_ratio_optimizer import SharpRatioOptimizer
from category_optimizer.optimizer.sortino_ratio_optimizer import SortinoRatioOptimizer
from category_optimizer.pypfopt_optimizer import Optimizer
from category_security_manager import CategorySecurityManager
from excel.excel_reader import ExcelReader
from excel.excel_writer import ExcelWriter
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
    print(sm.calculate_aggregated_data())
    print(sm.calculate_correlation_matrix())
    print(sm.calculate_average_historical_data())
    print("Category 95% VaR: ", sm.calculate_var_monte_carlo())
    print("Current 3-month Treasury Bill Rate: ", round(sm.risk_free_rate, 2), "%")
    print(sm.calculate_adjusted_yearly_returns())
    print("Category Downside Risks: ", sm.calculate_downside_risks())
    print("Category Yearly Downside Risks: ", sm.calculate_yearly_downside_risks())
    # sm.plot_category_historical_data()
    sortino_optimizer = SortinoRatioOptimizer(sm)
    sortino_optimizer.optimize_sortino_ratio(0)
    sharp_optimizer = SharpRatioOptimizer(sm)
    sharp_optimizer.optimize_sharp_ratio()

    print("-----------------------------")

    category_returns_dict, _, category_dividend_dict = sm.calculate_aggregated_data()
    category_historical_data = sm.calculate_average_historical_data()
    category_returns = pd.Series(category_returns_dict)
    category_dividend = pd.Series(category_dividend_dict)
    category_returns = category_returns
    category_dividend = category_dividend
    yearly_prices = category_historical_data.resample('Y').last()
    yearly_returns = yearly_prices.pct_change().dropna()
    std = round(yearly_returns.std() * 100, 2)
    print("Category 5y Std: ", std)
    optimizer = Optimizer()
    category_optimizer_returns = optimizer.mean_historical_returns(category_historical_data)
    total_returns = category_optimizer_returns.add(category_dividend, fill_value=0)
    print(total_returns)
    cov_matrix_total, cor_matrix_total = optimizer.covariance_correlation_matrix(category_historical_data)
    print(cor_matrix_total)

    optimizer.optimize_max_sharp_ratio(total_returns, cov_matrix_total, risk_free_rate=sm.risk_free_rate)

    # TODO: check with foreign security and with asset weight (Form: 0.11)
    # TODO: optimizer constraints
    adc = AggregatedDataCalculator()
    csm = CategorySecurityManager()
    for category in sm.grouped_securities:
        avg_data = adc.calculate_average_historical_data(sm.grouped_securities[category])
        adjsuted_returns = adc.calculate_average_adjusted_returns(sm.grouped_securities[category], avg_data)
        cov_matrix, cor_matrix = optimizer.covariance_correlation_matrix(avg_data)
        weight_dict, metrics_dict = optimizer.optimize_max_sharp_ratio(adjsuted_returns, cov_matrix, risk_free_rate=sm.risk_free_rate)

        csm.add_category_security(category, weight_dict, avg_data, metrics_dict)

    for category_security in csm.category_securities:
        category_security.print_category_security()

    # avg_data = adc.calculate_average_historical_data(sm.grouped_securities["Alternative"])
    # print(avg_data)
    # print(adc.mean_historical_returns(avg_data))
    # adjusted_returns_alternative = adc.calculate_average_adjusted_returns(sm.grouped_securities["Alternative"], avg_data)
    # print(adjusted_returns_alternative)
    # cov_matrix_alternative, cor_matrix_alternative = optimizer.covariance_correlation_matrix(avg_data)
    # print(cor_matrix_alternative)
    # weight_dict, metrics_dict = optimizer.optimize_max_sharp_ratio(adjusted_returns_alternative, cov_matrix_alternative, risk_free_rate=sm.risk_free_rate)
    # print(weight_dict)

    all_historical_data, all_returns = csm.group_aggregated_data()
    # print(all_historical_data.to_string())
    # print(all_returns)
    all_cov_matrix, all_cor_matrix = optimizer.covariance_correlation_matrix(all_historical_data)
    all_weight_dict, all_metrics_dict = optimizer.optimize_max_sharp_ratio(all_returns, all_cov_matrix, risk_free_rate=sm.risk_free_rate, constraints_dict={})

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




    ew = ExcelWriter(file_path, sm)
    ew.update_excel()
