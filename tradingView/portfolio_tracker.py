"""
Production-ready portfolio tracker with multiple stock entries support.

Uses TradingView via tvDatafeed to fetch real-time stock prices and
calculates comprehensive portfolio metrics including profit/loss analysis.
"""

import logging
import pandas as pd
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from tvDatafeed import TvDatafeed, Interval
import os

# ============================================================================
# CONSTANTS AND CONFIGURATION
# ============================================================================

CURRENCY = "VND"
OUTPUT_CSV = "portfolio_report.csv"
SEPARATOR = "=" * 50
STOCK_SEPARATOR = "=" * 35

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# ============================================================================
# PORTFOLIO DATA
# ============================================================================

# Define your portfolio here - easy to scale to database later
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
    },
    {
        "buy_date": "2026-03-20",
        "symbol": "VNM",
        "exchange": "HOSE",
        "quantity": 100,
        "buy_price": 87000
    }
]


# ============================================================================
# CORE FUNCTIONS
# ============================================================================

def fetch_stock_price(tv: TvDatafeed, symbol: str, exchange: str) -> Optional[float]:
    """
    Fetch the latest closing price for a stock from TradingView.
    
    Args:
        tv: TvDatafeed instance
        symbol: Stock symbol (e.g., 'BSR')
        exchange: Exchange name (e.g., 'HOSE')
        
    Returns:
        Latest close price or None if fetch fails
    """
    try:
        logger.info(f"Fetching price for {exchange}:{symbol}")
        df = tv.get_hist(
            symbol=symbol,
            exchange=exchange,
            interval=Interval.in_daily,
            n_bars=1
        )
        
        if df is None or df.empty:
            logger.warning(f"No data returned for {exchange}:{symbol}")
            return None
            
        current_price = df['close'].iloc[0]
        logger.info(f"Got price for {exchange}:{symbol}: {current_price:,.0f}")
        return current_price
        
    except Exception as e:
        logger.error(f"Error fetching price for {exchange}:{symbol}: {str(e)}")
        return None


def calculate_position_metrics(
    position: Dict,
    current_price: float
) -> Dict:
    """
    Calculate detailed metrics for a single position.
    
    Args:
        position: Portfolio entry with buy_date, symbol, exchange, quantity, buy_price
        current_price: Current market price
        
    Returns:
        Dictionary with calculated metrics
    """
    buy_price = position["buy_price"]
    quantity = position["quantity"]
    
    # Calculate values
    initial_investment = buy_price * quantity
    current_market_value = current_price * quantity
    profit_loss_amount = current_market_value - initial_investment
    profit_loss_percent = (profit_loss_amount / initial_investment) * 100
    
    return {
        **position,
        "current_price": current_price,
        "initial_investment": initial_investment,
        "current_market_value": current_market_value,
        "profit_loss_amount": profit_loss_amount,
        "profit_loss_percent": profit_loss_percent
    }


def format_number(value: float) -> str:
    """Format number with thousand separators."""
    return f"{value:,.0f}"


def print_position_summary(metrics: Dict) -> None:
    """
    Print a formatted summary for a single stock position.
    
    Args:
        metrics: Dictionary with position metrics
    """
    symbol = metrics["symbol"]
    exchange = metrics["exchange"]
    buy_date = metrics["buy_date"]
    buy_price = metrics["buy_price"]
    current_price = metrics["current_price"]
    quantity = metrics["quantity"]
    initial_investment = metrics["initial_investment"]
    current_market_value = metrics["current_market_value"]
    profit_loss_percent = metrics["profit_loss_percent"]
    profit_loss_amount = metrics["profit_loss_amount"]
    
    # Format profit/loss with sign
    pl_sign = "+" if profit_loss_percent >= 0 else ""
    pl_amount_sign = "+" if profit_loss_amount >= 0 else ""
    
    print("\n" + SEPARATOR)
    print(f"Stock: {exchange}:{symbol}")
    print(STOCK_SEPARATOR)
    print(f"Buy Date:        {buy_date}")
    print(f"Buy Price:       {format_number(buy_price)} {CURRENCY}")
    print(f"Current Price:   {format_number(current_price)} {CURRENCY}")
    print(f"Quantity:        {format_number(quantity)} shares")
    print(f"Investment:      {format_number(initial_investment)} {CURRENCY}")
    print(f"Current Value:   {format_number(current_market_value)} {CURRENCY}")
    print(f"Profit:          {pl_sign}{profit_loss_percent:.2f}%")
    print(f"Profit Amount:   {pl_amount_sign}{format_number(abs(profit_loss_amount))} {CURRENCY}")
    print(STOCK_SEPARATOR)


def calculate_portfolio_summary(positions: List[Dict]) -> Dict:
    """
    Calculate aggregated portfolio metrics.
    
    Args:
        positions: List of calculated position metrics
        
    Returns:
        Dictionary with total portfolio metrics
    """
    total_investment = sum(p["initial_investment"] for p in positions)
    total_current_value = sum(p["current_market_value"] for p in positions)
    total_profit_loss = total_current_value - total_investment
    total_profit_loss_percent = (total_profit_loss / total_investment * 100) if total_investment > 0 else 0
    
    return {
        "total_investment": total_investment,
        "total_current_value": total_current_value,
        "total_profit_loss": total_profit_loss,
        "total_profit_loss_percent": total_profit_loss_percent
    }


def print_portfolio_summary(summary: Dict) -> None:
    """
    Print portfolio-wide summary statistics.
    
    Args:
        summary: Dictionary with portfolio summary metrics
    """
    total_investment = summary["total_investment"]
    total_current_value = summary["total_current_value"]
    total_profit_loss = summary["total_profit_loss"]
    total_profit_loss_percent = summary["total_profit_loss_percent"]
    
    # Format profit/loss with sign
    pl_sign = "+" if total_profit_loss_percent >= 0 else ""
    pl_amount_sign = "+" if total_profit_loss >= 0 else ""
    
    print("\n")
    print(SEPARATOR)
    print("PORTFOLIO SUMMARY".center(50))
    print(SEPARATOR)
    print(f"Total Investment:    {format_number(total_investment)} {CURRENCY}")
    print(f"Total Current Value: {format_number(total_current_value)} {CURRENCY}")
    print(f"Total Profit/Loss:   {pl_amount_sign}{format_number(abs(total_profit_loss))} {CURRENCY}")
    print(f"Total Return:        {pl_sign}{total_profit_loss_percent:.2f}%")
    print(SEPARATOR)


def create_portfolio_dataframe(positions: List[Dict]) -> pd.DataFrame:
    """
    Convert portfolio positions to pandas DataFrame for export.
    
    Args:
        positions: List of calculated position metrics
        
    Returns:
        pandas DataFrame ready for export
    """
    # Select relevant columns for export
    export_data = []
    for pos in positions:
        export_data.append({
            "Buy Date": pos["buy_date"],
            "Symbol": pos["symbol"],
            "Exchange": pos["exchange"],
            "Buy Price": pos["buy_price"],
            "Current Price": pos["current_price"],
            "Quantity": pos["quantity"],
            "Initial Investment": pos["initial_investment"],
            "Current Value": pos["current_market_value"],
            "Profit/Loss Amount": pos["profit_loss_amount"],
            "Profit/Loss %": pos["profit_loss_percent"]
        })
    
    return pd.DataFrame(export_data)


def export_to_csv(df: pd.DataFrame, filename: str = OUTPUT_CSV) -> None:
    """
    Export portfolio report to CSV file.
    
    Args:
        df: Portfolio DataFrame
        filename: Output CSV filename
    """
    try:
        df.to_csv(filename, index=False)
        logger.info(f"Portfolio exported to {filename}")
        print(f"\nReport saved to: {filename}")
    except Exception as e:
        logger.error(f"Error exporting to CSV: {str(e)}")


def process_portfolio(portfolio: List[Dict]) -> Tuple[List[Dict], Dict]:
    """
    Main portfolio processing function. Fetches prices and calculates metrics.
    
    Args:
        portfolio: List of portfolio entries
        
    Returns:
        Tuple of (processed positions list, portfolio summary dict)
    """
    tv = TvDatafeed()
    
    # Cache for API calls - avoid duplicate calls for same symbol
    price_cache = {}
    processed_positions = []
    
    logger.info(f"Processing {len(portfolio)} portfolio entries")
    
    for entry in portfolio:
        symbol = entry["symbol"]
        exchange = entry["exchange"]
        
        # Create cache key
        cache_key = f"{exchange}:{symbol}"
        
        # Fetch price (use cache if available)
        if cache_key not in price_cache:
            current_price = fetch_stock_price(tv, symbol, exchange)
            if current_price is None:
                logger.warning(f"Skipping {cache_key} - failed to fetch price")
                continue
            price_cache[cache_key] = current_price
        else:
            current_price = price_cache[cache_key]
            logger.info(f"Using cached price for {cache_key}: {current_price:,.0f}")
        
        # Calculate metrics
        metrics = calculate_position_metrics(entry, current_price)
        processed_positions.append(metrics)
    
    # Calculate portfolio summary
    if not processed_positions:
        logger.error("No positions processed - exiting")
        return [], {}
    
    portfolio_summary = calculate_portfolio_summary(processed_positions)
    
    return processed_positions, portfolio_summary


def main():
    """Main execution function."""
    logger.info("Starting portfolio analysis")
    
    # Process portfolio
    positions, summary = process_portfolio(PORTFOLIO)
    
    if not positions:
        print("Error: Could not process any portfolio entries.")
        return
    
    # Print individual position summaries
    for metrics in positions:
        print_position_summary(metrics)
    
    # Print portfolio summary
    print_portfolio_summary(summary)
    
    # Create and export DataFrame
    df = create_portfolio_dataframe(positions)
    export_to_csv(df)
    
    logger.info("Portfolio analysis complete")


if __name__ == "__main__":
    main()
