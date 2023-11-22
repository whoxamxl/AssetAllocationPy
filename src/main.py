

from category_optimizer.optimizer.sharp_ratio_optimizer import SharpRatioOptimizer
from category_optimizer.optimizer.sortino_ratio_optimizer import SortinoRatioOptimizer
from category_optimizer.pypfopt_optimizer import Optimizer
from excel.excel_reader import ExcelReader
from excel.excel_writer import ExcelWriter
from security_manager import SecurityManager
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
    category_returns = category_returns / 100
    category_dividend = category_dividend / 100
    yearly_prices = category_historical_data.resample('Y').last()
    yearly_returns = yearly_prices.pct_change().dropna()
    std = round(yearly_returns.std() * 100, 2)
    print("Category 5y Std: ", std)
    optimizer = Optimizer()
    category_optimizer_returns = optimizer.mean_historical_returns(category_historical_data)
    total_returns = category_optimizer_returns.add(category_dividend, fill_value=0)
    print(total_returns)
    cov_matrix, cor_matrix = optimizer.covariance_correlation_matrix(category_historical_data)
    print(cor_matrix)

    optimizer.optimize_max_sharp_ratio(total_returns, cov_matrix, risk_free_rate=sm.risk_free_rate / 100)





    ew = ExcelWriter(file_path, sm)
    ew.update_excel()
