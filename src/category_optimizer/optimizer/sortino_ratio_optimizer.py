from category_optimizer.category_optimizer import CategoryOptimizer
import numpy as np


class SortinoRatioOptimizer(CategoryOptimizer):

    def __init__(self, security_manager):
        super().__init__(security_manager)

    def calculate_sortino_ratio(self, portfolio_return, portfolio_downside_risk, risk_free_rate):
        return (portfolio_return - risk_free_rate) / portfolio_downside_risk

    def calculate_geometric_mean(self, returns):
        # Calculate the geometric mean of the returns
        return np.prod(1 + returns) ** (1 / len(returns)) - 1

    def optimize_sortino_ratio(self, target_return=0, num_portfolios=50000):
        category_names, _, _, _, downside_risks, _ = self.convert_to_numpy_array()
        returns_in_series = self.security_manager.calculate_adjusted_yearly_returns()
        risk_free_rate = self.security_manager.risk_free_rate / 100

        # Calculate geometric mean returns for each category
        geometric_mean_returns = {cat: self.calculate_geometric_mean(returns_in_series[cat]) for cat in category_names}

        best_sortino_ratio = float('-inf')
        optimal_weights = None

        for _ in range(num_portfolios):
            weights = np.random.random(len(category_names))
            weights /= np.sum(weights)  # Normalize to sum to 1

            # Calculate expected portfolio return using geometric mean
            portfolio_return = np.dot(weights, [geometric_mean_returns[cat] for cat in category_names])

            # Check if the portfolio meets the target return
            if portfolio_return >= target_return:
                # Calculate Sortino Ratio
                portfolio_downside_risk = np.dot(weights, downside_risks)
                sortino_ratio = self.calculate_sortino_ratio(portfolio_return, portfolio_downside_risk, risk_free_rate)

                if sortino_ratio > best_sortino_ratio:
                    best_sortino_ratio = sortino_ratio
                    optimal_weights = weights

        # Convert optimal weights to a dictionary
        optimal_weights_dict = {category: weight for category, weight in zip(category_names, optimal_weights)}

        print("Optimal Weights (Sortino Ratio):", optimal_weights_dict)
        return optimal_weights_dict, best_sortino_ratio

