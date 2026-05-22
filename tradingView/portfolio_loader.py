"""
Portfolio data loader - reads portfolio entries from external text file.

This module handles loading and parsing portfolio data from a text file,
enabling users to edit portfolio data without modifying Python source code.

Format:
    buy_date | symbol | exchange | quantity | buy_price
    
    Example:
        2026-05-25|BSR|HOSE|8|30900
        2026-05-25|DCM|HOSE|5|41900
"""

import logging
from typing import List, Dict, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)


def load_portfolio_from_file(file_path: str) -> List[Dict]:
    """
    Load portfolio data from an external text file.
    
    Reads a pipe-separated file and converts it to a list of portfolio dictionaries.
    Ignores empty lines and comments (lines starting with '#').
    
    Args:
        file_path: Path to the portfolio file
        
    Returns:
        List of dictionaries with keys: buy_date, symbol, exchange, quantity, buy_price
        Empty list if file not found or all lines invalid
        
    Raises:
        Logs errors but does not raise - gracefully handles invalid data
        
    Example:
        >>> portfolio = load_portfolio_from_file("portfolio.txt")
        >>> len(portfolio)
        2
        >>> portfolio[0]['symbol']
        'BSR'
    """
    portfolio = []
    skipped_count = 0
    
    # Check if file exists
    file_path_obj = Path(file_path)
    if not file_path_obj.exists():
        logger.error(f"Portfolio file not found: {file_path}")
        return []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, start=1):
                # Strip whitespace
                line = line.strip()
                
                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue
                
                # Parse the line
                entry = _parse_portfolio_line(line, line_num)
                if entry is None:
                    skipped_count += 1
                    continue
                
                portfolio.append(entry)
        
        # Log summary
        logger.info(f"Portfolio loaded successfully from {file_path}")
        logger.info(f"Loaded {len(portfolio)} portfolio entries")
        
        if skipped_count > 0:
            logger.warning(f"Skipped {skipped_count} invalid entries")
        
        return portfolio
        
    except IOError as e:
        logger.error(f"Error reading portfolio file: {str(e)}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error loading portfolio: {str(e)}")
        return []


def _parse_portfolio_line(line: str, line_num: int) -> Dict | None:
    """
    Parse a single portfolio line.
    
    Args:
        line: A line from the portfolio file (pipe-separated values)
        line_num: Line number (for error reporting)
        
    Returns:
        Portfolio entry dictionary or None if invalid
    """
    fields = line.split('|')
    
    # Validate field count
    if len(fields) != 5:
        logger.warning(
            f"Line {line_num}: Invalid format - expected 5 fields, got {len(fields)}. "
            f"Format: buy_date|symbol|exchange|quantity|buy_price"
        )
        return None
    
    buy_date, symbol, exchange, quantity_str, buy_price_str = [f.strip() for f in fields]
    
    # Validate required fields are not empty
    if not all([buy_date, symbol, exchange, quantity_str, buy_price_str]):
        logger.warning(f"Line {line_num}: Missing required fields")
        return None
    
    # Validate and convert quantity to int
    try:
        quantity = int(quantity_str)
        if quantity <= 0:
            raise ValueError("quantity must be positive")
    except ValueError as e:
        logger.warning(
            f"Line {line_num}: Invalid quantity '{quantity_str}' - {str(e)}"
        )
        return None
    
    # Validate and convert buy_price to float
    try:
        buy_price = float(buy_price_str)
        if buy_price <= 0:
            raise ValueError("buy_price must be positive")
    except ValueError as e:
        logger.warning(
            f"Line {line_num}: Invalid buy_price '{buy_price_str}' - {str(e)}"
        )
        return None
    
    # Return valid entry
    return {
        "buy_date": buy_date,
        "symbol": symbol.upper(),
        "exchange": exchange.upper(),
        "quantity": quantity,
        "buy_price": buy_price
    }


def validate_portfolio(portfolio: List[Dict]) -> Tuple[bool, str]:
    """
    Validate loaded portfolio data for consistency.
    
    Args:
        portfolio: List of portfolio entries
        
    Returns:
        Tuple of (is_valid, message)
    """
    if not portfolio:
        return False, "Portfolio is empty"
    
    # Check for duplicate entries (same symbol, exchange, buy_date)
    seen = set()
    duplicates = []
    
    for entry in portfolio:
        key = (entry['buy_date'], entry['symbol'], entry['exchange'])
        if key in seen:
            duplicates.append(f"{entry['exchange']}:{entry['symbol']} on {entry['buy_date']}")
        seen.add(key)
    
    if duplicates:
        msg = f"Found {len(duplicates)} duplicate entries: {', '.join(duplicates)}"
        logger.warning(msg)
        return True, msg  # Not fatal - portfolio is valid but has duplicates
    
    return True, f"Portfolio valid with {len(portfolio)} entries"
