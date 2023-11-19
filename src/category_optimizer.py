import numpy as np
import yahooquery as yq


class CategoryOptimizer:

    TBILL_3MONTHS = "^IRX"
    def __init__(self, security_manager):
        self.security_manager = security_manager
        self.risk_free_rate = self.__fetch_risk_free_rate()


    def __fetch_risk_free_rate(self):
        try:
            treasury = yq.Ticker(self.TBILL_3MONTHS)
            data = treasury.history(period='1y')

            if not data.empty and 'close' in data.columns:
                return data['close'].iloc[-1]
            else:
                raise ValueError("Data not available or invalid format")
        except Exception as e:
            print(f"Error fetching risk-free rate: {e}")
            return None  # Or handle as appropriate for your application


    def __convert_to_numpy_array(self):
        category_averages_return, category_averages_std_dev = self.security_manager.calculate_aggregated_data()
        category_vars = self.security_manager.calculate_var_monte_carlo()

        # Ensure the order of categories is consistent
        categories = category_averages_return.keys()

        # Convert to numpy arrays
        expected_returns = np.array([category_averages_return[cat] for cat in categories])
        std_devs = np.array([category_averages_std_dev[cat] for cat in categories])
        vars95 = np.array([category_vars[cat] for cat in categories])

        correlation_matrix_df = self.security_manager.calculate_correlation_matrix()
        correlation_matrix = correlation_matrix_df.values  # Convert to numpy array

        return categories, expected_returns, std_devs, vars95, correlation_matrix

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
        category_names, _, _, _, _ = self.__convert_to_numpy_array()
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
        category_names, _, _, _, _ = self.__convert_to_numpy_array()
        optimal_weights_dict = dict(zip(category_names, optimal_weights))

        # Return the optimal weights along with the highest geometric mean return
        optimal_return = geometric_returns[index_max_return]
        print("Optimal Weights (Geometric Mean):", optimal_weights_dict)

        return optimal_weights_dict, optimal_return

    def optimize_for_sortino_ratio(self, risk_free_rate=0.02, target_return=0, num_portfolios=10000):
        """
        Optimize the portfolio for the highest Sortino Ratio.
        :param risk_free_rate: The risk-free rate for the market.
        :param target_return: The minimum acceptable return.
        :param num_portfolios: Number of random portfolios to generate for optimization.
        :return: Optimal weights and corresponding Sortino Ratio.
        """
        category_names, expected_returns, _, _, correlation_matrix = self.__convert_to_numpy_array()
        expected_returns = self.__convert_to_decimal(expected_returns)

        best_sortino_ratio = float('-inf')
        optimal_weights = None

        for _ in range(num_portfolios):
            weights = np.random.random(len(category_names))
            weights /= np.sum(weights)

            portfolio_return = np.dot(weights, expected_returns)
            portfolio_sortino_ratio = self.calculate_sortino_ratio(portfolio_return, risk_free_rate, target_return)

            if portfolio_sortino_ratio > best_sortino_ratio:
                best_sortino_ratio = portfolio_sortino_ratio
                optimal_weights = weights

        optimal_weights_dict = dict(zip(category_names, optimal_weights))
        print("Optimal Weights (Sortino Ratio):", optimal_weights_dict)

        return optimal_weights_dict, best_sortino_ratio

    def calculate_sortino_ratio(self, portfolio_returns, risk_free_rate, target_return=0):
        """
        Calculate the Sortino Ratio for a given set of portfolio returns.
        :param portfolio_returns: Array of portfolio returns.
        :param risk_free_rate: The risk-free rate for the market.
        :param target_return: The minimum acceptable return, default is 0.
        :return: Sortino Ratio.
        """
        # Calculate excess returns over the target return
        excess_returns = portfolio_returns - target_return

        # Calculate downside deviation
        downside_returns = excess_returns[excess_returns < 0]
        downside_deviation = np.sqrt(np.mean(downside_returns ** 2))

        # Calculate Sortino Ratio
        sortino_ratio = (np.mean(excess_returns) - risk_free_rate) / downside_deviation
        return sortino_ratio

    def generate_portfolios(self, num_portfolios=10000):
        category_names, expected_returns, std_devs, _, correlation_matrix = self.__convert_to_numpy_array()
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
        category_names, expected_returns, std_devs, _, correlation_matrix = self.__convert_to_numpy_array()
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


