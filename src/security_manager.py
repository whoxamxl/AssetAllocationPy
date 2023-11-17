from securities.security_type.alternative import Alternative
from securities.security_type.bond import Bond
from securities.security_type.commodity import Commodity
from securities.security_type.currency import Currency
from securities.security_type.equity import Equity
from securities.security_type.metal import Metal
from securities.security_type.reit import Reit


class SecurityManager:
    def __init__(self):
        self.securities = []

    def add_security(self, ticker, type):
        if not self.__security_exists(ticker):
            match type:
                case "Equity":
                    self.securities.append(Equity(ticker))
                case "Bond":
                    self.securities.append(Bond(ticker))
                case "REIT":
                    self.securities.append(Reit(ticker))
                case "Metal":
                    self.securities.append(Metal(ticker))
                case "Commodity":
                    self.securities.append(Commodity(ticker))
                case "Currency":
                    self.securities.append(Currency(ticker))
                case "Alternative":
                    self.securities.append(Alternative(ticker))
                case _:
                    print("Unknown type.")
        else:
            print(f"Security with ticker {ticker} already exists.")

    def __security_exists(self, ticker):
        return any(security.ticker == ticker for security in self.securities)

    def remove_security(self, ticker):
        # Remove security with the specified ticker
        self.securities = [security for security in self.securities if security.ticker != ticker]

    def print_securities(self):
        for security in self.securities:
            print(f"Ticker: {security.ticker} Geometric Mean: {security.geometric_mean_5y}% Adjusted Geometric Mean: {security.adjusted_geometric_mean_5y}%")

