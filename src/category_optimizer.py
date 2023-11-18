import numpy as np
from scipy.optimize import minimize

class CategoryOptimizer:
    def __init__(self, security_manager):
        self.security_manager = security_manager

    def __convert_to_numpy_array(self):
        category_averages_return, category_averages_std_dev = self.security_manager.calculate_aggregated_data()

        # Ensure the order of categories is consistent
        categories = category_averages_return.keys()

        # Convert to numpy arrays
        expected_returns = np.array([category_averages_return[cat] for cat in categories])
        std_devs = np.array([category_averages_std_dev[cat] for cat in categories])

        correlation_matrix_df = self.security_manager.calculate_correlation_matrix()
        correlation_matrix = correlation_matrix_df.values  # Convert to numpy array

        return categories, expected_returns, std_devs, correlation_matrix

    def __convert_to_decimal(self, percentage_rate):
        return percentage_rate / 100

    def optimize_sharp_ratio(self, risk_free_rate=0.04):
        # Generate random portfolios and their returns and volatilities
        weights, returns, volatilities = self.generate_portfolios()

        # Adjust returns for risk-free rate
        adjusted_returns = returns - risk_free_rate

        # Calculate Sharpe Ratios for each portfolio
        sharpe_ratios = adjusted_returns / volatilities

        # Find the portfolio with the highest Sharpe Ratio
        index_max_sharpe = np.argmax(sharpe_ratios)
        optimal_weights = weights[index_max_sharpe]

        # Map optimal weights to category names
        category_names, _, _, _ = self.__convert_to_numpy_array()
        optimal_weights_dict = dict(zip(category_names, optimal_weights))

        # Optional: Calculate and return expected return and volatility for the optimal portfolio
        optimal_return = returns[index_max_sharpe]
        optimal_volatility = volatilities[index_max_sharpe]

        print("Optimal Weights (Sharp Ratio):", optimal_weights_dict)

        return optimal_weights_dict, optimal_return, optimal_volatility

    def optimize_geometric_mean(self):
        # Generate random portfolios and calculate their geometric mean returns
        weights, geometric_returns = self.generate_portfolios_geometric_mean()

        # Find the portfolio with the highest geometric mean return
        index_max_return = np.argmax(geometric_returns)
        optimal_weights = weights[index_max_return]

        # Map optimal weights to category names
        category_names, _, _, _ = self.__convert_to_numpy_array()
        optimal_weights_dict = dict(zip(category_names, optimal_weights))

        # Return the optimal weights along with the highest geometric mean return
        optimal_return = geometric_returns[index_max_return]
        print("Optimal Weights (Geometric Mean):", optimal_weights_dict)

        return optimal_weights_dict, optimal_return


    def generate_portfolios(self, num_portfolios=10000):
        category_names, expected_returns, std_devs, correlation_matrix = self.__convert_to_numpy_array()
        expected_returns = self.__convert_to_decimal(expected_returns)
        cov_matrix = np.outer(std_devs, std_devs) * correlation_matrix

        portfolio_weights = []
        portfolio_returns = []
        portfolio_volatilities = []

        for _ in range(num_portfolios):
            weights = np.random.random(len(category_names))
            weights /= np.sum(weights)
            portfolio_weights.append(weights)

            portfolio_return = np.dot(weights, expected_returns)
            portfolio_volatility = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))

            portfolio_returns.append(portfolio_return)
            portfolio_volatilities.append(portfolio_volatility)

        return np.array(portfolio_weights), np.array(portfolio_returns), np.array(portfolio_volatilities)

    def generate_portfolios_geometric_mean(self, num_portfolios=10000):
        category_names, expected_returns, std_devs, correlation_matrix = self.__convert_to_numpy_array()
        expected_returns = self.__convert_to_decimal(expected_returns)
        portfolio_weights = []
        portfolio_geometric_returns = []

        for _ in range(num_portfolios):
            weights = np.random.random(len(category_names))
            weights /= np.sum(weights)
            portfolio_weights.append(weights)

            geometric_return = self.calculate_geometric_mean_return(weights, expected_returns)
            portfolio_geometric_returns.append(geometric_return)

        return np.array(portfolio_weights), np.array(portfolio_geometric_returns)

    @staticmethod
    def calculate_geometric_mean_return(weights, returns):
        # Calculating the weighted product of returns
        weighted_returns = 1 + np.dot(weights, returns)
        return weighted_returns ** (1 / len(weights)) - 1


