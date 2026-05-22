"""
Portfolio configuration file - easily manage your portfolio data.

This file can be extended to support:
- Loading from JSON/YAML files
- Fetching from databases
- Environment-based configuration
"""

from typing import List, Dict

# Portfolio entries - customize this with your actual holdings
PORTFOLIO: List[Dict] = [
    {
        "buy_date": "2026-05-25",
        "symbol": "BSR",
        "exchange": "HOSE",
        "quantity": 8,
        "buy_price": 30900
    },
    {
        "buy_date": "2026-05-25",
        "symbol": "DCM",
        "exchange": "HOSE",
        "quantity": 5,
        "buy_price": 41900
    }
]

# Application settings
SETTINGS = {
    "currency": "VND",
    "output_csv": "portfolio_report.csv",
    "log_level": "INFO",
    "cache_enabled": True,
    "timeout_seconds": 30
}


def load_portfolio_from_json(filepath: str) -> List[Dict]:
    """
    Load portfolio from JSON file.
    
    Example JSON format:
    [
        {
            "buy_date": "2026-05-01",
            "symbol": "BSR",
            "exchange": "HOSE",
            "quantity": 1000,
            "buy_price": 18000
        }
    ]
    """
    import json
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Portfolio file {filepath} not found")
        return []


def save_portfolio_to_json(portfolio: List[Dict], filepath: str) -> None:
    """Save portfolio to JSON file."""
    import json
    with open(filepath, 'w') as f:
        json.dump(portfolio, f, indent=2)
