# Portfolio Data Refactoring Guide

## Overview

The portfolio tracking application has been refactored to externalize portfolio data from Python source code into a dedicated text file (`portfolio.txt`). This change makes the application more flexible and user-friendly.

## What Changed

### Before (Hardcoded)
```python
# In portfolio_tracker.py
PORTFOLIO = [
    {
        "buy_date": "2026-05-25",
        "symbol": "BSR",
        "exchange": "HOSE",
        "quantity": 8,
        "buy_price": 30900
    },
    # ... more entries hardcoded
]
```

### After (Externalized)
```python
# In portfolio_tracker.py
from portfolio_loader import load_portfolio_from_file, validate_portfolio

PORTFOLIO_FILE = "portfolio.txt"
PORTFOLIO = load_portfolio_from_file(PORTFOLIO_FILE)
```

And portfolio data lives in `portfolio.txt`:
```txt
2026-05-25|BSR|HOSE|8|30900
2026-05-25|DCM|HOSE|5|41900
```

## Files Changed

1. **portfolio_loader.py** (NEW)
   - New module containing `load_portfolio_from_file()` function
   - Handles file I/O, parsing, and validation
   - Includes comprehensive error handling and logging

2. **portfolio_tracker.py** (MODIFIED)
   - Imports `load_portfolio_from_file()` from portfolio_loader
   - Replaced hardcoded PORTFOLIO list with dynamic loading
   - Enhanced `main()` function with portfolio validation
   - Existing functionality remains unchanged

3. **portfolio.txt** (NEW)
   - Example portfolio data file
   - Documented with clear instructions
   - Ready for user customization

## Why Externalize Portfolio Data?

### 1. **Separation of Concerns**
   - Data management is separate from business logic
   - Easier to maintain and understand code

### 2. **Non-Technical User Access**
   - Users can edit `portfolio.txt` in any text editor
   - No need to modify Python code
   - Reduces risk of syntax errors in source code

### 3. **Scalability**
   - Easy to switch to different data sources later (CSV, JSON, Database)
   - Code is structured to support multiple loaders

### 4. **Version Control**
   - Portfolio data can be versioned separately from code
   - Users can track portfolio changes independently

### 5. **Team Collaboration**
   - Different team members can manage portfolio without touching code
   - Clear audit trail of portfolio changes

### 6. **Multiple Portfolio Scenarios**
   - Easy to maintain multiple portfolio files for testing
   - Example: `portfolio_test.txt`, `portfolio_backup.txt`

## File Format

### portfolio.txt Structure

```
buy_date | symbol | exchange | quantity | buy_price
```

### Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| buy_date | String (YYYY-MM-DD) | Purchase date | 2026-05-25 |
| symbol | String | Stock ticker symbol | BSR, DCM, VNM |
| exchange | String | Exchange name | HOSE, HNX |
| quantity | Integer (>0) | Number of shares | 8, 5, 100 |
| buy_price | Float (>0) | Price per share | 30900, 41900 |

### Formatting Rules

- **Delimiter**: Pipe character `|`
- **Comments**: Lines starting with `#` are ignored
- **Empty lines**: Ignored
- **Whitespace**: Automatically trimmed from field values
- **Case**: Symbols and exchanges converted to uppercase automatically

### Example Portfolio

```txt
# My Stock Portfolio
# Format: buy_date|symbol|exchange|quantity|buy_price

# Banking stocks
2026-05-25|BSR|HOSE|8|30900
2026-05-25|DCM|HOSE|5|41900

# Tech stocks
2026-04-10|VIC|HOSE|10|26000
```

## Usage

### Running the Application

```bash
python portfolio_tracker.py
```

The application will:
1. Load portfolio from `portfolio.txt`
2. Validate portfolio data
3. Fetch current prices from TradingView
4. Calculate portfolio metrics
5. Display summary and export to CSV

### Editing Your Portfolio

1. Open `portfolio.txt` in your text editor
2. Add or modify entries using the format: `date|symbol|exchange|quantity|price`
3. Save the file
4. Run the portfolio tracker again

### Validation

The loader automatically:
- ✅ Validates file format (5 fields per line)
- ✅ Checks quantity and price are positive numbers
- ✅ Converts data types (quantity→int, price→float)
- ✅ Handles missing or empty values
- ✅ Reports errors with line numbers
- ✅ Detects duplicate entries
- ✅ Logs detailed information

### Error Handling

If there are errors:
1. Check the log messages (printed to console)
2. Look for your symbol in the "skipped" count
3. Verify format matches: `date|symbol|exchange|quantity|price`
4. Ensure no extra spaces around pipes
5. Confirm quantity and price are numbers

Example error:
```
WARNING: Line 5: Invalid quantity '8a' - invalid literal for int()
```

## Function Reference

### load_portfolio_from_file(file_path: str) → List[Dict]

Loads and parses portfolio data from a text file.

**Parameters:**
- `file_path` (str): Path to the portfolio file

**Returns:**
- List of dictionaries with keys: `buy_date`, `symbol`, `exchange`, `quantity`, `buy_price`
- Empty list if file not found or all entries invalid

**Logs:**
- Portfolio loaded successfully (INFO)
- Number of entries loaded (INFO)
- Skipped invalid entries (WARNING)
- Detailed validation errors (WARNING)

### validate_portfolio(portfolio: List[Dict]) → Tuple[bool, str]

Validates portfolio data for consistency.

**Parameters:**
- `portfolio` (List[Dict]): Portfolio entries

**Returns:**
- Tuple of (is_valid, message)
  - `is_valid`: True if portfolio is valid
  - `message`: Validation summary or error description

## Future Improvements

### 1. CSV Support
```python
def load_portfolio_from_csv(file_path: str) -> List[Dict]:
    """Load portfolio from CSV file (comma-separated values)."""
    import csv
    # Implementation
```

### 2. JSON Support
```python
def load_portfolio_from_json(file_path: str) -> List[Dict]:
    """Load portfolio from JSON file (structured data)."""
    import json
    # Implementation
```

### 3. Database Support
```python
def load_portfolio_from_database(connection_string: str) -> List[Dict]:
    """Load portfolio from PostgreSQL/MySQL database."""
    import sqlalchemy
    # Implementation
```

### 4. Google Sheets Integration
```python
def load_portfolio_from_sheets(sheet_id: str, sheet_name: str) -> List[Dict]:
    """Load portfolio from Google Sheets."""
    from google.colab import auth
    # Implementation
```

### 5. Web UI Input Form
```python
# Flask web application for portfolio management
@app.route('/portfolio/add', methods=['POST'])
def add_portfolio_entry():
    """Web form to add portfolio entries."""
    # Implementation
```

### 6. Multiple Portfolio Support
```python
def load_all_portfolios(directory: str) -> Dict[str, List[Dict]]:
    """Load multiple portfolio files from directory."""
    # Implementation
```

### 7. Portfolio History Tracking
```python
def save_portfolio_snapshot(portfolio: List[Dict], timestamp: str) -> None:
    """Save portfolio snapshot for historical analysis."""
    # Implementation
```

### 8. Data Validation Schema
```python
from pydantic import BaseModel

class PortfolioEntry(BaseModel):
    buy_date: str
    symbol: str
    exchange: str
    quantity: int
    buy_price: float
```

## Migration Guide

If you have an existing portfolio in Python code, follow these steps:

### Step 1: Backup
```bash
cp portfolio_tracker.py portfolio_tracker.py.backup
```

### Step 2: Create portfolio.txt
Manually create `portfolio.txt` with your current holdings:
```txt
2026-05-25|BSR|HOSE|8|30900
2026-05-25|DCM|HOSE|5|41900
```

### Step 3: Test
```bash
python portfolio_tracker.py
```

### Step 4: Verify Output
Check that:
- Portfolio loads successfully (no errors)
- Same number of entries as before
- Calculations match previous results

### Step 5: Delete Old Code
Once verified, remove hardcoded PORTFOLIO from portfolio_tracker.py (already done in this refactoring)

## Troubleshooting

### Issue: "Portfolio file not found"
**Solution**: Ensure `portfolio.txt` exists in the same directory as `portfolio_tracker.py`

### Issue: "Invalid format - expected 5 fields"
**Solution**: Check that each line has exactly 5 fields separated by `|` pipes

### Issue: "Invalid quantity" or "Invalid buy_price"
**Solution**: Ensure quantity and price are valid numbers (no letters or special characters)

### Issue: "Portfolio is empty"
**Solution**: Check that `portfolio.txt` has non-comment, non-empty lines with valid data

### Issue: "Missing required fields"
**Solution**: Ensure no empty fields - all 5 fields must have values

## Best Practices

1. **Keep a backup**: Save copies of your portfolio before major edits
2. **Use comments**: Document portfolio sections with `#` comments
3. **Validate regularly**: Check log output for warnings
4. **Version control**: Commit portfolio changes to git
5. **Date format**: Always use YYYY-MM-DD format for dates
6. **Symbols**: Use correct ticker symbols for your exchange
7. **Testing**: Create a test portfolio before applying to main

## Example Portfolios

### Beginner Portfolio
```txt
2026-05-25|VNM|HOSE|5|83000
2026-05-25|VIC|HOSE|3|26000
2026-05-25|HPG|HOSE|10|29000
```

### Diversified Portfolio
```txt
# Banking
2026-05-25|BSR|HOSE|8|30900
2026-05-25|ACB|HOSE|10|25000

# Tech
2026-04-10|FPT|HOSE|5|60000

# Energy
2026-03-15|PVD|HOSE|20|12000

# Consumer
2026-05-20|MWG|HOSE|7|45000
```

### Long-term Holding Portfolio
```txt
2025-01-15|VNM|HOSE|100|80000
2025-02-20|VIC|HOSE|50|25000
2025-03-10|HPG|HOSE|200|27000
```

## Support

For issues or questions:
1. Check the error messages in the log output
2. Review the "Troubleshooting" section above
3. Verify portfolio.txt format against the examples
4. Ensure all required fields are present and valid

## Summary

The refactored portfolio tracking system is now:
- ✅ More flexible and user-friendly
- ✅ Separated from code logic
- ✅ Easier to maintain and extend
- ✅ Ready for future enhancements
- ✅ Production-ready with proper validation

Start using `portfolio.txt` to manage your portfolio!
