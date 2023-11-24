import pandas as pd


class CategorySecurity:
    def __init__(self, category, sub_weight, sub_historical_data, sub_metrics):
        self.category = category
        self.historical_data = None
        self.average_return = None
        self.sub_category_weights = sub_weight
        self.sub_category_metrics = sub_metrics
        self.sub_category_historical_data = sub_historical_data
        self.calculate_weighted_average_historical_data()
        self.set_average_return()


    def calculate_weighted_average_historical_data(self):
        # Ensure the index of sub_category_historical_data is a DateTimeIndex for resampling
        if not isinstance(self.sub_category_historical_data.index, pd.DatetimeIndex):
            raise ValueError("The index of sub_category_historical_data must be a DateTimeIndex for resampling.")

        # Create an empty DataFrame to store the weighted average
        weighted_averages = pd.DataFrame(columns=self.sub_category_historical_data.columns)

        # Align sub-categories
        aligned_sub_categories = set(self.sub_category_historical_data.columns) & set(self.sub_category_weights.keys())

        for sub_category in aligned_sub_categories:
            weight = self.sub_category_weights[sub_category]
            weighted_avg = (self.sub_category_historical_data[sub_category] * weight).sum() / weight
            weighted_averages.loc[0, sub_category] = weighted_avg

        # Resample and drop NaN values
        resampled_weighted_averages = weighted_averages.resample('D').last().dropna()
        self.historical_data = resampled_weighted_averages

    def set_average_return(self):
        self.average_return = self.sub_category_metrics["Expected Annual Return"]

    def print_category_security(self):
        print("-----------------------------------")
        print(self.category)
        print(self.sub_category_weights)
        print(self.sub_category_metrics)
        print(self.sub_category_historical_data)
        print(self.historical_data)
        print(self.average_return)
        print("-----------------------------------")