import pandas as pd

class ExcelWriter:
    def __init__(self, file_path, all_category):
        self.file_path = file_path
        self.all_category = all_category

    def update_excel(self):
        try:
            # Read existing data from the file
            with pd.ExcelFile(self.file_path) as xls:
                existing_data = {sheet_name: pd.read_excel(xls, sheet_name) for sheet_name in xls.sheet_names}

            # Update data
            updated_data = {}
            for category in self.all_category.categories:
                securities_data = []
                for subcategory in category.subcategories:
                    for security in subcategory.securities:
                        securities_data.append({
                            'Ticker': security.ticker,
                            'Sub Category': security.sub_category,
                            'Sub Category Risk Weight': round(security.sub_category_weight * 100, 2),
                            'Name': security.name,
                            'Category Name': security.category_name,
                            'Exchange Name': security.exchange_name,
                            'Traded Currency': security.traded_currency,
                            'Expense Ratio': round(security.expense_ratio * 100, 4),
                            'Dividend Yield': round(security.dividend_yield * 100, 2),
                            'Simple Return': round(security.geometric_mean_5y * 100, 2),
                            'Total Return': round(security.adjusted_geometric_mean_5y * 100, 2),
                            'Standard Deviation': round(security.standard_deviation_5y * 100, 2),
                            'Downside Deviation': round(security.downside_deviation_5y * 100, 2),
                            'Value at Risk 95%': round(security.var_95 * 100, 2),
                            'Sharpe Ratio': security.sharpe_ratio,
                            'Asset Weight': security.asset_weight,
                        })

                if securities_data:
                    updated_data[category.name] = pd.DataFrame(securities_data)

            # Write updated data to file
            with pd.ExcelWriter(self.file_path, engine='openpyxl') as writer:
                for sheet_name, df in updated_data.items():
                    df.to_excel(writer, sheet_name=sheet_name, index=False)

                # Keep existing sheets not being updated
                for sheet_name, df in existing_data.items():
                    if sheet_name not in updated_data:
                        df.to_excel(writer, sheet_name=sheet_name, index=False)

        except Exception as e:
            print(f"An error occurred: {e}")
