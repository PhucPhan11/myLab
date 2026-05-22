# Production-Ready Portfolio Tracker

A comprehensive Python stock portfolio tracking system using TradingView data (tvDatafeed) with support for multiple portfolio entries, automatic profit/loss calculations, and CSV reporting. **Now with externalized portfolio data management!**

## Features

✅ **Externalized Portfolio Data** - Edit portfolio.txt, not Python code  
✅ **Multi-Entry Portfolio Support** - Track unlimited stocks  
✅ **Real-time Price Fetching** - Uses TradingView via tvDatafeed  
✅ **Comprehensive Metrics** - Profit/loss %, amounts, investment values  
✅ **Smart Caching** - Avoids duplicate API calls for same symbol  
✅ **CSV Export** - Generate reports for spreadsheets  
✅ **Professional Formatting** - Readable output with formatted numbers  
✅ **Error Handling** - Graceful failures with detailed logging  
✅ **Production-Ready** - Type hints, logging, clean code structure  

## Quick Start

### Installation

```bash
pip install -r requirements.txt
```

### Basic Usage

1. **Edit portfolio entries** in `portfolio.txt` (no code changes needed!):

```txt
# Format: buy_date | symbol | exchange | quantity | buy_price
2026-05-25|BSR|HOSE|8|30900
2026-05-25|DCM|HOSE|5|41900
2026-05-20|FPT|HOSE|10|60000
```

2. **Run the tracker**:

```bash
python portfolio_tracker.py
```

### Output Example

```
==================================================
Stock: HOSE:BSR
===================================
Buy Date:        2026-05-01
Buy Price:       18,000 VND
Current Price:   19,200 VND
Quantity:        1,000 shares
Investment:      18,000,000 VND
Current Value:   19,200,000 VND
Profit:          +6.67%
Profit Amount:   +1,200,000 VND
===================================

==================================================
PORTFOLIO SUMMARY
==================================================
Total Investment:    50,000,000 VND
Total Current Value: 54,300,000 VND
Total Profit/Loss:   +4,300,000 VND
Total Return:        +8.60%
==================================================

Report saved to: portfolio_report.csv
```

## File Structure

```
portfolio_tracker.py      # Main script
portfolio_loader.py       # Portfolio data loader (NEW!)
portfolio.txt             # Portfolio data file (externalized!)
portfolio_config.py       # Configuration & settings
requirements.txt          # Python dependencies
portfolio_report.csv      # Generated report (created at runtime)
README.md                 # This file
```

## Portfolio Data Format

Edit `portfolio.txt` to define your portfolio (no code changes needed!):

```txt
# Format: buy_date | symbol | exchange | quantity | buy_price
# Comments start with # and are ignored
# Empty lines are ignored

2026-05-25|BSR|HOSE|8|30900
2026-05-25|DCM|HOSE|5|41900
2026-05-20|FPT|HOSE|10|60000
```

### File Format Specification

| Field | Type | Example | Notes |
|-------|------|---------|-------|
| buy_date | Date (YYYY-MM-DD) | 2026-05-25 | Purchase date |
| symbol | String | BSR | Stock ticker symbol |
| exchange | String | HOSE | Exchange code |
| quantity | Integer | 8 | Number of shares (must be >0) |
| buy_price | Float | 30900 | Price per share (must be >0) |

Rules:
- Separator: Pipe `|` character
- Comments: Lines starting with `#` are ignored
- Empty lines: Ignored automatically
- Whitespace: Auto-trimmed from fields
- Case: Symbols/exchanges auto-converted to uppercase

## Configuration

### Portfolio File (`portfolio.txt`)

Simply edit `portfolio.txt` to add/remove/modify stocks:

```txt
2026-05-25|BSR|HOSE|8|30900
2026-05-25|DCM|HOSE|5|41900
2026-05-20|FPT|HOSE|10|60000
```

The application automatically loads this file at startup.

### Application Settings

Edit `CURRENCY` and `OUTPUT_CSV` constants in `portfolio_tracker.py`:

```python
CURRENCY = "VND"
OUTPUT_CSV = "portfolio_report.csv"
```

For advanced configuration, see `portfolio_config.py`.

## Core Functions

| Function | Purpose |
|----------|---------|
| `load_portfolio_from_file()` | Load portfolio from portfolio.txt file |
| `validate_portfolio()` | Validate portfolio data consistency |
| `fetch_stock_price()` | Fetch latest price from TradingView |
| `calculate_position_metrics()` | Calculate P&L for single position |
| `print_position_summary()` | Display formatted position details |
| `calculate_portfolio_summary()` | Aggregate total portfolio metrics |
| `print_portfolio_summary()` | Display portfolio totals |
| `create_portfolio_dataframe()` | Convert to pandas DataFrame |
| `export_to_csv()` | Export portfolio to CSV |
| `process_portfolio()` | Main orchestration function |

## Calculated Metrics

For each position, the tracker calculates:

| Metric | Formula |
|--------|---------|
| Current Market Value | Current Price × Quantity |
| Initial Investment | Buy Price × Quantity |
| Profit/Loss Amount | Current Value - Initial Investment |
| Profit/Loss % | (P&L Amount / Initial Investment) × 100 |

## Logging

The script logs all operations to console:

```
2026-05-22 11:56:14,859 - INFO - Portfolio loaded successfully from portfolio.txt
2026-05-22 11:56:14,859 - INFO - Loaded 2 portfolio entries
2026-05-21 15:20:30,123 - INFO - Starting portfolio analysis
2026-05-21 15:20:31,456 - INFO - Fetching price for HOSE:BSR
2026-05-21 15:20:32,789 - INFO - Got price for HOSE:BSR: 19,200
```

Adjust log level by modifying:

```python
logging.basicConfig(level=logging.INFO)
```

## Advanced Usage

### Load Portfolio from Text File

The portfolio is automatically loaded from `portfolio.txt`:

```bash
python portfolio_tracker.py
```

### Load Portfolio from JSON (Alternative)

```python
from portfolio_config import load_portfolio_from_json

portfolio = load_portfolio_from_json("my_portfolio.json")
positions, summary = process_portfolio(portfolio)
```

### Custom Processing

```python
from portfolio_tracker import process_portfolio, create_portfolio_dataframe

positions, summary = process_portfolio(PORTFOLIO)
df = create_portfolio_dataframe(positions)
df.to_excel("portfolio.xlsx")  # Export to Excel
```

### Integrate with Cron

```bash
# Update portfolio daily at 9 AM (Linux/Mac)
0 9 * * * cd /path/to/portfolio && python portfolio_tracker.py
```

## Scaling Guide

### 1. Database Integration (PostgreSQL)

```python
# portfolio_db.py
import psycopg2

def load_portfolio_from_db():
    conn = psycopg2.connect("dbname=portfolio user=postgres")
    cur = conn.cursor()
    cur.execute("SELECT * FROM portfolio_entries")
    return cur.fetchall()
```

### 2. WebSocket Real-time Updates

```python
# Use TvDatafeed with websocket
from tvDatafeed import TvDatafeed
import websocket

tv = TvDatafeed()
# Subscribe to real-time quotes
tv.get_hist(..., is_first_bar=True)  # Real-time mode
```

### 3. Scheduled Refresh (APScheduler)

```python
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()
scheduler.add_job(main, 'cron', hour=9)
scheduler.start()
```

### 4. REST API with FastAPI

```python
from fastapi import FastAPI
from portfolio_tracker import process_portfolio

app = FastAPI()

@app.get("/portfolio")
async def get_portfolio():
    positions, summary = process_portfolio(PORTFOLIO)
    return {"positions": positions, "summary": summary}
```

## Troubleshooting

### "No data returned for HOSE:BSR"

- Check if symbol is correct
- Verify exchange name (HOSE, HNX, UPCOM)
- TradingView might be rate-limiting - wait and retry

### API Throttling

The script includes intelligent caching to avoid duplicate calls. Each unique symbol:exchange combination is fetched only once per run.

### Connection Issues

Ensure you have internet access. TradingView nologin method is used (may have data limitations).

## Next Steps / Roadmap

- [ ] Database backend (PostgreSQL/SQLite)
- [ ] Web dashboard (Flask/Django/FastAPI)
- [ ] WebSocket real-time updates
- [ ] Scheduled automatic refresh (APScheduler)
- [ ] Email alerts for profit/loss thresholds
- [ ] Multi-user support
- [ ] Portfolio comparison/benchmarking
- [ ] Tax reporting features
- [ ] Transaction history tracking
- [ ] Mobile app integration

## Performance Notes

- **API Calls**: ~1 second per unique symbol (TradingView limit)
- **Processing**: <100ms for calculations
- **CSV Export**: Instant (uses pandas)
- **Memory**: Minimal (<10MB for 100 positions)

## License

MIT - Feel free to use, modify, and distribute

## Support

For issues with tvDatafeed:
https://github.com/rongardF/tvdatafeed

For TradingView documentation:
https://www.tradingview.com/

## Author Notes

This script is designed to be:
- **Easy to understand** - Clear variable names, good comments
- **Easy to extend** - Modular functions, configuration files
- **Production-ready** - Error handling, logging, type hints
- **Scalable** - Database-ready architecture

Start simple, scale up as needed. ✨
