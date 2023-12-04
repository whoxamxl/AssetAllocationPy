SUB_CATEGORY_CONSTRAINTS = {
    "Equity": {
        "Traditional Equity_min": 0.6,
    },
    "Bond": {

    },
    "Alternative": {
        "Metal_min": 0.3,

    }
}

CATEGORY_CONSTRAINTS = {
    "Equity_min": 0.3,
    "Bond_min": 0.1,
    "Alternative_max": 0.2,
}

#RISK_FREE_RATE = None -> Automatically fetch T-Bill 3 Month rate
RISK_FREE_RATE = 0.02