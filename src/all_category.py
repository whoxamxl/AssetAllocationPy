from category.category import Category


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