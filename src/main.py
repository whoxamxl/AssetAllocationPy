from category_optimizer.category_optimizer import CategoryOptimizer
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
    print("Category 95% VaR: ", sm.calculate_var_monte_carlo())
    print("Current 3-month Treasury Bill Rate: ", round(sm.risk_free_rate, 2), "%")
    print(sm.calculate_adjusted_yearly_returns())
    print("Category Downside Risks: ", sm.calculate_downside_risks())
    print("Category Yearly Downside Risks: ", sm.calculate_yearly_downside_risks())
    # sm.plot_category_historical_data()



    ew = ExcelWriter(file_path, sm)
    ew.update_excel()
