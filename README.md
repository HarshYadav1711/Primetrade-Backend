# 📈 Crypto Trade Logger

A full-stack trading position tracker built as a take-home assignment for **Primetrade.ai** backend internship. This application demonstrates proficiency in building reliable, scalable APIs with a focus on financial data handling.

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-teal?logo=fastapi)
![React](https://img.shields.io/badge/React-18-blue?logo=react)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue?logo=postgresql)
![Docker](https://img.shields.io/badge/Docker-Compose-blue?logo=docker)

---

## ✨ Features

### Backend
- **JWT Authentication** - Secure user registration and login
- **Trade Management** - CRUD operations for trading positions
- **P&L Calculation** - Automatic profit/loss calculation when closing trades
- **Portfolio Analytics** - Performance metrics and win rate statistics
- **Global Exception Handling** - Consistent, clean error responses
- **User Data Isolation** - Strict separation of user data (tested)

### Frontend
- **Modern UI** - Dark theme optimized for traders
- **Real-time Updates** - Instant feedback on all actions
- **Color-coded Trades** - Green for BUY, Red for SELL
- **Responsive Design** - Works on desktop and mobile

---

## 🛠️ Tech Stack

| Layer | Technology | Rationale |
|-------|------------|-----------|
| **Backend** | Python 3.11 + FastAPI | Async-first framework with automatic OpenAPI docs |
| **Database** | PostgreSQL + SQLAlchemy (Async) | Production-grade RDBMS with non-blocking queries |
| **Frontend** | React 18 + Vite + Tailwind | Fast development build + modern styling |
| **Auth** | JWT (python-jose) + bcrypt | Stateless auth with secure password hashing |
| **Testing** | Pytest + pytest-asyncio | Async test support with isolated fixtures |
| **DevOps** | Docker Compose | One-command deployment |

---

## 🚀 Quick Start

### Option 1: Docker (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd "Primetrade Backend"

# Start all services
docker-compose up --build

# The API will be available at http://localhost:8000
# Swagger docs at http://localhost:8000/docs
```

### Option 2: Manual Setup

#### Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your PostgreSQL connection string

# Run the server
uvicorn app.main:app --reload
```

#### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev

# Open http://localhost:5173
```

---

## 📚 API Documentation

Once the backend is running, access the interactive API docs:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/auth/register` | Create new user account |
| `POST` | `/auth/login` | Authenticate and get JWT token |
| `POST` | `/trades` | Open a new trading position |
| `GET` | `/trades` | List all trades for current user |
| `PATCH` | `/trades/{id}/close` | Close trade with exit price |
| `GET` | `/portfolio/summary` | Get P&L and performance metrics |

---

## 🧪 Running Tests

```bash
cd backend

# Install test dependencies
pip install pytest pytest-asyncio httpx aiosqlite

# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=app
```

### Test Coverage

The test suite includes:
1. **User A cannot see User B's trades** - Data isolation
2. **User A cannot modify User B's trades** - Permission enforcement  
3. **Portfolio summary only includes own trades** - Analytics isolation

---

## 📐 Design Decisions

### Why FastAPI over Flask/Django?

FastAPI was chosen for several reasons aligned with HFT requirements:

1. **Native Async Support**: Essential for high-concurrency trading workloads. While Flask requires greenlet workarounds, FastAPI is async-first.

2. **Automatic OpenAPI Documentation**: Reduces documentation burden and provides interactive testing out-of-the-box.

3. **Pydantic Integration**: Type-safe request/response validation catches errors at the boundary, not in business logic.

4. **Performance**: One of the fastest Python frameworks, approaching Node.js/Go performance levels.

### Why Decimal Instead of Float?

Financial data requires precision. IEEE 754 floating-point arithmetic has well-known issues:

```python
>>> 0.1 + 0.2
0.30000000000000004  # Not 0.3!
```

In trading, these tiny errors compound. A $0.00000001 error per trade across millions of trades becomes significant. We use:

- `Numeric(precision=18, scale=8)` in PostgreSQL
- `Decimal` in Python
- 8 decimal places (matching Bitcoin's satoshi precision)

### Why Not Raw SQL?

SQLAlchemy ORM with async sessions was chosen because:

1. **Type Safety**: Python models provide IDE support and catch errors early
2. **SQL Injection Prevention**: Parameterized queries by default
3. **Relationship Management**: User-Trade relationships handled cleanly
4. **Async Support**: Non-blocking database operations via asyncpg

### Global Exception Handling

Instead of letting errors bubble up as 500 errors with stack traces, we:

1. **Catch all exceptions** at the application level
2. **Return structured JSON** with error codes and messages
3. **Log internally** for debugging while hiding implementation details
4. **Use 404 for authorization failures** (prevents information leakage about resource existence)

---

## 📁 Project Structure

```
Primetrade Backend/
├── backend/
│   ├── app/
│   │   ├── config.py          # Environment configuration
│   │   ├── database.py        # Async SQLAlchemy setup
│   │   ├── dependencies.py    # FastAPI dependencies (auth)
│   │   ├── main.py            # Application entry point
│   │   ├── models/            # SQLAlchemy ORM models
│   │   ├── schemas/           # Pydantic validation schemas
│   │   ├── routers/           # API route handlers
│   │   ├── services/          # Business logic layer
│   │   └── middleware/        # Exception handling
│   ├── tests/                 # Pytest test suite
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/        # Reusable UI components
│   │   ├── pages/             # Page components
│   │   ├── context/           # React context (auth)
│   │   └── services/          # API client
│   ├── package.json
│   └── vite.config.js
├── docker-compose.yml
└── README.md
```

---

## 🔒 Security Considerations

1. **Password Hashing**: bcrypt with automatic salt generation
2. **JWT Tokens**: Signed with HMAC-SHA256, includes expiration
3. **CORS**: Configured for frontend origins only
4. **SQL Injection**: Prevented via SQLAlchemy ORM
5. **Information Leakage**: 404 returned for unauthorized access attempts

---

## 🚀 Scalability & Architecture

This architecture is designed to handle high concurrency - a critical requirement for trading platforms and HFT systems.

### Why This Stack Scales

| Component | Scalability Benefit |
|-----------|---------------------|
| **FastAPI + Async** | Non-blocking I/O allows a single worker to handle thousands of concurrent connections. While one request awaits database response, others are processed. |
| **Asyncpg** | Fully async PostgreSQL driver. No thread blocking during DB operations. Connection pooling reduces overhead. |
| **Stateless JWT** | No server-side session storage. Any server instance can validate tokens. Enables true horizontal scaling. |
| **SQLAlchemy Async** | Async sessions prevent thread exhaustion under load. Prepared statements reduce query parsing overhead. |

### Horizontal Scaling Strategy

```
                    ┌─────────────┐
                    │   Load      │
                    │  Balancer   │
                    └──────┬──────┘
              ┌───────────┼───────────┐
              ▼           ▼           ▼
        ┌─────────┐ ┌─────────┐ ┌─────────┐
        │ API #1  │ │ API #2  │ │ API #3  │
        │ (uvicorn)│ │ (uvicorn)│ │ (uvicorn)│
        └────┬────┘ └────┬────┘ └────┬────┘
             │           │           │
             └───────────┼───────────┘
                         ▼
              ┌─────────────────────┐
              │   PostgreSQL        │
              │  (Connection Pool)  │
              └─────────────────────┘
```

**Key Points:**
1. **Stateless APIs**: JWT tokens eliminate session affinity requirements
2. **Database Pool**: Shared connection pool prevents database saturation
3. **Independent Workers**: Each uvicorn worker handles requests independently
4. **No Shared State**: No Redis/Memcached required for basic operations

### Concurrency in Practice

```python
# Single endpoint can handle 1000+ concurrent requests
# because each await yields to event loop
async def get_trades(db: AsyncSession):
    result = await db.execute(query)  # Non-blocking!
    return result.scalars().all()
```

### Production Recommendations

For high-throughput trading systems, consider:
- **Redis**: For rate limiting and caching hot data
- **Read Replicas**: Separate read/write database connections
- **Kubernetes**: Auto-scaling based on CPU/memory metrics
- **Message Queue**: Async processing for non-critical operations

---

## 🔄 Future Enhancements

If this were a production system, I would add:

1. **Real-time Price Feed**: WebSocket integration for live P&L updates
2. **Rate Limiting**: Prevent API abuse
3. **Audit Logging**: Track all user actions for compliance
4. ~~**API Versioning**: `/v1/trades` for backward compatibility~~ ✅ Implemented
5. **Database Migrations**: Alembic for schema evolution
6. **Caching**: Redis for frequently accessed data
7. **CI/CD**: GitHub Actions for automated testing and deployment

---

## 👤 Author

Built for Primetrade.ai Backend Internship Take-Home Assignment

---

## 📄 License

This project is for demonstration purposes only.
