import pandas as pd


class ExcelWriter:
    def __init__(self, file_path, security_manager):
        self.file_path = file_path
        self.security_manager = security_manager

    def update_excel(self):
        try:
            # Read existing data from the file
            with pd.ExcelFile(self.file_path) as xls:
                existing_data = {sheet_name: pd.read_excel(xls, sheet_name) for sheet_name in xls.sheet_names}

            # Update data
            updated_data = {}
            for security_type in set(type(s).__name__ for s in self.security_manager.securities):
                securities_data = []
                for security in self.security_manager.securities:
                    if type(security).__name__ == security_type:
                        securities_data.append({
                            'Ticker': security.ticker,
                            'Name': security.name,
                            'Exchange Name': security.exchange_name,
                            'Category Name': security.category_name,
                            'Expense Ratio': security.expense_ratio,
                            'Dividend Yield': security.dividend_yield,
                            '5y Std Dev': security.std_5y,
                            'Risk Weight': security.risk_weight,
                            'Asset Weight': security.asset_weight
                        })

                updated_data[security_type] = pd.DataFrame(securities_data)

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

# Usage remains the same
