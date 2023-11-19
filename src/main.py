import math

from category_optimizer import CategoryOptimizer
from excel.excel_reader import ExcelReader
from excel.excel_writer import ExcelWriter
from security_manager import SecurityManager

if __name__ == '__main__':
    sm = SecurityManager()
    file_path = "ETF.xlsx"
    er = ExcelReader(file_path, sm)
    er.read_and_update_securities()
    sm.print_securities()
    print(sm.calculate_aggregated_data())
    print(sm.calculate_correlation_matrix())
    print(sm.calculate_average_historical_data())
    print("Category VaR: ", sm.calculate_var_monte_carlo())
    optimizer = CategoryOptimizer(sm)
    print("Current 1-Year Treasury Bill Rate: ", round(optimizer.risk_free_rate, 2), "%")
    optimal_weights_sharpe, _, _ = optimizer.optimize_sharp_ratio()
    optimal_weights_geom_mean, _ = optimizer.optimize_geometric_mean()


    intermediate_arithmetic_weights = {category: (optimal_weights_sharpe[category] + optimal_weights_geom_mean[category]) / 2
                            for category in optimal_weights_sharpe}
    print("Optimal Weights (Balanced Arithmetic):", intermediate_arithmetic_weights)


    ew = ExcelWriter(file_path, sm)
    ew.update_excel()
