"""
PORTFOLIO TRACKER - SCALING & IMPLEMENTATION GUIDE

Quick reference for extending the system from standalone script to production.
"""

# ============================================================================
# PROJECT STRUCTURE
# ============================================================================

"""
RECOMMENDED DIRECTORY STRUCTURE:

portfolio-tracker/
├── README.md                    # Project overview
├── ARCHITECTURE.md              # Scaling guide (this file)
├── requirements.txt             # Dependencies
├── setup.py                     # Installation script
│
├── core/
│   ├── __init__.py
│   ├── portfolio_tracker.py     # Main logic
│   ├── portfolio_config.py      # Configuration
│   └── constants.py             # Shared constants
│
├── data/
│   ├── __init__.py
│   ├── models.py                # Database models
│   ├── repository.py            # Database access layer
│   └── migrations/              # Database migrations
│       ├── 001_init_schema.sql
│       └── 002_add_user_table.sql
│
├── api/
│   ├── __init__.py
│   ├── app.py                   # FastAPI application
│   ├── routes/
│   │   ├── portfolio.py
│   │   ├── stocks.py
│   │   └── users.py
│   └── middleware.py            # Auth, logging, etc.
│
├── services/
│   ├── __init__.py
│   ├── price_service.py         # TradingView integration
│   ├── notification_service.py  # Email/Telegram
│   ├── cache_service.py         # Redis
│   └── alert_service.py         # Alert logic
│
├── jobs/
│   ├── __init__.py
│   ├── scheduler.py             # APScheduler setup
│   └── tasks.py                 # Celery tasks
│
├── tests/
│   ├── __init__.py
│   ├── test_portfolio_tracker.py
│   ├── test_api.py
│   └── conftest.py              # Pytest fixtures
│
├── config/
│   ├── __init__.py
│   ├── development.py
│   ├── production.py
│   └── settings.py
│
├── scripts/
│   ├── init_db.py               # Initialize database
│   ├── run_scheduler.py         # Start background jobs
│   └── export_data.py           # Data export utilities
│
├── docker/
│   ├── Dockerfile               # API container
│   ├── Dockerfile.worker        # Worker container
│   └── docker-compose.yml       # Full stack
│
└── docs/
    ├── API.md                   # API documentation
    ├── DEPLOYMENT.md            # Deployment guide
    └── TROUBLESHOOTING.md       # Common issues
"""


# ============================================================================
# STEP 1: LOCAL DEVELOPMENT SETUP
# ============================================================================

"""
1. Clone repository
git clone https://github.com/yourusername/portfolio-tracker.git
cd portfolio-tracker

2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

3. Install dependencies
pip install -r requirements.txt

4. Create .env file
PORTFOLIO_JSON_FILE=portfolio.json
DATABASE_URL=sqlite:///portfolio.db
REDIS_URL=redis://localhost:6379
LOG_LEVEL=INFO

5. Run tests
pytest -v

6. Run locally
python core/portfolio_tracker.py

Output should be:
✓ Portfolio analysis complete
✓ Report saved to portfolio_report.csv
"""


# ============================================================================
# STEP 2: ADD DATABASE PERSISTENCE (SQLite → PostgreSQL)
# ============================================================================

"""
PHASE: Week 1

SQLite First (Development):
────────────────────────────
from sqlalchemy import create_engine
from data.models import Base

# Create database
engine = create_engine('sqlite:///portfolio.db')
Base.metadata.create_all(engine)

Migrate to PostgreSQL (Production):
───────────────────────────────────
# Install PostgreSQL
brew install postgresql  # macOS
sudo apt install postgresql  # Linux
docker run -d postgres:15  # Docker

# Update connection string
DATABASE_URL=postgresql://user:password@localhost/portfolio_db

# Run migrations
alembic upgrade head

MIGRATION EXAMPLE (alembic):
───────────────────────────
# Create migration
alembic revision --autogenerate -m "Create portfolio table"

# Apply migration
alembic upgrade head

# Rollback if needed
alembic downgrade -1
"""


# ============================================================================
# STEP 3: ADD CACHING LAYER
# ============================================================================

"""
PHASE: Week 1-2

Benefits:
- Reduce TradingView API calls by 80%
- Faster price lookups (1ms vs 1000ms)
- Better reliability during API downtime

Implementation:
───────────────

1. Install Redis
docker run -d -p 6379:6379 redis:latest

2. Add to requirements.txt
redis>=4.5.0

3. Update portfolio_tracker.py:

from services.cache_service import RedisPriceCache

cache = RedisPriceCache(ttl_seconds=300)

# In process_portfolio():
price = cache.get_price(symbol, exchange)
if not price:
    price = fetch_stock_price(tv, symbol, exchange)
    cache.set_price(symbol, exchange, price)

Cache hit rate: Should reach 70%+ after 1 hour
"""


# ============================================================================
# STEP 4: BUILD REST API
# ============================================================================

"""
PHASE: Week 2-3

Framework: FastAPI (modern, fast, auto-docs)

Installation:
pip install fastapi uvicorn

Create api/app.py:
──────────────────

from fastapi import FastAPI
from api.routes import portfolio, stocks

app = FastAPI(title="Portfolio Tracker")

app.include_router(portfolio.router)
app.include_router(stocks.router)

@app.get("/health")
def health_check():
    return {"status": "healthy"}

API ENDPOINTS:
──────────────
GET    /portfolio/{user_id}         → Fetch portfolio
POST   /portfolio/add               → Add entry
GET    /stock/{symbol}              → Get stock price
GET    /portfolio/{user_id}/history → Historical data
POST   /portfolio/{user_id}/export  → Export CSV
WebSocket /ws/portfolio/{user_id}   → Real-time updates

Run API:
───────
uvicorn api.app:app --reload --host 0.0.0.0 --port 8000

Auto-docs: http://localhost:8000/docs
"""


# ============================================================================
# STEP 5: ADD BACKGROUND JOBS
# ============================================================================

"""
PHASE: Week 3

Options:
A. APScheduler - Simple, in-process (good for small deployments)
B. Celery + RabbitMQ - Distributed, scalable (production-grade)

SIMPLE APPROACH (APScheduler):
──────────────────────────────

from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()

@scheduler.scheduled_job('cron', hour=9, minute=0)
def daily_refresh():
    refresh_all_portfolios()

scheduler.start()

PRODUCTION APPROACH (Celery):
──────────────────────────────

from celery import Celery

app = Celery('portfolio_tracker')
app.config_from_object('celeryconfig')

@app.task
def refresh_portfolio(user_id):
    portfolio = load_portfolio(user_id)
    positions, summary = process_portfolio(portfolio)
    save_snapshot(user_id, summary)
    return summary

# Run worker
celery -A tasks worker --loglevel=info

# Schedule periodic tasks
from celery.schedules import crontab

app.conf.beat_schedule = {
    'refresh-portfolio-daily': {
        'task': 'tasks.refresh_portfolio',
        'schedule': crontab(hour=9, minute=0),
    },
}
"""


# ============================================================================
# STEP 6: ADD NOTIFICATIONS
# ============================================================================

"""
PHASE: Week 3-4

Notification Channels:
1. Email - Portfolio reports, alerts
2. Telegram - Real-time price alerts
3. SMS - Critical alerts (optional)
4. Push Notifications - Mobile app

EMAIL SETUP:
────────────

1. Gmail: Enable App Passwords
   https://myaccount.google.com/apppasswords

2. .env configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-app-password

3. Send email
from services.notification_service import EmailNotifier

mailer = EmailNotifier()
mailer.send_portfolio_report(recipient_email, metrics)

TELEGRAM SETUP:
───────────────

1. Create bot with @BotFather
2. Get TOKEN and chat_id
3. .env configuration
TELEGRAM_BOT_TOKEN=123456789:ABCDefGhIjKlMnOpQrStUvWxYz
TELEGRAM_CHAT_ID=987654321

4. Send alert
from services.notification_service import TelegramAlerter

telegram = TelegramAlerter()
telegram.send_portfolio_summary(chat_id, metrics)
"""


# ============================================================================
# STEP 7: DEPLOY TO PRODUCTION
# ============================================================================

"""
PHASE: Week 4-5

OPTION A: Heroku (Easiest)
────────────────────────────

1. Create Heroku account
2. Install Heroku CLI
3. Create Procfile:

web: gunicorn api.app:app
worker: celery -A tasks worker --loglevel=info
beat: celery -A tasks beat --loglevel=info

4. Deploy
heroku create portfolio-tracker
git push heroku main
heroku addons:create heroku-postgresql:premium-0
heroku addons:create heroku-redis:premium-0


OPTION B: Docker + AWS
────────────────────────

1. Create Docker images
docker build -t portfolio-tracker:latest .
docker build -f docker/Dockerfile.worker -t portfolio-worker:latest .

2. Push to ECR
docker tag portfolio-tracker:latest 123456789.dkr.ecr.us-east-1.amazonaws.com/portfolio:latest
docker push 123456789.dkr.ecr.us-east-1.amazonaws.com/portfolio:latest

3. Deploy to ECS/EKS
(Use CloudFormation or AWS CLI)


OPTION C: Kubernetes (Most Scalable)
──────────────────────────────────────

Create deployment.yaml:

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
      - name: api
        image: portfolio-tracker:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: portfolio-secrets
              key: database_url
        resources:
          requests:
            cpu: 100m
            memory: 256Mi

kubectl apply -f deployment.yaml
"""


# ============================================================================
# STEP 8: ADD WEBSOCKET REAL-TIME UPDATES
# ============================================================================

"""
PHASE: Month 2

Enables real-time price updates without polling.

from fastapi import WebSocket
import asyncio

@app.websocket("/ws/portfolio/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    await websocket.accept()
    
    while True:
        # Fetch latest prices
        portfolio = db.load_portfolio(user_id)
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

Frontend (JavaScript):
──────────────────────

const ws = new WebSocket('ws://localhost:8000/ws/portfolio/1');

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    updateDashboard(data);
};
"""


# ============================================================================
# STEP 9: MONITORING & ALERTS
# ============================================================================

"""
PHASE: Month 2

Tools: Prometheus + Grafana for monitoring

Key Metrics:
- API response time
- Database query performance
- Cache hit rate
- API error rate
- Price fetch success rate
- User alerts triggered

Setup:
1. Install Prometheus/Grafana
2. Export metrics from FastAPI
3. Create dashboards
4. Configure alerts

Example metrics:

from prometheus_client import Counter, Histogram

portfolio_refreshes = Counter(
    'portfolio_refreshes_total',
    'Total portfolio refreshes'
)

price_fetch_time = Histogram(
    'price_fetch_seconds',
    'Time to fetch stock price'
)
"""


# ============================================================================
# SCALING TIMELINE
# ============================================================================

"""
WEEK 1:
└─ ✓ Local script with multiple portfolios
   ✓ CSV export
   ✓ Error handling & logging
   ✓ SQLite database
   ✓ Redis caching

WEEK 2:
└─ ✓ PostgreSQL migration
   ✓ Basic FastAPI REST API
   ✓ Authentication (JWT)
   ✓ Input validation

WEEK 3:
└─ ✓ Background jobs (APScheduler)
   ✓ Email notifications
   ✓ Telegram alerts
   ✓ Portfolio snapshots/history

WEEK 4:
└─ ✓ Docker containerization
   ✓ docker-compose for local dev
   ✓ Deployment to Heroku/AWS
   ✓ Monitoring setup

MONTH 2:
└─ ✓ WebSocket real-time updates
   ✓ Web dashboard (React)
   ✓ Advanced analytics
   ✓ Multi-user support

MONTH 3+:
└─ ✓ Mobile app (React Native)
   ✓ AI price predictions
   ✓ Advanced portfolio analytics
   ✓ Tax reporting features
"""


# ============================================================================
# COST ESTIMATE (PRODUCTION)
# ============================================================================

"""
SMALL DEPLOYMENT (1-100 users):
────────────────────────────────
- Heroku Dyno (web): $7/month
- Heroku Dyno (worker): $7/month
- PostgreSQL (standard): $50/month
- Redis (premium): $30/month
────────────────────
Total: ~$95/month

MEDIUM DEPLOYMENT (100-1000 users):
──────────────────────────────────
- AWS EC2 (t3.medium x2): $30/month
- RDS PostgreSQL (db.t3.medium): $100/month
- ElastiCache Redis: $50/month
- CloudFront CDN: $20/month
- SNS (notifications): $10/month
────────────────────
Total: ~$210/month

LARGE DEPLOYMENT (1000+ users):
────────────────────────────────
- AWS EKS (Kubernetes cluster): $150/month
- RDS PostgreSQL (db.r5.xlarge): $300/month
- ElastiCache Redis (cache.r5.large): $150/month
- NAT Gateway: $45/month
- Monitoring (CloudWatch): $50/month
────────────────────
Total: ~$695/month +compute

FREE TIER OPTIONS:
- AWS Free Tier (1 year)
- Heroku Free (limited)
- Railway.app (free tier)
- Render.com (free tier)
"""


# ============================================================================
# TESTING STRATEGY
# ============================================================================

"""
Unit Tests:
──────────
pytest tests/test_portfolio_tracker.py

class TestPortfolioCalculations:
    def test_profit_loss_calculation(self):
        metrics = calculate_position_metrics(
            {"buy_price": 100, "quantity": 10},
            current_price=110
        )
        assert metrics['profit_loss_percent'] == 10.0

Integration Tests:
──────────────────
pytest tests/test_api.py

def test_get_portfolio_endpoint(client):
    response = client.get("/portfolio/1")
    assert response.status_code == 200
    assert "total_investment" in response.json()

Load Tests:
───────────
# Use locust for load testing
locust -f tests/locustfile.py --host=http://localhost:8000

CI/CD Pipeline (GitHub Actions):
────────────────────────────────
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - run: pip install -r requirements.txt
      - run: pytest
      - run: pytest --cov
"""


# ============================================================================
# TROUBLESHOOTING COMMON ISSUES
# ============================================================================

"""
Issue: TradingView returns no data
───────────────────────────────────
Causes:
- Invalid symbol or exchange
- TradingView rate limiting
- Network connectivity issues

Solutions:
1. Verify symbol (use HOSE, HNX, UPCOM)
2. Add retry logic with exponential backoff
3. Check internet connection
4. Use API key when available

from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
def fetch_stock_price(tv, symbol, exchange):
    # Fetch logic


Issue: Database migrations fail
────────────────────────────────
Solutions:
1. Reset database: alembic downgrade base
2. Check migrations folder exists
3. Verify database connection
4. Check for conflicting migrations


Issue: Redis connection errors
────────────────────────────────
Solutions:
1. Verify Redis is running: redis-cli ping
2. Check host/port configuration
3. Check firewall rules
4. Monitor Redis memory: redis-cli info memory


Issue: API timeouts
──────────────────
Solutions:
1. Add timeout configuration
2. Implement request queueing
3. Scale horizontally (add more instances)
4. Optimize database queries
5. Enable response caching
"""


# ============================================================================
# RESOURCES & REFERENCES
# ============================================================================

"""
DOCUMENTATION:
- FastAPI: https://fastapi.tiangolo.com
- SQLAlchemy: https://docs.sqlalchemy.org
- APScheduler: https://apscheduler.readthedocs.io
- tvDatafeed: https://github.com/rongardF/tvdatafeed
- Docker: https://docs.docker.com
- Kubernetes: https://kubernetes.io/docs

TUTORIALS:
- FastAPI + SQLAlchemy: https://...
- Docker for Python: https://...
- PostgreSQL Setup: https://...

TOOLS:
- Postman: API testing
- pgAdmin: PostgreSQL management
- Redisinsight: Redis visualization
- Datadog: Monitoring
- Sentry: Error tracking
"""
