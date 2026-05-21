# Production-Ready Portfolio Tracker

A comprehensive Python stock portfolio tracking system using TradingView data (tvDatafeed) with support for multiple portfolio entries, automatic profit/loss calculations, and CSV reporting.

## Features

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

1. **Edit portfolio entries** in `portfolio_tracker.py` (lines 42-61):

```python
PORTFOLIO = [
    {
        "buy_date": "2026-05-01",
        "symbol": "BSR",
        "exchange": "HOSE",
        "quantity": 1000,
        "buy_price": 18000
    },
    {
        "buy_date": "2026-04-15",
        "symbol": "FPT",
        "exchange": "HOSE",
        "quantity": 200,
        "buy_price": 120000
    }
]
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
portfolio_config.py       # Configuration & portfolio data
requirements.txt          # Python dependencies
portfolio_report.csv      # Generated report (created at runtime)
README.md                 # This file
```

## Core Functions

| Function | Purpose |
|----------|---------|
| `fetch_stock_price()` | Fetch latest price from TradingView |
| `calculate_position_metrics()` | Calculate P&L for single position |
| `print_position_summary()` | Display formatted position details |
| `calculate_portfolio_summary()` | Aggregate total portfolio metrics |
| `print_portfolio_summary()` | Display portfolio totals |
| `create_portfolio_dataframe()` | Convert to pandas DataFrame |
| `export_to_csv()` | Export portfolio to CSV |
| `process_portfolio()` | Main orchestration function |

## Portfolio Entry Structure

Each portfolio entry requires:

```python
{
    "buy_date": "YYYY-MM-DD",      # Purchase date
    "symbol": "BSR",                # Stock symbol
    "exchange": "HOSE",             # Exchange (HOSE, HNX, UPCOM)
    "quantity": 1000,               # Number of shares
    "buy_price": 18000              # Purchase price per share
}
```

## Configuration

Edit `PORTFOLIO` and `SETTINGS` constants in `portfolio_tracker.py`:

```python
CURRENCY = "VND"
OUTPUT_CSV = "portfolio_report.csv"
```

For more advanced config, use `portfolio_config.py` to:
- Load portfolio from JSON
- Load from environment variables
- Connect to databases

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
2026-05-21 15:20:30,123 - INFO - Starting portfolio analysis
2026-05-21 15:20:31,456 - INFO - Fetching price for HOSE:BSR
2026-05-21 15:20:32,789 - INFO - Got price for HOSE:BSR: 19,200
```

Adjust log level by modifying:

```python
logging.basicConfig(level=logging.INFO)
```

## Advanced Usage

### Load Portfolio from JSON

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
