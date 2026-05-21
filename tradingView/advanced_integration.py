"""
Advanced Examples: Integration Patterns & Production Use Cases

Demonstrates how to integrate portfolio tracker with:
- PostgreSQL database
- Redis cache
- Email notifications
- Telegram alerts
- Scheduled jobs
- REST API
"""

# ============================================================================
# EXAMPLE 1: POSTGRESQL INTEGRATION
# ============================================================================

"""
Installation:
pip install psycopg2-binary sqlalchemy
"""

class PostgresPortfolioRepository:
    """Database abstraction layer for portfolio operations"""
    
    def __init__(self, connection_string: str):
        from sqlalchemy import create_engine
        self.engine = create_engine(connection_string)
    
    def load_portfolio(self, user_id: int) -> list:
        """Load portfolio entries from database"""
        from sqlalchemy import text
        
        with self.engine.connect() as conn:
            result = conn.execute(text("""
                SELECT symbol, exchange, quantity, buy_price, buy_date
                FROM portfolio_entries
                WHERE user_id = :user_id
                ORDER BY buy_date DESC
            """), {"user_id": user_id})
            
            return [dict(row._mapping) for row in result]
    
    def save_snapshot(self, user_id: int, metrics: dict) -> None:
        """Save portfolio metrics snapshot"""
        from sqlalchemy import text
        from datetime import datetime
        
        with self.engine.connect() as conn:
            conn.execute(text("""
                INSERT INTO portfolio_snapshots
                (user_id, total_investment, total_current_value, 
                 total_profit_loss, total_return_percent, snapshot_date)
                VALUES
                (:user_id, :total_investment, :total_current_value,
                 :total_profit_loss, :total_return_percent, :snapshot_date)
            """), {
                "user_id": user_id,
                "total_investment": metrics["total_investment"],
                "total_current_value": metrics["total_current_value"],
                "total_profit_loss": metrics["total_profit_loss"],
                "total_return_percent": metrics["total_profit_loss_percent"],
                "snapshot_date": datetime.now()
            })
            conn.commit()
    
    def add_entry(self, user_id: int, entry: dict) -> None:
        """Add new portfolio entry"""
        from sqlalchemy import text
        
        with self.engine.connect() as conn:
            conn.execute(text("""
                INSERT INTO portfolio_entries
                (user_id, symbol, exchange, quantity, buy_price, buy_date)
                VALUES
                (:user_id, :symbol, :exchange, :quantity, :buy_price, :buy_date)
            """), {
                "user_id": user_id,
                **entry
            })
            conn.commit()


# ============================================================================
# EXAMPLE 2: REDIS CACHING
# ============================================================================

"""
Installation:
pip install redis

Start Redis:
docker run -d -p 6379:6379 redis:latest
"""

class RedisPriceCache:
    """Redis-based price caching to reduce API calls"""
    
    def __init__(self, host='localhost', port=6379, ttl_seconds=300):
        import redis
        self.redis = redis.Redis(host=host, port=port, decode_responses=True)
        self.ttl = ttl_seconds
    
    def get_price(self, symbol: str, exchange: str) -> float:
        """Get cached price or fetch fresh"""
        key = f"price:{exchange}:{symbol}"
        cached = self.redis.get(key)
        
        if cached:
            return float(cached)
        return None
    
    def set_price(self, symbol: str, exchange: str, price: float) -> None:
        """Cache price for TTL seconds"""
        key = f"price:{exchange}:{symbol}"
        self.redis.setex(key, self.ttl, str(price))
    
    def flush_all(self) -> None:
        """Clear all cached prices"""
        self.redis.flushdb()


def fetch_stock_price_cached(cache: RedisPriceCache, tv, symbol: str, exchange: str):
    """Enhanced fetch with caching"""
    from portfolio_tracker import fetch_stock_price
    import logging
    
    logger = logging.getLogger(__name__)
    
    # Try cache first
    cached_price = cache.get_price(symbol, exchange)
    if cached_price:
        logger.info(f"Cache HIT for {exchange}:{symbol} = {cached_price}")
        return cached_price
    
    # Fetch fresh
    price = fetch_stock_price(tv, symbol, exchange)
    
    # Update cache
    if price:
        cache.set_price(symbol, exchange, price)
        logger.info(f"Cache MISS - fetched and cached {exchange}:{symbol}")
    
    return price


# ============================================================================
# EXAMPLE 3: EMAIL NOTIFICATIONS
# ============================================================================

"""
Installation:
pip install python-dotenv

Create .env file:
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-app-password
"""

class EmailNotifier:
    """Send portfolio notifications via email"""
    
    def __init__(self):
        import os
        from dotenv import load_dotenv
        
        load_dotenv()
        self.smtp_server = os.getenv('SMTP_SERVER')
        self.smtp_port = int(os.getenv('SMTP_PORT'))
        self.sender_email = os.getenv('SENDER_EMAIL')
        self.sender_password = os.getenv('SENDER_PASSWORD')
    
    def send_portfolio_report(self, recipient_email: str, metrics: dict) -> None:
        """Send portfolio summary email"""
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        
        subject = "Portfolio Daily Report"
        
        body = f"""
        Daily Portfolio Report
        
        Total Investment:     {metrics['total_investment']:,.0f} VND
        Current Value:        {metrics['total_current_value']:,.0f} VND
        Profit/Loss:          {metrics['total_profit_loss']:+,.0f} VND
        Return:               {metrics['total_profit_loss_percent']:+.2f}%
        
        Generated: {__import__('datetime').datetime.now().isoformat()}
        """
        
        msg = MIMEMultipart()
        msg['From'] = self.sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        
        with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
            server.starttls()
            server.login(self.sender_email, self.sender_password)
            server.send_message(msg)


# ============================================================================
# EXAMPLE 4: TELEGRAM ALERTS
# ============================================================================

"""
Installation:
pip install python-telegram-bot

Setup:
1. Create bot: @BotFather on Telegram
2. Get TOKEN from BotFather
3. Store in .env: TELEGRAM_BOT_TOKEN=...
"""

class TelegramAlerter:
    """Send portfolio alerts via Telegram"""
    
    def __init__(self):
        import os
        from dotenv import load_dotenv
        
        load_dotenv()
        self.token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.base_url = f"https://api.telegram.org/bot{self.token}"
    
    def send_alert(self, chat_id: int, message: str) -> None:
        """Send alert message"""
        import requests
        
        url = f"{self.base_url}/sendMessage"
        
        params = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "HTML"
        }
        
        response = requests.post(url, params=params)
        response.raise_for_status()
    
    def send_portfolio_summary(self, chat_id: int, metrics: dict) -> None:
        """Send formatted portfolio summary"""
        total_pl = metrics['total_profit_loss']
        total_pl_pct = metrics['total_profit_loss_percent']
        
        emoji = "📈" if total_pl >= 0 else "📉"
        
        message = f"""
<b>{emoji} Portfolio Update</b>

<b>Investment:</b> {metrics['total_investment']:,.0f} VND
<b>Current Value:</b> {metrics['total_current_value']:,.0f} VND
<b>Profit/Loss:</b> <b>{total_pl:+,.0f}</b> VND
<b>Return:</b> <b>{total_pl_pct:+.2f}%</b>

<i>Last update: {__import__('datetime').datetime.now().strftime('%H:%M:%S')}</i>
        """
        
        self.send_alert(chat_id, message)


# ============================================================================
# EXAMPLE 5: SCHEDULED REFRESH WITH APScheduler
# ============================================================================

"""
Installation:
pip install apscheduler

Usage:
app = PortfolioScheduler(db_connection)
app.start()

The scheduler will:
- Refresh portfolio daily at 9 AM
- Send alerts every 15 minutes
- Clean up old snapshots weekly
"""

class PortfolioScheduler:
    """Manage scheduled portfolio tasks"""
    
    def __init__(self, db_connection: str):
        from apscheduler.schedulers.background import BackgroundScheduler
        
        self.scheduler = BackgroundScheduler()
        self.db = PostgresPortfolioRepository(db_connection)
    
    def start(self):
        """Start all scheduled jobs"""
        
        # Daily portfolio refresh
        self.scheduler.add_job(
            func=self._refresh_all_portfolios,
            trigger='cron',
            hour=9,
            minute=0,
            id='daily_refresh',
            name='Daily Portfolio Refresh'
        )
        
        # Alert checks every 15 minutes
        self.scheduler.add_job(
            func=self._check_alerts,
            trigger='interval',
            minutes=15,
            id='alert_check',
            name='Check Alerts'
        )
        
        # Weekly cleanup
        self.scheduler.add_job(
            func=self._cleanup_old_snapshots,
            trigger='cron',
            day_of_week='mon',
            hour=2,
            minute=0,
            id='weekly_cleanup',
            name='Cleanup Old Snapshots'
        )
        
        self.scheduler.start()
    
    def _refresh_all_portfolios(self):
        """Refresh all user portfolios"""
        from portfolio_tracker import process_portfolio
        import logging
        
        logger = logging.getLogger(__name__)
        
        # Get all user IDs
        user_ids = self.db.get_all_user_ids()
        
        for user_id in user_ids:
            try:
                portfolio = self.db.load_portfolio(user_id)
                positions, summary = process_portfolio(portfolio)
                self.db.save_snapshot(user_id, summary)
                logger.info(f"Refreshed portfolio for user {user_id}")
            except Exception as e:
                logger.error(f"Error refreshing portfolio for user {user_id}: {e}")
    
    def _check_alerts(self):
        """Check if any alerts should be triggered"""
        logger = logging.getLogger(__name__)
        logger.info("Checking user alerts...")
        # Implementation would check thresholds
    
    def _cleanup_old_snapshots(self):
        """Remove snapshots older than 90 days"""
        logger = logging.getLogger(__name__)
        logger.info("Cleaning up old snapshots...")
        # Implementation would delete old data


# ============================================================================
# EXAMPLE 6: FULL WORKFLOW
# ============================================================================

def example_production_workflow():
    """Complete production workflow example"""
    
    # Initialize components
    db = PostgresPortfolioRepository(
        "postgresql://user:password@localhost/portfolio_db"
    )
    cache = RedisPriceCache(ttl_seconds=300)
    mailer = EmailNotifier()
    telegram = TelegramAlerter()
    scheduler = PortfolioScheduler("postgresql://user:password@localhost/portfolio_db")
    
    # Start scheduler
    scheduler.start()
    
    # Load and process portfolio
    user_id = 1
    portfolio = db.load_portfolio(user_id)
    
    # Get prices with caching
    tv = __import__('tvDatafeed').TvDatafeed()
    
    for entry in portfolio:
        price = fetch_stock_price_cached(
            cache, tv, entry['symbol'], entry['exchange']
        )
        entry['current_price'] = price
    
    # Calculate metrics
    from portfolio_tracker import (
        process_portfolio, calculate_portfolio_summary
    )
    
    positions, metrics = process_portfolio(portfolio)
    portfolio_metrics = calculate_portfolio_summary(positions)
    
    # Save snapshot
    db.save_snapshot(user_id, portfolio_metrics)
    
    # Send notifications
    mailer.send_portfolio_report(
        "user@example.com",
        portfolio_metrics
    )
    
    telegram.send_portfolio_summary(12345678, portfolio_metrics)
    
    print("Workflow complete!")


if __name__ == "__main__":
    example_production_workflow()
