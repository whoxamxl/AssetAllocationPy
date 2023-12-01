from category.sub_category.sub_category import SubCategory


class Category:
    def __init__(self, name):
        self.name = name
        self.subcategories = []

    def add_subcategory(self, subcategory):
        pass

    def find_or_create_subcategory(self, subcategory_name):
        subcategory = next((sc for sc in self.subcategories if sc.name == subcategory_name), None)
        if not subcategory:
            subcategory = SubCategory(subcategory_name)
            self.subcategories.append(subcategory)
        return subcategory