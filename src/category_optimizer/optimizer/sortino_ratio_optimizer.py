from category_optimizer.category_optimizer import CategoryOptimizer
import numpy as np

class SortinoRatioOptimizer(CategoryOptimizer):

    def __init__(self, security_manager):
        super().__init__(security_manager)

    def optimize_for_sortino_ratio(self, risk_free_rate=0.02, target_return=0, num_portfolios=10000):
        category_names, expected_returns, std_devs, vars95, correlation_matrix = self.__convert_to_numpy_array()
        expected_returns = self.__convert_to_decimal(expected_returns)

        # Generate portfolios
        weights, returns, volatilities, vars = self.generate_portfolios(num_portfolios)

        best_sortino_ratio = float('-inf')
        optimal_weights = None

        for i in range(len(returns)):
            # Calculate Sortino Ratio for each portfolio
            sortino_ratio = self.calculate_sortino_ratio(returns[i], risk_free_rate, target_return)

            # Update the best Sortino Ratio and corresponding weights
            if sortino_ratio > best_sortino_ratio:
                best_sortino_ratio = sortino_ratio
                optimal_weights = weights[i]

        optimal_weights_dict = dict(zip(category_names, optimal_weights))
        print("Optimal Weights (Highest Sortino Ratio):", optimal_weights_dict)

        return optimal_weights_dict, best_sortino_ratio

    def calculate_sortino_ratio(self, portfolio_return, risk_free_rate, target_return=0):
        # Assuming portfolio_return is a single aggregated return value for the portfolio

        # Calculate excess return over the risk-free rate
        excess_return = portfolio_return - risk_free_rate

        # For simplicity, let's assume downside deviation equals the standard deviation if the return is below target
        downside_deviation = np.std(portfolio_return) if portfolio_return < target_return else risk_free_rate

        # Calculate Sortino Ratio
        sortino_ratio = excess_return / downside_deviation
        return sortino_ratio