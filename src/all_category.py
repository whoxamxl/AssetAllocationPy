from categories.category import Category
from categories.sub_categories.securities.security import Security


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
        for ticker, subcategory_name, category_name in securities:
            category = self.find_or_create_category(category_name)
            subcategory = category.find_or_create_subcategory(subcategory_name)
            category.add_security_to_subcategory(Security(ticker, subcategory_name), subcategory_name)

    def remove_securities(self, tickers_to_remove):
        pass