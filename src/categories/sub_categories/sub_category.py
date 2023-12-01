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
