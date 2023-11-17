import pandas as pd

class ExcelReader:
    def __init__(self, file_path, security_manager):
        self.file_path = file_path
        self.security_manager = security_manager

    def read_and_update_securities(self):
        # Read the Excel file
        xls = pd.ExcelFile(self.file_path)
        current_tickers = set()  # Set to hold tickers present in the Excel file

        # Read each sheet and update current_tickers
        # Iterate through each sheet
        for sheet_name in xls.sheet_names:
            df = pd.read_excel(xls, sheet_name=sheet_name)

            # Check if the DataFrame is empty or does not have the expected column
            if df.empty or 'Ticker' not in df.columns:
                print(f"Warning: Sheet '{sheet_name}' is empty or does not have the expected format.")
                continue

            # Assuming tickers are in a column named 'Ticker'
            for ticker in df['Ticker'].dropna():
                # Use sheet name as security type
                self.security_manager.add_security(ticker, sheet_name)
                current_tickers.add(ticker)  # Update the set with the current ticker

        # Remove securities not in current_tickers
        securities_to_remove = [security.ticker for security in self.security_manager.securities if security.ticker not in current_tickers]
        for ticker in securities_to_remove:
            self.security_manager.remove_security(ticker)
