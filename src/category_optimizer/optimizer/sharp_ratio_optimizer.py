from category_optimizer.category_optimizer import CategoryOptimizer
import numpy as np

class SharpRatioOptimizer(CategoryOptimizer):

    def __init__(self, security_manager):
        super().__init__(security_manager)

    def optimize_sharp_ratio(self):
        # Generate random portfolios and their returns and volatilities
        weights, returns, volatilities, _ = self.generate_portfolios()

        # Adjust returns for risk-free rate
        adjusted_returns = returns - (self.security_manager.risk_free_rate / 100)

        # Calculate Sharpe Ratios for each portfolio
        sharpe_ratios = adjusted_returns / volatilities

        # Find the portfolio with the highest Sharpe Ratio
        index_max_sharpe = np.argmax(sharpe_ratios)
        optimal_weights = weights[index_max_sharpe]

        # Map optimal weights to category names
        category_names, _, _, _, _, _ = self.convert_to_numpy_array()
        optimal_weights_dict = dict(zip(category_names, optimal_weights))

        # Optional: Calculate and return expected return and volatility for the optimal portfolio
        optimal_return = returns[index_max_sharpe]
        optimal_volatility = volatilities[index_max_sharpe]

        print("Optimal Weights (Sharp Ratio): ", optimal_weights_dict)
        print("Optimal Return (Sharp Ratio): ", optimal_return, "Optimal Volatility (Sharp Ratio): ", optimal_volatility)

        return optimal_weights_dict, optimal_return, optimal_volatility