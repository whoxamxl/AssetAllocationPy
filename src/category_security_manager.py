from sub_category_securities.category_security import CategorySecurity


class CategorySecurityManager:

    def __init__(self):
        self.category_securities = []

    def add_category_security(self, category, sub_weight, sub_historical_data, sub_metrics):
        self.category_securities.append(CategorySecurity(category, sub_weight, sub_historical_data, sub_metrics))
