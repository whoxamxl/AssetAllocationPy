from ..security import Security

class Currency (Security):
    class_risk_weight = None
    class_asset_weight = None

    def __init__ (self, ticker):
        super().__init__(ticker)