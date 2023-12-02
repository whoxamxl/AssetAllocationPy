from categories.sub_categories.securities.security import Security


class SubCategory:
    def __init__(self, name):
        self.name = name
        self.securities = []

    def add_security(self, security):
        if isinstance(security, Security):
            self.securities.append(security)
        else:
            raise TypeError("Only Security instances can be added")

    def calculate_asset_weights(self):
        total_inverse_risk = sum(
            1 / security.standard_deviation_5y for security in self.securities if security.standard_deviation_5y > 0)

        if total_inverse_risk == 0:
            raise ValueError("Total inverse risk is zero. Cannot calculate asset weights.")

        for security in self.securities:
            if security.standard_deviation_5y > 0:
                inverse_risk = 1 / security.standard_deviation_5y
                security.sub_asset_weight = inverse_risk / total_inverse_risk
            else:
                security.sub_asset_weight = 0  # Handle securities with zero standard deviation if necessary
