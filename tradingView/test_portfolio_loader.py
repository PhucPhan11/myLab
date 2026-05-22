#!/usr/bin/env python
"""Test script for portfolio loader."""

import sys
sys.path.insert(0, 'c:\\Work\\Project\\Lab\\tradingView')

from portfolio_loader import load_portfolio_from_file, validate_portfolio

print("Testing portfolio loader...")
print("-" * 50)

portfolio = load_portfolio_from_file('portfolio.txt')
print(f"\n✓ Portfolio loaded: {len(portfolio)} entries")

print("\nPortfolio contents:")
for p in portfolio:
    print(f"  - {p['symbol']}: {p['quantity']} shares @ {p['buy_price']} VND ({p['exchange']})")

valid, msg = validate_portfolio(portfolio)
print(f"\n✓ Validation: {msg}")

print("\nDetailed entries:")
for i, p in enumerate(portfolio, 1):
    print(f"\n  Entry {i}:")
    print(f"    buy_date: {p['buy_date']}")
    print(f"    symbol: {p['symbol']}")
    print(f"    exchange: {p['exchange']}")
    print(f"    quantity: {p['quantity']} (type: {type(p['quantity']).__name__})")
    print(f"    buy_price: {p['buy_price']} (type: {type(p['buy_price']).__name__})")

print("\n" + "-" * 50)
print("✓ All tests passed!")
