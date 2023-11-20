from category_optimizer.category_optimizer import CategoryOptimizer
import numpy as np

class GeometricMeanReturnOptimizer(CategoryOptimizer):

    def __init__(self, security_manager):
        super().__init__(security_manager)

    def optimize_geometric_mean(self):
        # Generate random portfolios and calculate their geometric mean returns
        weights, geometric_returns = self.generate_portfolios_geometric_mean()

        # Find the portfolio with the highest geometric mean return
        index_max_return = np.argmax(geometric_returns)
        optimal_weights = weights[index_max_return]

        # Map optimal weights to category names
        category_names, _, _, _, _ = self.convert_to_numpy_array()
        optimal_weights_dict = dict(zip(category_names, optimal_weights))

        # Return the optimal weights along with the highest geometric mean return
        optimal_return = geometric_returns[index_max_return]
        print("Optimal Weights (Geometric Mean):", optimal_weights_dict)

        return optimal_weights_dict, optimal_return
