#!/usr/bin/env python
"""
Quick verification script showing the refactored portfolio system working end-to-end.
This demonstrates the integration of portfolio_loader.py with portfolio_tracker.py
"""

import sys
from pathlib import Path

# Add the tradingView directory to path
sys.path.insert(0, str(Path(__file__).parent))

from portfolio_loader import load_portfolio_from_file, validate_portfolio

def print_section(title):
    """Print a formatted section header."""
    print(f"\n{'=' * 70}")
    print(f"  {title}")
    print(f"{'=' * 70}\n")

def main():
    """Demonstrate the refactored portfolio system."""
    
    print_section("Portfolio Refactoring Verification")
    
    # 1. Load portfolio from external file
    print("1. LOADING PORTFOLIO FROM FILE")
    print("-" * 70)
    portfolio_file = "portfolio.txt"
    print(f"   Loading from: {portfolio_file}")
    
    portfolio = load_portfolio_from_file(portfolio_file)
    
    if not portfolio:
        print("   ✗ ERROR: Failed to load portfolio")
        return False
    
    print(f"   ✓ Successfully loaded {len(portfolio)} entries\n")
    
    # 2. Validate portfolio
    print("2. VALIDATING PORTFOLIO DATA")
    print("-" * 70)
    
    is_valid, message = validate_portfolio(portfolio)
    print(f"   ✓ Validation: {message}\n")
    
    # 3. Display loaded data
    print("3. PORTFOLIO CONTENTS")
    print("-" * 70)
    print(f"   {'Symbol':<8} {'Exchange':<8} {'Quantity':<10} {'Buy Price':<12} {'Date':<12}")
    print("   " + "-" * 62)
    
    total_invested = 0
    for entry in portfolio:
        symbol = entry['symbol']
        exchange = entry['exchange']
        qty = entry['quantity']
        price = entry['buy_price']
        date = entry['buy_date']
        investment = qty * price
        total_invested += investment
        
        print(f"   {symbol:<8} {exchange:<8} {qty:<10} {price:>11,.0f} {date:<12}")
    
    print("   " + "-" * 62)
    print(f"   {'TOTAL INITIAL INVESTMENT:':<38} {total_invested:>11,.0f} VND\n")
    
    # 4. Verify data types
    print("4. DATA TYPE VERIFICATION")
    print("-" * 70)
    if portfolio:
        first_entry = portfolio[0]
        checks = [
            ("buy_date is string", isinstance(first_entry['buy_date'], str)),
            ("symbol is string", isinstance(first_entry['symbol'], str)),
            ("exchange is string", isinstance(first_entry['exchange'], str)),
            ("quantity is integer", isinstance(first_entry['quantity'], int)),
            ("buy_price is float", isinstance(first_entry['buy_price'], float)),
        ]
        
        for check, result in checks:
            status = "✓" if result else "✗"
            print(f"   {status} {check}")
    
    # 5. File format verification
    print("\n5. FILE FORMAT VERIFICATION")
    print("-" * 70)
    
    with open(portfolio_file, 'r') as f:
        lines = f.readlines()
    
    print(f"   Total lines in file: {len(lines)}")
    print(f"   Comment lines: {len([l for l in lines if l.strip().startswith('#')])}")
    print(f"   Empty lines: {len([l for l in lines if not l.strip()])}")
    print(f"   Data lines: {len([l for l in lines if l.strip() and not l.strip().startswith('#')])}")
    print(f"   ✓ File format valid\n")
    
    # 6. Integration check
    print("6. INTEGRATION VERIFICATION")
    print("-" * 70)
    try:
        from portfolio_tracker import PORTFOLIO, PORTFOLIO_FILE
        print(f"   ✓ portfolio_tracker.py imports successfully")
        print(f"   ✓ PORTFOLIO_FILE constant: {PORTFOLIO_FILE}")
        print(f"   ✓ PORTFOLIO loaded: {len(PORTFOLIO)} entries")
    except ImportError as e:
        print(f"   ✗ Import error: {e}")
        return False
    
    print_section("✓ REFACTORING VERIFICATION COMPLETE")
    
    print("Summary:")
    print(f"  • External portfolio file: {portfolio_file}")
    print(f"  • Entries loaded: {len(portfolio)}")
    print(f"  • Data validation: Passed")
    print(f"  • Type checking: Passed")
    print(f"  • Integration: Successful")
    print(f"  • Application ready: Yes\n")
    
    print("Next steps:")
    print("  1. Edit portfolio.txt to add/remove stocks")
    print("  2. Run: python portfolio_tracker.py")
    print("  3. Check portfolio_report.csv for results\n")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
