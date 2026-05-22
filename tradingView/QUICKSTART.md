# Quick Start Guide - Portfolio Tracker

## What You Got

A production-ready Python stock portfolio tracking system that:
- ✅ Loads portfolio from externalized text file (no code changes!)
- ✅ Tracks multiple stocks with real-time prices from TradingView
- ✅ Calculates profit/loss amounts and percentages
- ✅ Exports reports to CSV
- ✅ Includes comprehensive error handling and logging
- ✅ Uses reusable, modular functions
- ✅ Is fully documented and easy to extend

## Files Created

| File | Purpose |
|------|---------|
| `portfolio_tracker.py` | Main script - run this! |
| `portfolio_loader.py` | Portfolio data loader (NEW!) |
| `portfolio.txt` | Portfolio data file (externalized!) |
| `portfolio_config.py` | Configuration and settings |
| `advanced_integration.py` | Examples for production use |
| `requirements.txt` | Python dependencies |
| `README.md` | Detailed documentation |
| `ARCHITECTURE.md` | Scaling strategies |
| `IMPLEMENTATION_GUIDE.md` | Step-by-step scaling roadmap |
| `portfolio_report.csv` | Generated report |

## Installation

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Edit your portfolio in portfolio.txt (see below)

# 3. Run the tracker
python portfolio_tracker.py
```

## Configure Your Portfolio

Edit `portfolio.txt` with your stock holdings:

```txt
# Format: buy_date | symbol | exchange | quantity | buy_price
# Comments starting with # are ignored
# Empty lines are ignored

2026-05-25|BSR|HOSE|8|30900
2026-05-25|DCM|HOSE|5|41900
2026-05-20|FPT|HOSE|10|60000
```

That's it! No Python code changes needed.

```
==================================================
Stock: HOSE:BSR
===================================
Buy Date:        2026-05-01
Buy Price:       18,000 VND
Current Price:   30,700 VND
Quantity:        1,000 shares
Investment:      18,000,000 VND
Current Value:   30,700,000 VND
Profit:          +70.56%
Profit Amount:   +12,700,000 VND

==================================================
Stock: HOSE:VNM
===================================
Buy Date:        2026-03-20
Buy Price:       87,000 VND
Current Price:   59,000 VND
Quantity:        100 shares
Investment:      8,700,000 VND
Current Value:   5,900,000 VND
Profit:          -32.18%
Profit Amount:   -2,800,000 VND

==================================================
           PORTFOLIO SUMMARY
==================================================
Total Investment:    26,700,000 VND
Total Current Value: 36,600,000 VND
Total Profit/Loss:   +9,900,000 VND
Total Return:        +37.08%
==================================================

Report saved to: portfolio_report.csv
```

## Key Features Explained

### 1. Externalized Portfolio Data (NEW!)
No need to edit Python code. Edit `portfolio.txt`:
```txt
2026-05-25|BSR|HOSE|8|30900
2026-05-25|DCM|HOSE|5|41900
```

### 2. Multiple Portfolio Support
Add as many stocks as you want to `portfolio.txt`

### 3. Smart Caching
Avoids duplicate API calls for the same stock:
```python
# First BSR call: 1 second (API fetch)
# Second BSR call: <1ms (cache hit)
```

### 4. Automatic CSV Export
Generates `portfolio_report.csv` with all metrics:
- Buy/Current prices
- Quantities
- Investment amounts
- Profit/Loss metrics

### 5. Comprehensive Error Handling
- Handles missing TradingView data gracefully
- Logs all operations for debugging
- Skips failed entries, continues processing others
- Validates portfolio format on load

### 6. Production-Ready Code
- Type hints for IDE support
- Docstrings on all functions
- Clean variable naming
- Organized into reusable functions

## Main Functions

```python
# Load portfolio from file
portfolio = load_portfolio_from_file("portfolio.txt")

# Validate portfolio
is_valid, msg = validate_portfolio(portfolio)

# Fetch current price from TradingView
current_price = fetch_stock_price(tv, "BSR", "HOSE")

# Calculate metrics for one position
metrics = calculate_position_metrics(portfolio_entry, current_price)

# Create pandas DataFrame for export
df = create_portfolio_dataframe(positions)

# Export to CSV
export_to_csv(df)

# Process entire portfolio
positions, summary = process_portfolio(PORTFOLIO)
```

## Logging

All operations are logged. Check the console output:
```
2026-05-22 11:56:14,859 - INFO - Portfolio loaded successfully from portfolio.txt
2026-05-22 11:56:14,859 - INFO - Loaded 2 portfolio entries
2026-05-21 15:20:30,123 - INFO - Starting portfolio analysis
2026-05-21 15:20:31,456 - INFO - Fetching price for HOSE:BSR
2026-05-21 15:20:32,789 - INFO - Got price for HOSE:BSR: 30,700
2026-05-21 15:20:33,000 - INFO - Portfolio exported to portfolio_report.csv
```

## Customization

### Change Currency
Edit line 18 in `portfolio_tracker.py`:
```python
CURRENCY = "VND"  # Change to "USD", "EUR", etc.
```

### Change Output Filename
Edit line 19:
```python
OUTPUT_CSV = "my_portfolio_report.csv"
```

### Add More Stocks
Just edit `portfolio.txt`:
```txt
2026-05-25|BSR|HOSE|8|30900
2026-05-25|DCM|HOSE|5|41900
2026-05-20|FPT|HOSE|10|60000
# Add more as needed
```

## Next Steps to Scale

### Week 1: Add Database
```bash
pip install sqlalchemy
# See IMPLEMENTATION_GUIDE.md for database setup
```

### Week 2: Add Web API
```bash
pip install fastapi uvicorn
# See ARCHITECTURE.md for FastAPI examples
```

### Week 3: Add Scheduling
```bash
pip install apscheduler
# Run portfolio refresh daily at 9 AM
```

### Week 4: Add Notifications
```bash
pip install python-telegram-bot
# Get Telegram alerts on price changes
```

See `IMPLEMENTATION_GUIDE.md` for detailed roadmap.

## Troubleshooting

### "No data returned for HOSE:BSR"
- Verify symbol is correct (check TradingView)
- Try different exchange (HOSE, HNX, UPCOM)
- TradingView may be rate-limiting - wait 5 minutes and retry

### Missing pandas or tvDatafeed
```bash
pip install -r requirements.txt
```

### Permission denied on portfolio_report.csv
- The script creates the file automatically
- Make sure you have write permissions in the directory

### Script runs but no output
- Check that `PORTFOLIO` list has entries (lines 42-61)
- Check internet connection
- Review logs for errors

## Support

For issues with tvDatafeed: https://github.com/rongardF/tvdatafeed

For TradingView data: https://www.tradingview.com/

## License

MIT License - Use freely, modify as needed.

---

**Ready to get started?** Edit `portfolio_tracker.py` with your stock entries and run:
```bash
python portfolio_tracker.py
```

**Questions?** Check `README.md` for detailed documentation or `ARCHITECTURE.md` for scaling options.
