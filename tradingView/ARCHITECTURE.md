"""
Extended Portfolio Tracker - Production Architecture & Scaling Guide

This module demonstrates how to scale the portfolio tracker from standalone
script to a production system with database, API, real-time updates, and web UI.

REFACTORING UPDATE (Latest):
- Portfolio data now externalized to portfolio.txt
- New portfolio_loader.py module handles file I/O and validation
- No code changes needed to add/remove stocks
- Type-safe, with comprehensive error handling
"""

# ============================================================================
# ARCHITECTURE LAYERS
# ============================================================================

"""
CURRENT STATE (portfolio_tracker.py with portfolio_loader.py):
├── Data Input: Portfolio file (portfolio.txt)
├── Data Loading: portfolio_loader.py (validation & parsing)
├── Price Fetching: TvDatafeed API calls
├── Calculations: Portfolio metrics
├── Output: Console + CSV file

SCALABLE ARCHITECTURE:
┌─────────────────────────────────────────────────────────────────┐
│                         WEB UI LAYER                             │
│  (Dashboard, Real-time charts, Mobile app)                      │
├─────────────────────────────────────────────────────────────────┤
│                         API LAYER (FastAPI/Flask)               │
│  (/portfolio, /stocks, /metrics, /alerts)                       │
├─────────────────────────────────────────────────────────────────┤
│                     BUSINESS LOGIC LAYER                         │
│  (Calculations, Strategies, Portfolio Analysis)                 │
├─────────────────────────────────────────────────────────────────┤
│                         DATA LAYER                               │
│  ┌──────────────┬──────────────┬──────────────────────┐         │
│  │  PostgreSQL  │  Redis Cache │  Message Queue       │         │
│  │  (Portfolio) │  (Prices)    │  (RabbitMQ/Kafka)    │         │
│  └──────────────┴──────────────┴──────────────────────┘         │
├─────────────────────────────────────────────────────────────────┤
│                  DATA LOADING & VALIDATION                       │
│  ┌──────────────┬──────────────┬──────────────────────┐         │
│  │portfolio.txt │  portfolio   │   Data Loader        │         │
│  │(User data)   │ _loader.py   │  (Parsing & Validation)        │
│  └──────────────┴──────────────┴──────────────────────┘         │
├─────────────────────────────────────────────────────────────────┤
│                    EXTERNAL DATA SOURCES                         │
│  ┌──────────────┬──────────────┬──────────────────────┐         │
│  │ TradingView  │  Alpha Vantage  │  WebSocket Feeds  │         │
│  │ (tvDatafeed) │  (Stock data)   │  (Real-time)      │         │
│  └──────────────┴──────────────┴──────────────────────┘         │
└─────────────────────────────────────────────────────────────────┘
"""


# ============================================================================
# LAYER 1: DATABASE PERSISTENCE
# ============================================================================

# Option A: SQLite (Development/Small deployments)
"""
Easy setup, no external dependencies, file-based.
Good for: Local use, testing, small portfolios.
"""

SQLITE_SCHEMA = """
CREATE TABLE IF NOT EXISTS portfolio (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    symbol VARCHAR(10) NOT NULL,
    exchange VARCHAR(10) NOT NULL,
    quantity REAL NOT NULL,
    buy_price REAL NOT NULL,
    buy_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, symbol, buy_date)
);

CREATE TABLE IF NOT EXISTS price_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol VARCHAR(10) NOT NULL,
    exchange VARCHAR(10) NOT NULL,
    price REAL NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    source VARCHAR(50),
    INDEX(symbol, exchange, timestamp)
);

CREATE TABLE IF NOT EXISTS portfolio_snapshot (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    total_investment REAL NOT NULL,
    total_value REAL NOT NULL,
    total_profit_loss REAL NOT NULL,
    total_return_percent REAL NOT NULL,
    snapshot_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""


# Option B: PostgreSQL (Production recommended)
"""
Robust, scalable, multi-user, enterprise features.
Good for: Production deployments, multiple users, heavy load.
"""

POSTGRES_SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS portfolio_entries (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    symbol VARCHAR(10) NOT NULL,
    exchange VARCHAR(10) NOT NULL,
    quantity DECIMAL(15, 6) NOT NULL,
    buy_price DECIMAL(15, 2) NOT NULL,
    buy_date DATE NOT NULL,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, symbol, buy_date)
);

CREATE TABLE IF NOT EXISTS stock_prices (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    exchange VARCHAR(10) NOT NULL,
    price DECIMAL(15, 2) NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    source VARCHAR(50),
    UNIQUE(symbol, exchange, timestamp)
);

CREATE TABLE IF NOT EXISTS portfolio_snapshots (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    total_investment DECIMAL(18, 2) NOT NULL,
    total_current_value DECIMAL(18, 2) NOT NULL,
    total_profit_loss DECIMAL(18, 2) NOT NULL,
    total_return_percent DECIMAL(10, 4) NOT NULL,
    snapshot_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_portfolio_user ON portfolio_entries(user_id);
CREATE INDEX idx_stock_prices_lookup ON stock_prices(symbol, exchange, timestamp DESC);
CREATE INDEX idx_snapshots_user_date ON portfolio_snapshots(user_id, snapshot_date DESC);
"""


def example_postgres_integration():
    """Example: Load portfolio from PostgreSQL"""
    import psycopg2
    from psycopg2.extras import RealDictCursor
    
    conn = psycopg2.connect(
        dbname="portfolio_db",
        user="portfolio_user",
        password="secure_password",
        host="localhost",
        port=5432
    )
    
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("""
            SELECT symbol, exchange, quantity, buy_price, buy_date
            FROM portfolio_entries
            WHERE user_id = %s
            ORDER BY buy_date DESC
        """, (user_id,))
        
        portfolio = [dict(row) for row in cur.fetchall()]
    
    conn.close()
    return portfolio


def example_sqlite_integration():
    """Example: Load portfolio from SQLite"""
    import sqlite3
    
    conn = sqlite3.connect("portfolio.db")
    conn.row_factory = sqlite3.Row
    
    cursor = conn.cursor()
    cursor.execute("""
        SELECT symbol, exchange, quantity, buy_price, buy_date
        FROM portfolio
        WHERE user_id = ?
        ORDER BY buy_date DESC
    """, (user_id,))
    
    portfolio = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return portfolio


# ============================================================================
# LAYER 2: CACHING LAYER (Redis)
# ============================================================================

"""
Redis cache prevents hammering TradingView API with same requests.
Automatic expiration keeps data fresh while reducing API calls.
"""

def example_redis_caching():
    """Example: Use Redis for price caching"""
    import redis
    
    cache = redis.Redis(host='localhost', port=6379, db=0)
    
    def get_stock_price(symbol, exchange):
        # Try cache first
        cache_key = f"price:{exchange}:{symbol}"
        cached_price = cache.get(cache_key)
        
        if cached_price:
            print(f"Cache hit for {symbol}")
            return float(cached_price)
        
        # Fetch from TradingView if not cached
        from portfolio_tracker import fetch_stock_price
        from tvDatafeed import TvDatafeed
        
        tv = TvDatafeed()
        price = fetch_stock_price(tv, symbol, exchange)
        
        # Cache for 5 minutes
        if price:
            cache.setex(cache_key, 300, price)
        
        return price


# ============================================================================
# LAYER 3: MESSAGE QUEUE (Background Jobs)
# ============================================================================

"""
Use Celery + RabbitMQ to process portfolio updates in background.
Allows API to respond instantly without waiting for price fetches.
"""

def example_celery_tasks():
    """Example: Celery tasks for async portfolio processing"""
    from celery import Celery
    
    app = Celery('portfolio_tracker')
    app.config_from_object('celeryconfig')
    
    @app.task
    def refresh_portfolio(user_id):
        """Background task: refresh portfolio prices and metrics"""
        portfolio = load_portfolio_from_db(user_id)
        positions, summary = process_portfolio(portfolio)
        
        # Save snapshot to database
        save_portfolio_snapshot(user_id, summary)
        
        return {
            'status': 'success',
            'user_id': user_id,
            'positions': len(positions),
            'total_return': summary['total_profit_loss_percent']
        }
    
    @app.task
    def send_alert(user_id, alert_type, message):
        """Background task: send email/SMS alerts"""
        send_email(user_id, alert_type, message)


# ============================================================================
# LAYER 4: REAL-TIME UPDATES (WebSocket)
# ============================================================================

"""
WebSocket enables live price updates pushing to clients.
Eliminates polling, reduces network traffic.
"""

def example_websocket_server():
    """Example: Real-time price updates with WebSocket"""
    from fastapi import FastAPI, WebSocket
    import asyncio
    
    app = FastAPI()
    
    @app.websocket("/ws/portfolio/{user_id}")
    async def websocket_endpoint(websocket: WebSocket, user_id: int):
        await websocket.accept()
        
        while True:
            # Fetch latest prices
            portfolio = load_portfolio_from_db(user_id)
            positions, summary = process_portfolio(portfolio)
            
            # Send to client
            await websocket.send_json({
                'type': 'portfolio_update',
                'timestamp': datetime.now().isoformat(),
                'positions': positions,
                'summary': summary
            })
            
            # Update every 60 seconds
            await asyncio.sleep(60)


# ============================================================================
# LAYER 5: REST API (FastAPI)
# ============================================================================

"""
Modern, fast REST API with automatic documentation.
"""

def example_fastapi_app():
    """Example: Complete FastAPI portfolio application"""
    from fastapi import FastAPI, HTTPException, Depends
    from fastapi.responses import JSONResponse
    from pydantic import BaseModel
    from datetime import datetime
    
    app = FastAPI(
        title="Portfolio Tracker API",
        description="Professional stock portfolio tracking API",
        version="1.0.0"
    )
    
    # ===== Models =====
    
    class PortfolioEntry(BaseModel):
        symbol: str
        exchange: str
        quantity: float
        buy_price: float
        buy_date: str
    
    class PortfolioResponse(BaseModel):
        total_investment: float
        total_current_value: float
        total_profit_loss: float
        total_return_percent: float
        positions: list
    
    # ===== Endpoints =====
    
    @app.get("/portfolio/{user_id}", response_model=PortfolioResponse)
    async def get_portfolio(user_id: int):
        """Fetch full portfolio with current metrics"""
        portfolio = load_portfolio_from_db(user_id)
        positions, summary = process_portfolio(portfolio)
        
        return {
            **summary,
            'positions': positions
        }
    
    @app.post("/portfolio/add")
    async def add_to_portfolio(user_id: int, entry: PortfolioEntry):
        """Add new entry to portfolio"""
        entry_dict = entry.dict()
        save_portfolio_entry(user_id, entry_dict)
        
        return {
            'status': 'success',
            'message': f"Added {entry.quantity} shares of {entry.symbol}"
        }
    
    @app.get("/stock/{symbol}")
    async def get_stock_price(symbol: str, exchange: str = "HOSE"):
        """Get current price for a stock"""
        price = get_cached_price(symbol, exchange)
        
        if not price:
            raise HTTPException(status_code=404, detail="Stock not found")
        
        return {
            'symbol': symbol,
            'exchange': exchange,
            'price': price,
            'timestamp': datetime.now().isoformat()
        }
    
    @app.get("/portfolio/{user_id}/history")
    async def get_portfolio_history(user_id: int, days: int = 30):
        """Get portfolio value history"""
        snapshots = load_portfolio_snapshots(user_id, days)
        
        return {
            'period_days': days,
            'snapshots': snapshots
        }
    
    @app.post("/portfolio/{user_id}/export")
    async def export_portfolio(user_id: int, format: str = "csv"):
        """Export portfolio to CSV or Excel"""
        portfolio = load_portfolio_from_db(user_id)
        df = create_portfolio_dataframe([...])
        
        if format == "csv":
            return df.to_csv(index=False)
        elif format == "excel":
            return df.to_excel(index=False)


# ============================================================================
# LAYER 6: SCHEDULING (APScheduler)
# ============================================================================

"""
Automatic portfolio refresh on schedule.
"""

def example_scheduled_refresh():
    """Example: Schedule portfolio refresh"""
    from apscheduler.schedulers.background import BackgroundScheduler
    
    scheduler = BackgroundScheduler()
    
    # Refresh all portfolios daily at 9 AM
    scheduler.add_job(
        func=refresh_all_portfolios,
        trigger='cron',
        hour=9,
        minute=0,
        id='daily_portfolio_refresh'
    )
    
    # Send alerts for thresholds
    scheduler.add_job(
        func=check_alerts,
        trigger='interval',
        minutes=15,
        id='check_alerts'
    )
    
    scheduler.start()


# ============================================================================
# LAYER 7: MONITORING & ALERTING
# ============================================================================

"""
Monitor system health and alert users.
"""

def example_alerting_system():
    """Example: Alert system for profit/loss thresholds"""
    
    class AlertThreshold:
        def __init__(self, user_id, trigger_type, value):
            self.user_id = user_id
            self.trigger_type = trigger_type  # 'profit_percent', 'loss_amount'
            self.value = value
    
    def check_alerts(user_id):
        """Check if any alerts should be triggered"""
        portfolio = load_portfolio_from_db(user_id)
        positions, summary = process_portfolio(portfolio)
        
        # Load user's alert thresholds
        thresholds = load_user_thresholds(user_id)
        
        for threshold in thresholds:
            if threshold.trigger_type == 'profit_percent':
                if summary['total_profit_loss_percent'] >= threshold.value:
                    send_alert(
                        user_id,
                        'success',
                        f"Portfolio profit reached {threshold.value}%!"
                    )
            
            elif threshold.trigger_type == 'loss_amount':
                if summary['total_profit_loss'] <= -threshold.value:
                    send_alert(
                        user_id,
                        'warning',
                        f"Portfolio loss exceeded {threshold.value}!"
                    )


# ============================================================================
# DEPLOYMENT EXAMPLES
# ============================================================================

"""
DOCKER DEPLOYMENT:

docker-compose.yml
==================
version: '3.8'
services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: portfolio_db
      POSTGRES_USER: portfolio_user
      POSTGRES_PASSWORD: secure_password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7
    ports:
      - "6379:6379"

  api:
    build: .
    command: uvicorn api:app --host 0.0.0.0 --port 8000
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - redis
    environment:
      DATABASE_URL: postgresql://portfolio_user:secure_password@postgres:5432/portfolio_db
      REDIS_URL: redis://redis:6379

  celery_worker:
    build: .
    command: celery -A tasks worker --loglevel=info
    depends_on:
      - postgres
      - redis

volumes:
  postgres_data:


KUBERNETES DEPLOYMENT:

deployment.yaml
===============
apiVersion: apps/v1
kind: Deployment
metadata:
  name: portfolio-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: portfolio-api
  template:
    metadata:
      labels:
        app: portfolio-api
    spec:
      containers:
      - name: portfolio-api
        image: portfolio-tracker:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: portfolio-secrets
              key: database_url
        - name: REDIS_URL
          value: redis://redis-service:6379
        resources:
          requests:
            cpu: 100m
            memory: 256Mi
          limits:
            cpu: 500m
            memory: 512Mi
"""


# ============================================================================
# MIGRATION PATH
# ============================================================================

"""
START HERE:
1. portfolio_tracker.py - Single-threaded, CLI
   (Current state - works great for personal use)

PHASE 1 (Week 1):
2. Add portfolio_config.py - Load from JSON/YAML
3. Add SQLite persistence
4. Add logging to file

PHASE 2 (Week 2-3):
5. Switch to PostgreSQL
6. Add Redis caching
7. Create simple Flask/FastAPI REST API

PHASE 3 (Week 4):
8. Add WebSocket real-time updates
9. Implement Celery background tasks
10. Deploy to Docker

PHASE 4 (Ongoing):
11. Add web dashboard (React/Vue)
12. Mobile app (React Native/Flutter)
13. Advanced analytics
14. Machine learning models
"""
