from category_securities.category_security import CategorySecurity
import pandas as pd

class CategorySecurityManager:

    def __init__(self):
        self.category_securities = []

    def add_category_security(self, category, sub_weight, sub_historical_data, sub_metrics):
        self.category_securities.append(CategorySecurity(category, sub_weight, sub_historical_data, sub_metrics))

    def group_aggregated_data(self):
        all_historical_data = pd.DataFrame()
        all_returns = pd.Series()

        for security in self.category_securities:
            all_historical_data[security.category] = security.historical_data
            all_returns[security.category] = security.average_return

        all_historical_data = all_historical_data.resample('D').last()
        all_historical_data.dropna(inplace=True)
        all_historical_data.interpolate(method='pchip', inplace=True)

        return all_historical_data, all_returns
