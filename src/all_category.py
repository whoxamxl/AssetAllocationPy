from categories.category import Category
from categories.sub_categories.securities.security import Security
import numpy as np


class AllCategory:
    def __init__(self):
        self.categories = []

    def find_or_create_category(self, category_name):
        category = next((cat for cat in self.categories if cat.name == category_name), None)
        if not category:
            category = Category(category_name)
            self.categories.append(category)
        return category

    def add_security(self, security):
        category = self.find_or_create_category(type(security).__name__)
        subcategory = category.find_or_create_subcategory(security.sub_category)
        subcategory.add_security(security)

    def add_securities(self, securities):
        for ticker, subcategory_name, category_name, sub_category_weight in securities:
            category = self.find_or_create_category(category_name)
            subcategory = category.find_or_create_subcategory(subcategory_name)
            category.add_security_to_subcategory(Security(ticker, subcategory_name, sub_category_weight),
                                                 subcategory_name)

    def remove_securities(self, tickers_to_remove):
        pass

    def check_subcategory_weights(self):
        for category in self.categories:
            for subcategory in category.subcategories:
                total_weight = sum(security.sub_risk_weight for security in subcategory.securities if
                                   security.sub_risk_weight is not None)

                # Check if the total weight is approximately 1 (100%)
                if not np.isclose(total_weight, 1, atol=0.01):
                    raise ValueError(
                        f"Total weight in sub-category '{subcategory.name}' of category '{category.name}' is not 1 (100%). It's {total_weight * 100:.2f}%.")

        return True  # Only returns True if all checks pass

    def assign_asset_weights_to_subcategories(self):
        for category in self.categories:
            for subcategory in category.subcategories:
                subcategory.calculate_asset_weights()

    def print_security_weight_details(self):
        for category in self.categories:
            print(f"Category: {category.name}")
            for subcategory in category.subcategories:
                print(f"  Sub-Category: {subcategory.name}")
                for security in subcategory.securities:
                    ticker = security.ticker
                    risk_weight = security.sub_risk_weight  # assuming this is an attribute in Security
                    asset_weight = security.sub_asset_weight  # assuming this is an attribute in Security
                    print(f"    Security: {ticker}, Risk Weight: {risk_weight}, Asset Weight: {asset_weight}")

