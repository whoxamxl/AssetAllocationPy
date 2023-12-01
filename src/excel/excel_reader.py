import pandas as pd


class ExcelReader:
    def __init__(self, file_path, all_category):
        self.file_path = file_path
        self.all_category = all_category

    def read_and_update_securities(self):
        xls = pd.ExcelFile(self.file_path)
        current_tickers = set()

        for sheet_name in xls.sheet_names:
            df = pd.read_excel(xls, sheet_name=sheet_name, usecols=['Ticker', 'Sub Category'])
            df = df.dropna(subset=['Ticker'])

            if df.empty:
                print(f"Warning: Sheet '{sheet_name}' is empty or does not have the expected format.")
                continue

            securities = df.apply(
                lambda row: (row['Ticker'], row['Sub Category'] if pd.notna(row['Sub Category']) else None, sheet_name),
                axis=1)
            self.all_category.add_securities(securities.tolist())
            current_tickers.update(df['Ticker'])

        all_tickers = set(security.ticker for category in self.all_category.categories
                                            for subcategory in category.subcategories
                                            for security in subcategory.securities)
        securities_to_remove = all_tickers - current_tickers
        self.all_category.remove_securities(list(securities_to_remove))