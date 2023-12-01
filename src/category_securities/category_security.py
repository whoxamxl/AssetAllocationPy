import pandas as pd

class CategorySecurity:
    def __init__(self, category, sub_weight, sub_historical_data, sub_metrics):
        self.category = category
        self.sub_category_weights = sub_weight
        self.sub_category_metrics = sub_metrics
        self.sub_category_historical_data = sub_historical_data
        self.historical_data = self.calculate_weighted_average_historical_data()
        self.average_return = self.set_average_return()

    def calculate_weighted_average_historical_data(self):
        # Ensure each DataFrame in sub_category_historical_data is a DateTimeIndex
        for sub_category, data in self.sub_category_historical_data.items():
            if not isinstance(data.index, pd.DatetimeIndex):
                raise ValueError(f"The index of sub_category_historical_data for '{sub_category}' must be a DateTimeIndex.")

        # Calculate weighted averages
        weighted_averages = pd.DataFrame()
        for sub_category, weight in self.sub_category_weights.items():
            if sub_category in self.sub_category_historical_data:
                # Resample sub-categories data
                resampled_data = self.sub_category_historical_data[sub_category].resample('D').last().dropna()
                weighted_averages[sub_category] = resampled_data * weight

        # Sum the weighted averages across all sub-categories
        total_weight = sum(self.sub_category_weights.values())
        if total_weight > 0:
            return weighted_averages.sum(axis=1) / total_weight
        else:
            return pd.DataFrame()

    def set_average_return(self):
        return self.sub_category_metrics.get("Expected Annual Return", 0)

    def print_category_security(self):
        print("-----------------------------------")
        print(f"Category: {self.category}")
        print("Sub-categories Weights:", self.sub_category_weights)
        print("Sub-categories Metrics:", self.sub_category_metrics)
        print("Sub-categories Historical Data:", self.sub_category_historical_data)
        print("Historical Data:", self.historical_data)
        print("Average Return:", self.average_return)
        print("-----------------------------------")
