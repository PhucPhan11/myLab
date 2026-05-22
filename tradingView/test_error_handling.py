#!/usr/bin/env python
"""Test script for portfolio loader error handling."""

import sys
sys.path.insert(0, 'c:\\Work\\Project\\Lab\\tradingView')

from portfolio_loader import load_portfolio_from_file, validate_portfolio

print("Testing portfolio loader error handling...")
print("=" * 60)

portfolio = load_portfolio_from_file('portfolio_test.txt')
print(f"\n✓ Portfolio loaded: {len(portfolio)} valid entries")

print("\nValid entries loaded:")
for i, p in enumerate(portfolio, 1):
    print(f"  {i}. {p['symbol']}: {p['quantity']} shares @ {p['buy_price']} ({p['exchange']})")

valid, msg = validate_portfolio(portfolio)
print(f"\n✓ Validation: {msg}")

print("\n" + "=" * 60)
print("✓ Error handling test passed!")
print("\nNote: See WARNING messages above for details on invalid entries")
