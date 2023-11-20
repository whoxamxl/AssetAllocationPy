import numpy as np



class CategoryOptimizer:


    def __init__(self, security_manager):
        self.security_manager = security_manager



    def convert_to_numpy_array(self):
        category_averages_return, category_averages_std_dev, _ = self.security_manager.calculate_aggregated_data()
        category_vars = self.security_manager.calculate_var_monte_carlo()
        category_downside_risk = self.security_manager.calculate_yearly_downside_risks()

        # Ensure the order of categories is consistent
        categories = category_averages_return.keys()

        # Convert to numpy arrays
        expected_returns = np.array([category_averages_return[cat] for cat in categories])
        std_devs = np.array([category_averages_std_dev[cat] for cat in categories])
        vars95 = np.array([category_vars[cat] for cat in categories])
        downside_risks = np.array([category_downside_risk[cat] for cat in categories])

        correlation_matrix_df = self.security_manager.calculate_correlation_matrix()
        correlation_matrix = correlation_matrix_df.values  # Convert to numpy array

        return categories, expected_returns, std_devs, vars95, downside_risks, correlation_matrix

    def convert_to_decimal(self, percentage_rate):
        return percentage_rate / 100





    def generate_portfolios(self, num_portfolios=10000, max_portfolio_var=None):
        category_names, expected_returns, std_devs, vars95, downside_risk, correlation_matrix = self.convert_to_numpy_array()
        expected_returns = self.convert_to_decimal(expected_returns)
        cov_matrix = np.outer(std_devs, std_devs) * correlation_matrix

        portfolio_weights = []
        portfolio_returns = []
        portfolio_volatilities = []
        portfolio_vars = []

        for _ in range(num_portfolios):
            weights = np.random.random(len(category_names))
            weights /= np.sum(weights)

            # Calculate portfolio returns and volatility
            portfolio_return = np.dot(weights, expected_returns)
            portfolio_volatility = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))

            # Calculate portfolio VaR
            portfolio_var = self.calculate_portfolio_var(weights, vars95)

            # Check VaR constraint
            if max_portfolio_var is not None and portfolio_var > max_portfolio_var:
                continue

            portfolio_weights.append(weights)
            portfolio_returns.append(portfolio_return)
            portfolio_volatilities.append(portfolio_volatility)
            portfolio_vars.append(portfolio_var)

        return np.array(portfolio_weights), np.array(portfolio_returns), np.array(portfolio_volatilities), np.array(
            portfolio_vars)

    def calculate_portfolio_var(self, weights, category_vars):
        # Simplified aggregation of VaR
        weighted_vars = weights * category_vars
        portfolio_var = np.sum(weighted_vars)
        return portfolio_var

    def generate_portfolios_geometric_mean(self, num_portfolios=10000):
        category_names, expected_returns, std_devs, _, _, correlation_matrix = self.convert_to_numpy_array()
        expected_returns = self.convert_to_decimal(expected_returns)
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


