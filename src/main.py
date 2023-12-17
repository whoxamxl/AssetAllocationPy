from matplotlib import pyplot as plt

from all_category import AllCategory
from excel.excel_reader import ExcelReader
from excel.excel_writer import ExcelWriter
from pypfopt_optimizer.mean_variance_optimizer import MeanVarianceOptimizer
from categories.sub_categories.securities.security import Security


def plot_category_historical_data(historical_data):
    plt.figure(figsize=(10, 6))  # Set the size of the plot

    # Plot each categories
    for category in historical_data.columns:
        plt.plot(historical_data.index, historical_data[category], label=category)

    plt.title('Average Historical Data by Category')
    plt.xlabel('Date')
    plt.ylabel('Average Value')
    plt.legend()  # Add a legend to distinguish categories
    plt.grid(True)  # Add a grid for better readability
    plt.show()

def plot_returns(returns_filled_df):
    # Number of tickers
    num_tickers = len(returns_filled_df.columns)

    # Create a figure and a set of subplots
    fig, axs = plt.subplots(num_tickers, 1, figsize=(15, 5 * num_tickers))

    # Check if there's only one subplot (in case of a single ticker)
    if num_tickers == 1:
        axs = [axs]

    # Plot each ticker in a separate subplot
    for i, ticker in enumerate(returns_filled_df.columns):
        axs[i].plot(returns_filled_df.index, returns_filled_df[ticker])
        axs[i].set_title(f'Returns of {ticker}')
        axs[i].set_xlabel('Date')
        axs[i].set_ylabel('Returns')

    # Adjust layout to prevent overlapping
    plt.tight_layout()

    # Show the plot
    plt.show()

if __name__ == '__main__':
    # sm = SecurityManager()
    ac = AllCategory()
    file_path = "ETF.xlsx"
    er = ExcelReader(file_path, ac)
    er.read_and_update_securities()
    # Check sub-category weights

    # ac.print_security_weight_details()
    # ac.print_sub_category_returns_in_series()
    # ac.print_sub_category_aggregated_returns_in_series()
    # ac.print_sub_category_aggregated_returns_in_dataframe()
    # ac.optimize_sub_category()
    ac.print_security_average_dividend_yield()
    ac.optimize()



    # optimizer = MeanVarianceOptimizer()

    print(f"Risk Free Rate: {Security.get_risk_free_rate() * 100}%")

    ac.assign_final_asset_weights()

    # adc = AggregatedDataCalculator()
    # csm = CategorySecurityManager()
    # for categories in sm.grouped_securities:
    #     avg_data = adc.calculate_average_historical_data(sm.grouped_securities[categories])
    #     adjsuted_returns = adc.calculate_average_adjusted_returns(sm.grouped_securities[categories], avg_data)
    #     cov_matrix, cor_matrix = optimizer.covariance_correlation_matrix(avg_data)
    #     weight_dict, metrics_dict = optimizer.optimize_max_sharpe_ratio(adjsuted_returns, cov_matrix, risk_free_rate=0)
    #
    #     csm.add_category_security(categories, weight_dict, avg_data, metrics_dict)
    #
    # for category_security in csm.category_securities:
    #     category_security.print_category_security()

    # avg_data = adc.calculate_average_historical_data(sm.grouped_securities["Alternative"])
    # print(avg_data)
    # print(adc.mean_historical_returns(avg_data))
    # adjusted_returns_alternative = adc.calculate_average_adjusted_returns(sm.grouped_securities["Alternative"], avg_data)
    # print(adjusted_returns_alternative)
    # cov_matrix_alternative, cor_matrix_alternative = pypfopt_optimizer.covariance_correlation_matrix(avg_data)
    # print(cor_matrix_alternative)
    # weight_dict, metrics_dict = pypfopt_optimizer.optimize_max_sharpe_ratio(adjusted_returns_alternative, cov_matrix_alternative, risk_free_rate=sm.risk_free_rate)
    # print(weight_dict)

    # all_historical_data, all_returns = csm.group_aggregated_data()
    # print(all_historical_data.to_string())
    # print(all_returns)
    # all_cov_matrix, all_cor_matrix = optimizer.covariance_correlation_matrix(all_historical_data)
    # all_weight_dict, all_metrics_dict = optimizer.optimize_max_sharpe_ratio(all_returns, all_cov_matrix, risk_free_rate=0, constraints_dict={"Alternative_max": 0.2})


    # print(sm.aggregate_returns_in_series())
    # print(sm.aggregate_returns_in_series().to_string())
    # returns_filled_df = sm.aggregate_returns_in_series()
    # nco = NestedClusteredOptimizer()
    # nco.optimize(sm.aggregate_returns_in_series(), risk_free_rate=0)
    # plot_returns(sm.aggregate_returns_in_series())


    ew = ExcelWriter(file_path, ac)
    ew.update_excel()

