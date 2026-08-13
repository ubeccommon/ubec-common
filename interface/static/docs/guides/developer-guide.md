# UBEC DAO Protocol Suite Developer Onboarding Guide

**Version:** 1.0  
**Last Updated:** November 2, 2025  
**Target Audience:** Core Developers, Integration Developers, Protocol Research Developers

> *"As we learn to think like a plant, we discover that technology and nature are not opposites but complementary expressions of the same creative forces that shape our world."*

---

## Table of Contents

1. [Welcome to UBEC](#welcome-to-ubec)
2. [Prerequisites & Environment Setup](#prerequisites--environment-setup)
3. [System Architecture Overview](#system-architecture-overview)
4. [The 12 Design Principles](#the-12-design-principles)
5. [Developer Tracks](#developer-tracks)
   - [Track 1: Core Development](#track-1-core-development)
   - [Track 2: Integration Development](#track-2-integration-development)
   - [Track 3: Protocol Research](#track-3-protocol-research)
6. [Practical Exercises](#practical-exercises)
7. [Common Patterns & Anti-Patterns](#common-patterns--anti-patterns)
8. [Resources & Support](#resources--support)

---

## Welcome to UBEC

### What is UBEC?

The **Ubuntu Bioregional Economic Commons (UBEC) Protocol Suite** is a sophisticated blockchain-based economic platform built on the Stellar network that implements Ubuntu philosophical principles through a four-element token ecosystem.

### The Four Elements

Each token represents a fundamental aspect of economic cooperation:

| Element | Token | Principle | Purpose |
|---------|-------|-----------|---------|
| ðŸŒ¬ï¸ **Air** | UBEC | Diversity | Gateway access and network diversity |
| ðŸ’§ **Water** | UBECrc | Reciprocity | Flow of value and mutual exchange |
| ðŸŒ **Earth** | UBECgpi | Mutualism | Stability and collective prosperity |
| ðŸ”¥ **Fire** | UBECtt | Regeneration | Transformation and renewal |

### Project Philosophy

**Ubuntu:** "I am because we are" - The system emphasizes interconnectedness, community-centered approaches, and bioregional harmony.

**Precision:** Coding is an exact science. This system focuses exclusively on what it can ACTUALLY execute, not theoretical best-case scenarios.

**Nature-Inspired Design:** The architecture mirrors natural systems - holonic (whole/part) relationships, emergent behaviors, and regenerative patterns.

---

## Prerequisites & Environment Setup

### Required Knowledge

#### For All Developers:
- **Python 3.11+** proficiency
- **Async/await** patterns and asyncio
- **PostgreSQL** fundamentals
- **Git** version control
- Understanding of **service-oriented architecture**

#### Additional for Core Developers:
- Database schema design
- API rate limiting and circuit breakers
- Service registry patterns
- Dependency injection

#### Additional for Integration Developers:
- **Stellar blockchain** fundamentals
- RESTful API design
- Transaction modeling
- Cryptographic operations

#### Additional for Protocol Research:
- **Ubuntu philosophy** and principles
- Economic systems design
- Network analysis
- Data science and visualization

### Development Environment Setup

#### 1. System Requirements

```bash
# Operating System
Ubuntu 24.04 LTS (recommended) or compatible Linux distribution

# Python Version
Python 3.11 or higher

# Database
PostgreSQL 15.13 or higher
```

#### 2. Repository Setup

```bash
# Clone the repository
git clone [repository-url]
cd ubec-protocol-suite

# Create and activate virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --break-system-packages \
    stellar-sdk \
    asyncpg \
    aiohttp \
    matplotlib \
    numpy \
    pandas \
    pytest-asyncio
```

#### 3. Database Configuration

```bash
# Connect to PostgreSQL
psql -U postgres

# Create database and schema
CREATE DATABASE ubec;
\c ubec
CREATE SCHEMA ubec_main;

# Run schema initialization
psql -U postgres -d ubec -f database/schema/ubec_main_schema.sql
```

#### 4. Configuration Setup

```bash
# Copy environment template
cp .env.example .env

# Edit with your credentials
nano .env
```

Required environment variables:
```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/ubec
DATABASE_SCHEMA=ubec_main

# Stellar Network
STELLAR_NETWORK=mainnet  # or testnet for development
STELLAR_HORIZON_URL=https://horizon.stellar.org

# Service Configuration
LOG_LEVEL=INFO
RATE_LIMIT_REQUESTS=3000
RATE_LIMIT_PERIOD=3600
```

#### 5. Verify Installation

```bash
# Run health check
python main.py health --log-level=DEBUG

# Expected output:
# âœ“ Database connection successful
# âœ“ All 14 services initialized
# âœ“ Service registry operational
# âœ“ Stellar client connected
```

### Development Tools

#### Recommended IDE Setup

**VS Code Extensions:**
- Python
- Pylance
- PostgreSQL
- GitLens
- Markdown All in One

**PyCharm Configuration:**
- Enable async/await syntax highlighting
- Configure Python interpreter to use project venv
- Set up database tools for PostgreSQL

#### Debugging Setup

```python
# Add to launch.json (VS Code)
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "UBEC Main",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/main.py",
            "console": "integratedTerminal",
            "args": ["health", "--log-level=DEBUG"]
        }
    ]
}
```

---

## System Architecture Overview

### High-Level Architecture

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚                         main.py                              â”‚
â”‚                   (Sole Orchestrator)                        â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                         â”‚
                         â–¼
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚                   Service Registry                           â”‚
â”‚           (Dependency Injection Container)                   â”‚
â””â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
   â”‚                  â”‚                  â”‚
   â–¼                  â–¼                  â–¼
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”    â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”      â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚Infrastructureâ”‚ â”‚ Protocol â”‚      â”‚Operationalâ”‚
â”‚  Services    â”‚ â”‚ Services â”‚      â”‚ Services  â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜    â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜      â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

### Directory Structure

```
ubec-protocol-suite/
â”œâ”€â”€ main.py                    # Sole entry point (ONLY executable)
â”‚
â”œâ”€â”€ core/                      # Infrastructure layer
â”‚   â”œâ”€â”€ service_registry.py    # Central dependency management
â”‚   â”œâ”€â”€ database_manager.py    # Async DB connection pool
â”‚   â”œâ”€â”€ config_manager.py      # Database-backed configuration
â”‚   â””â”€â”€ health_checks.py       # Service health monitoring
â”‚
â”œâ”€â”€ services/                  # Operational services
â”‚   â”œâ”€â”€ stellar/
â”‚   â”‚   â”œâ”€â”€ stellar_client_service.py
â”‚   â”‚   â””â”€â”€ rate_limiter_service.py
â”‚   â”œâ”€â”€ data/
â”‚   â”‚   â””â”€â”€ synchronizer_service.py
â”‚   â”œâ”€â”€ analytics/
â”‚   â”‚   â”œâ”€â”€ analytics_service.py
â”‚   â”‚   â””â”€â”€ holonic_evaluator_service.py
â”‚   â”œâ”€â”€ distribution/
â”‚   â”‚   â”œâ”€â”€ distribution_manager_service.py
â”‚   â”‚   â””â”€â”€ distribution_evaluator_service.py
â”‚   â””â”€â”€ audit/
â”‚       â””â”€â”€ audit_service.py
â”‚
â”œâ”€â”€ protocols/                 # Element protocols
â”‚   â”œâ”€â”€ air_protocol.py        # Gateway & Diversity
â”‚   â”œâ”€â”€ water_protocol.py      # Flow & Reciprocity
â”‚   â”œâ”€â”€ earth_protocol.py      # Distribution & Mutualism
â”‚   â””â”€â”€ fire_protocol.py       # Transformation & Regeneration
â”‚
â”œâ”€â”€ visualization/             # Charts and reports
â”‚   â””â”€â”€ holonic_visualizer.py
â”‚
â”œâ”€â”€ database/                  # Database artifacts
â”‚   â”œâ”€â”€ schema/
â”‚   â”‚   â””â”€â”€ ubec_main_schema.sql
â”‚   â””â”€â”€ migrations/
â”‚
â”œâ”€â”€ tests/                     # Test suite
â”‚   â”œâ”€â”€ unit/
â”‚   â”œâ”€â”€ integration/
â”‚   â””â”€â”€ conftest.py
â”‚
â””â”€â”€ docs/                      # Documentation
    â”œâ”€â”€ api/
    â”œâ”€â”€ architecture/
    â””â”€â”€ deployment/
```

### Key Architectural Patterns

#### 1. Single Orchestrator Pattern
- **Only** `main.py` has execution permissions
- All other files are importable services
- No standalone script execution

#### 2. Service Registry Pattern
- Central registry (`ServiceRegistry`) manages all dependencies
- Services registered once, instantiated lazily
- Automatic dependency resolution via topological sorting
- Health monitoring built into every service

#### 3. Async-First Design
- **100% async operations** - no blocking calls
- All I/O operations use `async/await`
- Concurrent operations leveraged throughout
- No sync fallbacks or compatibility layers

#### 4. Database as Single Source of Truth
- PostgreSQL is authoritative for all data
- No configuration files (config in `ubec_config_settings` table)
- Zero data duplication across modules
- Query-first approach for all data access

### Service Dependency Graph

```
database â”€â”€â”€â”€â”
             â”‚
config â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€ stellar_client â”€â”¬â”€â”€â”€ synchronizer
             â”‚                     â”‚
             â”‚                     â”œâ”€â”€â”€ analytics
             â”‚                     â”‚
             â”‚                     â””â”€â”€â”€ distribution_manager
             â”‚
             â”œâ”€â”€â”€ air_protocol
             â”œâ”€â”€â”€ water_protocol
             â”œâ”€â”€â”€ earth_protocol
             â””â”€â”€â”€ fire_protocol
                       â”‚
                       â””â”€â”€â”€ holonic_evaluator â”€â”€â”€ visualizer
```

### The 14 Registered Services

| Service | Purpose | Dependencies |
|---------|---------|--------------|
| `database` | PostgreSQL connection pool | None |
| `config` | Configuration management | database |
| `stellar_client` | Stellar network API client | database, config |
| `air` | Air element protocol | database, stellar_client |
| `water` | Water element protocol | database, stellar_client |
| `earth` | Earth element protocol | database, stellar_client |
| `fire` | Fire element protocol | database, stellar_client |
| `synchronizer` | Blockchain data sync | database, stellar_client |
| `analytics` | Token analytics | database |
| `distribution` | Balance management | database, analytics |
| `distribution_evaluator` | Compliance checking | database, distribution |
| `holonic_evaluator` | Ubuntu assessment | database, analytics |
| `visualizer` | Charts and reports | database, holonic_evaluator |
| `audit` | Audit logging | database |

### Data Flow Example

```python
# User requests account evaluation
main.py (orchestrator)
    â†“
service_registry.get('holonic_evaluator')
    â†“
holonic_evaluator.evaluate_account(account_id)
    â†“
â”œâ”€â†’ database.query() â†’ PostgreSQL (ubec_holonic_metrics)
â”œâ”€â†’ analytics.get_transaction_patterns()
â”œâ”€â†’ stellar_client.get_account_operations()
â””â”€â†’ visualizer.generate_radar_chart()
    â†“
Returns: HolonicEvaluation with visualization
```

---

## The 12 Design Principles

Every line of code in UBEC must comply with these 12 principles. Understanding them is **critical** for all developers.

### Principle #1: Modular Design and Architecture

**What:** Each module operates as a self-contained holon with clear boundaries.

**Why:** Enables independent development, testing, and deployment. Reduces coupling and increases maintainability.

**How:**
```python
# âœ… GOOD: Clear module boundary
class AirProtocol:
    """Air element protocol - handles gateway and diversity tracking."""
    
    def __init__(self, database, stellar_client):
        self._db = database
        self._stellar = stellar_client
    
    async def check_trustline(self, account_id: str) -> bool:
        """Check if account has trustline to UBEC."""
        # Implementation isolated to this module
        pass

# âŒ BAD: Tight coupling
class AirProtocol:
    def __init__(self):
        # Directly importing and creating dependencies
        from core.database_manager import DatabaseManager
        self._db = DatabaseManager()  # Tight coupling!
```

**Checkpoint:** Can this module be tested in complete isolation?

---

### Principle #2: Service Pattern with Centralized Execution

**What:** All modules implement the service pattern. Only `main.py` executes code.

**Why:** Single point of control, predictable initialization order, clean startup/shutdown.

**How:**
```python
# âœ… GOOD: Service pattern
# In water_protocol.py
class WaterProtocol:
    """Service class with no execution code."""
    
    async def initialize(self):
        """Called by service registry during startup."""
        pass

# In main.py (ONLY place with execution)
async def main():
    registry = ServiceRegistry()
    await registry.initialize_all()
    water = await registry.get('water')
    await water.track_flow()

# âŒ BAD: Standalone execution
# In water_protocol.py
if __name__ == '__main__':
    # NEVER do this - violates principle #2
    protocol = WaterProtocol()
    asyncio.run(protocol.track_flow())
```

**Checkpoint:** Does your module have any `if __name__ == '__main__':` blocks?

---

### Principle #3: Service Registry for Dependencies

**What:** All inter-module dependencies managed through central registry.

**Why:** Enables dependency injection, loose coupling, and dynamic service discovery.

**How:**
```python
# âœ… GOOD: Registry-based dependency injection
async def create_holonic_evaluator(registry: ServiceRegistry):
    """Factory function for service creation."""
    database = await registry.get('database')
    analytics = await registry.get('analytics')
    return HolonicEvaluator(database, analytics)

# Register in main.py
registry.register_factory(
    'holonic_evaluator',
    create_holonic_evaluator,
    dependencies=['database', 'analytics']
)

# âŒ BAD: Direct imports
from services.analytics import AnalyticsService  # Direct import - tight coupling!
analytics = AnalyticsService()  # Breaks dependency injection!
```

**Checkpoint:** Are all dependencies declared in the service registry?

---

### Principle #4: Single Source of Truth

**What:** Database serves as the authoritative data source. Each piece of information has exactly one canonical location.

**Why:** Eliminates data inconsistency, simplifies debugging, ensures data integrity.

**How:**
```python
# âœ… GOOD: Database as single source of truth
async def get_token_balance(self, account_id: str, token_code: str) -> Decimal:
    """Always query the database for current balance."""
    query = """
        SELECT balance FROM ubec_main.ubec_balances
        WHERE account_id = $1 AND token_code = $2
    """
    return await self._db.fetchval(query, account_id, token_code)

# âŒ BAD: In-memory cache without database backing
class BalanceManager:
    def __init__(self):
        self._cache = {}  # Cached data not backed by database!
    
    def get_balance(self, account_id):
        return self._cache.get(account_id, 0)  # Where did this come from?
```

**Configuration Example:**
```python
# âœ… GOOD: Configuration in database
async def get_config(self, key: str) -> Any:
    """Fetch from ubec_config_settings table."""
    query = "SELECT value FROM ubec_main.ubec_config_settings WHERE key = $1"
    return await self._db.fetchval(query, key)

# âŒ BAD: Configuration in code or files
CONFIG = {
    'rate_limit': 3000,  # Hard-coded configuration!
    'timeout': 30
}
```

**Checkpoint:** Can you point to the single location in the database where this data is stored?

---

### Principle #5: Strict Async Operations

**What:** ALL I/O operations must use async/await patterns. No blocking operations.

**Why:** Maximizes concurrency, prevents blocking the event loop, enables efficient resource utilization.

**How:**
```python
# âœ… GOOD: Async operation
async def fetch_account_data(self, account_id: str) -> dict:
    """Async operation using await."""
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{self.horizon_url}/accounts/{account_id}") as response:
            return await response.json()

# âœ… GOOD: Multiple concurrent operations
async def fetch_multiple_accounts(self, account_ids: List[str]) -> List[dict]:
    """Leverage concurrency for efficiency."""
    tasks = [self.fetch_account_data(account_id) for account_id in account_ids]
    return await asyncio.gather(*tasks)

# âŒ BAD: Blocking operation
def fetch_account_data(self, account_id: str) -> dict:
    """Synchronous operation - BLOCKS event loop!"""
    response = requests.get(f"{self.horizon_url}/accounts/{account_id}")  # BLOCKING!
    return response.json()

# âŒ BAD: Async function with blocking call
async def fetch_account_data(self, account_id: str) -> dict:
    """Async wrapper around blocking code is still blocking!"""
    return requests.get(url).json()  # Still blocks!
```

**Checkpoint:** Does your code have any blocking I/O operations? (File I/O, network calls, database queries)

---

### Principle #6: No Sync Fallbacks or Backward Compatibility

**What:** Clean, forward-looking codebase only. No legacy support code.

**Why:** Reduces code complexity, eliminates technical debt, maintains architectural purity.

**How:**
```python
# âœ… GOOD: Pure async implementation
async def initialize(self):
    """Pure async initialization."""
    await self._db.connect()
    await self._load_configuration()

# âŒ BAD: Sync fallback
async def initialize(self):
    """With sync fallback - NEVER do this."""
    try:
        await self._db.connect()
    except Exception:
        # Fallback to sync connection
        self._db.connect_sync()  # Violates principle!

# âŒ BAD: Compatibility layer
async def get_balance(self, account_id: str) -> Decimal:
    """With legacy support - NEVER do this."""
    if self._legacy_mode:  # Legacy support adds complexity!
        return self._get_balance_v1(account_id)
    return await self._get_balance_v2(account_id)
```

**Checkpoint:** Is there any code that maintains backward compatibility or sync fallbacks?

---

### Principle #7: Per-Asset Monitoring with Execution Minimums

**What:** Individual asset tracking and limits. Minimum thresholds for execution.

**Why:** Prevents micro-transactions, ensures meaningful operations, optimizes resource usage.

**How:**
```python
# âœ… GOOD: Per-asset monitoring with minimums
async def should_execute_distribution(self, account_id: str, token_code: str) -> bool:
    """Check if distribution amount exceeds minimum threshold."""
    balance = await self.get_balance(account_id, token_code)
    minimum = await self.get_minimum_threshold(token_code)
    
    if balance < minimum:
        logger.info(f"Balance {balance} below minimum {minimum} for {token_code}")
        return False
    
    return True

# Configuration in database
"""
INSERT INTO ubec_config_settings (key, value) VALUES
    ('minimum_ubec_distribution', '10.0000000'),
    ('minimum_ubecrc_distribution', '5.0000000'),
    ('minimum_ubecgpi_distribution', '20.0000000'),
    ('minimum_ubectt_distribution', '1.0000000');
"""

# âŒ BAD: No minimum checking
async def execute_distribution(self, account_id: str, amount: Decimal):
    """Executes even for 0.0000001 tokens - wasteful!"""
    await self.send_payment(account_id, amount)
```

**Checkpoint:** Are there minimum execution thresholds for each asset?

---

### Principle #8: No Duplicate Configuration

**What:** Each configuration parameter defined exactly once.

**Why:** Eliminates inconsistencies, simplifies updates, reduces bugs.

**How:**
```python
# âœ… GOOD: Single configuration source
async def get_rate_limit(self) -> int:
    """Fetch from database - single source of truth."""
    query = "SELECT value FROM ubec_config_settings WHERE key = 'rate_limit'"
    return int(await self._db.fetchval(query))

# Usage throughout system
async def make_request(self):
    limit = await self._config.get_rate_limit()  # Always fetch from DB
    await self._rate_limiter.acquire(limit)

# âŒ BAD: Duplicate configuration
# In stellar_client.py
RATE_LIMIT = 3000  # Hard-coded!

# In rate_limiter.py
DEFAULT_RATE_LIMIT = 3000  # Duplicate!

# In config.json
{"rate_limit": 3000}  # Triple definition!
```

**Checkpoint:** Is each configuration parameter defined in exactly one place?

---

### Principle #9: Integrated Rate Limiting

**What:** Built-in rate limiting for all external API calls.

**Why:** Prevents service abuse, ensures compliance with provider limits, graceful degradation.

**How:**
```python
# âœ… GOOD: Integrated rate limiter
class StellarClientService:
    def __init__(self, rate_limiter):
        self._rate_limiter = rate_limiter
    
    async def fetch_account(self, account_id: str) -> dict:
        """All external calls go through rate limiter."""
        await self._rate_limiter.acquire()  # Wait for rate limit slot
        
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.horizon_url}/accounts/{account_id}") as response:
                return await response.json()

# Rate limiter implementation
class RateLimiter:
    def __init__(self, max_requests: int, period: int):
        """E.g., 3000 requests per 3600 seconds."""
        self._max_requests = max_requests
        self._period = period
        self._semaphore = asyncio.Semaphore(max_requests)
        self._request_times = []
    
    async def acquire(self):
        """Acquire rate limit slot, waiting if necessary."""
        async with self._semaphore:
            # Cleanup old requests outside the window
            now = time.time()
            self._request_times = [t for t in self._request_times if now - t < self._period]
            
            if len(self._request_times) >= self._max_requests:
                # Wait until oldest request expires
                wait_time = self._period - (now - self._request_times[0])
                await asyncio.sleep(wait_time)
            
            self._request_times.append(time.time())

# âŒ BAD: No rate limiting
async def fetch_account(self, account_id: str) -> dict:
    """Direct API call with no rate limiting - will hit limits!"""
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()
```

**Checkpoint:** Are all external API calls protected by rate limiting?

---

### Principle #10: Clear Separation of Concerns

**What:** Active processing separated from passive monitoring. Business logic isolated from infrastructure.

**Why:** Improves testability, simplifies debugging, enables independent scaling.

**How:**
```python
# âœ… GOOD: Clear separation
# Data access layer (services/data/)
class DataSynchronizer:
    """Handles data synchronization only."""
    async def sync_transactions(self, account_id: str):
        """Fetch and store transactions - no business logic."""
        transactions = await self._stellar.get_transactions(account_id)
        await self._db.insert_transactions(transactions)

# Business logic layer (protocols/)
class WaterProtocol:
    """Implements reciprocity business logic."""
    async def evaluate_reciprocity(self, account_id: str) -> float:
        """Pure business logic - no I/O operations."""
        transactions = await self._db.get_transactions(account_id)
        return self._calculate_reciprocity_score(transactions)
    
    def _calculate_reciprocity_score(self, transactions: List[dict]) -> float:
        """Pure calculation - no I/O."""
        # Business logic here
        pass

# âŒ BAD: Mixed concerns
class WaterProtocol:
    async def evaluate_reciprocity(self, account_id: str) -> float:
        """Mixing data access with business logic."""
        # Data access mixed with business logic!
        transactions = await self._stellar.get_transactions(account_id)
        await self._db.insert_transactions(transactions)
        score = sum([t['amount'] for t in transactions]) / len(transactions)
        return score
```

**Checkpoint:** Can you clearly identify the data access, business logic, and presentation layers?

---

### Principle #11: Comprehensive Documentation

**What:** Docstrings at top of every file, inline comments for complex logic, API documentation.

**Why:** Enables team collaboration, reduces onboarding time, improves maintainability.

**How:**
```python
# âœ… GOOD: Comprehensive documentation
"""
UBEC Holonic Evaluator Service - Production Version 2.0
========================================================
Evaluates accounts against Ubuntu principles and generates holonic metrics.

Design Principles Compliance:
â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    âœ… #1  Modular Design: Clear boundaries and interfaces
    âœ… #2  Service Pattern: No standalone execution
    âœ… #3  Service Registry: Dependencies injected via registry
    âœ… #4  Single Source of Truth: Database-backed evaluations
    âœ… #5  Strict Async: Full async/await throughout
    âœ… #6  No Sync Fallbacks: Pure async implementation
    âœ… #7  Per-Asset Monitoring: Per-principle evaluation
    âœ… #8  No Duplicate Configuration: Single config source
    âœ… #9  Integrated Rate Limiting: N/A (no external APIs)
    âœ… #10 Separation of Concerns: Business logic only
    âœ… #11 Comprehensive Documentation: This docstring
    âœ… #12 Method Singularity: Each method implemented once
â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

Dependencies:
    - database: For querying transaction and balance data
    - analytics: For computing network-wide statistics

Usage Example:
    >>> evaluator = await registry.get('holonic_evaluator')
    >>> result = await evaluator.evaluate_account('GABC123...')
    >>> print(f"Ubuntu Score: {result.total_score}")

Attribution:
    This project uses the services of Claude and Anthropic PBC to inform our 
    decisions and recommendations. This project was made possible with the 
    assistance of Claude and Anthropic PBC.
"""

class HolonicEvaluator:
    """
    Evaluates accounts against the five Ubuntu principles.
    
    Principles Evaluated:
        1. Autonomy-Integration: Balance between independence and collaboration
        2. Ubuntu Alignment: Adherence to "I am because we are"
        3. Reciprocity Health: Mutual exchange patterns
        4. Mutualism Capacity: Collective benefit generation
        5. Regeneration Impact: Contribution to ecosystem renewal
    
    Attributes:
        _db: Database manager instance
        _analytics: Analytics service instance
        _cache: Temporary evaluation cache (session-only, not persisted)
    """
    
    async def evaluate_account(
        self, 
        account_id: str,
        include_visualization: bool = False
    ) -> HolonicEvaluation:
        """
        Evaluate an account across all Ubuntu principles.
        
        This method orchestrates the complete evaluation process:
        1. Fetch account transaction history
        2. Calculate scores for each principle
        3. Generate aggregate Ubuntu score
        4. Optionally create visualization
        5. Store results in database
        
        Args:
            account_id: Stellar account ID (56-character public key)
            include_visualization: Whether to generate radar chart
        
        Returns:
            HolonicEvaluation: Complete evaluation with scores and metadata
        
        Raises:
            ValueError: If account_id is invalid format
            DatabaseError: If database query fails
            
        Example:
            >>> result = await evaluator.evaluate_account(
            ...     'GABC123...',
            ...     include_visualization=True
            ... )
            >>> print(f"Reciprocity: {result.reciprocity_score:.2f}")
        """
        # Implementation here

# âŒ BAD: Minimal documentation
class HolonicEvaluator:
    def evaluate_account(self, account_id):
        # Calculate score
        return score
```

**Attribution Block (Required in ALL files):**
```python
"""
Attribution:
    This project uses the services of Claude and Anthropic PBC to inform our 
    decisions and recommendations. This project was made possible with the 
    assistance of Claude and Anthropic PBC.
"""
```

**Checkpoint:** Does every file have a comprehensive docstring? Are all public methods documented?

---

### Principle #12: Method Singularity (No Redundancy)

**What:** Each method implemented exactly once in the entire codebase. Zero code duplication.

**Why:** Eliminates maintenance burden, ensures consistency, reduces bugs.

**How:**
```python
# âœ… GOOD: Method singularity with shared utilities
# In core/utils.py
async def validate_stellar_account(account_id: str) -> bool:
    """Validate Stellar account format - implemented ONCE."""
    import re
    pattern = r'^G[A-Z2-7]{55}$'
    return bool(re.match(pattern, account_id))

# Used throughout system
# In air_protocol.py
from core.utils import validate_stellar_account

async def check_trustline(self, account_id: str) -> bool:
    if not await validate_stellar_account(account_id):
        raise ValueError(f"Invalid account ID: {account_id}")
    # ... rest of implementation

# In water_protocol.py
from core.utils import validate_stellar_account

async def track_flow(self, account_id: str):
    if not await validate_stellar_account(account_id):
        raise ValueError(f"Invalid account ID: {account_id}")
    # ... rest of implementation

# âŒ BAD: Method duplication
# In air_protocol.py
async def check_trustline(self, account_id: str) -> bool:
    # Duplicated validation logic!
    import re
    if not re.match(r'^G[A-Z2-7]{55}$', account_id):
        raise ValueError(f"Invalid account ID")
    # ...

# In water_protocol.py
async def track_flow(self, account_id: str):
    # Duplicated validation logic AGAIN!
    import re
    if not re.match(r'^G[A-Z2-7]{55}$', account_id):
        raise ValueError(f"Invalid account ID")
    # ...
```

**Pattern: Shared Utilities Module**
```python
# core/utils.py - Central location for shared functionality
"""Shared utility functions used across the system."""

async def validate_stellar_account(account_id: str) -> bool:
    """Validate Stellar account ID format."""
    pass

async def parse_stellar_amount(amount: str) -> Decimal:
    """Parse Stellar amount string to Decimal."""
    pass

async def format_balance(balance: Decimal, decimals: int = 7) -> str:
    """Format balance with proper decimal places."""
    pass

def calculate_percentage(part: Decimal, whole: Decimal) -> float:
    """Calculate percentage with division by zero protection."""
    pass
```

**Checkpoint:** Can you find this exact code anywhere else in the codebase?

---

## Developer Tracks

Choose your track based on your primary responsibilities. All developers should complete the **Common Foundation** first.

### Common Foundation (All Developers)

#### Week 1: System Familiarization

**Day 1-2: Environment Setup**
- [ ] Complete [Prerequisites & Environment Setup](#prerequisites--environment-setup)
- [ ] Run `python main.py health` successfully
- [ ] Connect to PostgreSQL and explore `ubec_main` schema
- [ ] Review directory structure and understand file organization

**Day 3-4: Architecture Deep Dive**
- [ ] Read [System Architecture Overview](#system-architecture-overview)
- [ ] Study the service registry (`core/service_registry.py`)
- [ ] Trace initialization flow in `main.py`
- [ ] Map out the 14 services and their dependencies

**Day 5: Design Principles**
- [ ] Study all [12 Design Principles](#the-12-design-principles)
- [ ] For each principle, identify 3 examples in the codebase
- [ ] Complete the principle compliance checklist
- [ ] Review anti-patterns section

**Exercise 1: Service Registry Exploration**
```python
# Run this in Python REPL after starting system
import asyncio
from core.service_registry import ServiceRegistry

async def explore_registry():
    registry = ServiceRegistry()
    await registry.initialize_all()
    
    # Print all services
    info = registry.get_info()
    print(f"Total services: {info['total_services']}")
    print(f"Initialization order: {' â†’ '.join(info['initialization_order'])}")
    
    # Get and explore a service
    holonic = await registry.get('holonic_evaluator')
    print(f"Holonic evaluator type: {type(holonic)}")
    
    # Check health
    health = await registry.check_health()
    for service, status in health.items():
        print(f"{service}: {status['status']}")

asyncio.run(explore_registry())
```

**Expected Output:**
```
Total services: 14
Initialization order: database â†’ config â†’ stellar_client â†’ ...
Holonic evaluator type: <class 'services.analytics.HolonicEvaluator'>
database: healthy
config: healthy
stellar_client: healthy
...
```

**Checkpoint Questions:**
1. Why can't modules execute independently?
2. How does the service registry resolve circular dependencies?
3. What happens if a service fails to initialize?
4. Where is configuration stored, and why?

---

### Track 1: Core Development

**Focus:** Infrastructure, service architecture, database management, and core system operations.

#### Week 2-3: Deep Dive into Core Services

**Study Modules:**
1. `core/service_registry.py` - Master dependency injection
2. `core/database_manager.py` - Async database operations
3. `core/config_manager.py` - Configuration management
4. `services/stellar/rate_limiter_service.py` - Rate limiting implementation

**Key Concepts:**
- Topological sorting for dependency resolution
- Async connection pooling with `asyncpg`
- Health check patterns (`ServiceHealthCheck` utility)
- Rate limiting with semaphores and time windows

**Exercise 2: Create a New Service**

Your task: Create a **notification service** that sends alerts when Ubuntu scores drop below thresholds.

**Requirements:**
1. Follow all 12 design principles
2. Register with service registry
3. Depend on `database` and `holonic_evaluator`
4. Implement health checks
5. Use async/await throughout

**Template:**
```python
"""
UBEC Notification Service - Production Version 1.0
==================================================
Sends notifications when Ubuntu principle scores drop below configured thresholds.

Design Principles Compliance:
â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    âœ… #1  Modular Design: Clear notification boundaries
    âœ… #2  Service Pattern: No standalone execution
    âœ… #3  Service Registry: Dependencies via registry
    âœ… #4  Single Source of Truth: Thresholds in database
    âœ… #5  Strict Async: Full async/await
    âœ… #6  No Sync Fallbacks: Pure async
    âœ… #7  Per-Asset Monitoring: Per-account notifications
    âœ… #8  No Duplicate Configuration: Single config
    âœ… #9  Integrated Rate Limiting: Email rate limiting
    âœ… #10 Separation of Concerns: Notification logic only
    âœ… #11 Comprehensive Documentation: This docstring
    âœ… #12 Method Singularity: No code duplication
â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

Dependencies:
    - database: For querying scores and storing notification history
    - holonic_evaluator: For retrieving current Ubuntu scores

Usage Example:
    >>> notifier = await registry.get('notification')
    >>> await notifier.check_and_notify('GABC123...')

Attribution:
    This project uses the services of Claude and Anthropic PBC to inform our 
    decisions and recommendations. This project was made possible with the 
    assistance of Claude and Anthropic PBC.
"""

import asyncio
import logging
from typing import Dict, List, Optional
from datetime import datetime
from decimal import Decimal

logger = logging.getLogger(__name__)


class NotificationService:
    """
    Service for sending notifications about Ubuntu score changes.
    
    Monitors Ubuntu principle scores and sends notifications when:
    - Scores drop below configured thresholds
    - Scores show sustained declining trends
    - Critical low scores are detected
    
    Attributes:
        _db: Database manager instance
        _evaluator: Holonic evaluator instance
        _initialized: Service initialization status
    """
    
    def __init__(self, database, holonic_evaluator):
        """
        Initialize notification service.
        
        Args:
            database: Database manager service
            holonic_evaluator: Holonic evaluator service
        """
        self._db = database
        self._evaluator = holonic_evaluator
        self._initialized = False
        logger.info("NotificationService created")
    
    async def initialize(self):
        """
        Initialize the notification service.
        
        Sets up notification thresholds from database configuration.
        
        Raises:
            DatabaseError: If configuration cannot be loaded
        """
        logger.info("Initializing NotificationService...")
        
        # Load thresholds from database (principle #4: single source of truth)
        self._thresholds = await self._load_thresholds()
        
        self._initialized = True
        logger.info("âœ“ NotificationService initialized")
    
    async def _load_thresholds(self) -> Dict[str, Decimal]:
        """
        Load notification thresholds from database.
        
        Returns:
            Dictionary mapping principle names to threshold scores
        """
        query = """
            SELECT key, value 
            FROM ubec_main.ubec_config_settings
            WHERE key LIKE 'notification_threshold_%'
        """
        rows = await self._db.fetch(query)
        
        thresholds = {}
        for row in rows:
            principle = row['key'].replace('notification_threshold_', '')
            thresholds[principle] = Decimal(row['value'])
        
        return thresholds
    
    async def check_and_notify(self, account_id: str) -> bool:
        """
        Check account scores and send notifications if needed.
        
        Args:
            account_id: Stellar account ID to check
        
        Returns:
            True if notification was sent, False otherwise
        
        Raises:
            ValueError: If account_id is invalid
        """
        if not self._initialized:
            raise RuntimeError("Service not initialized")
        
        # Get current evaluation
        evaluation = await self._evaluator.evaluate_account(account_id)
        
        # Check each principle against threshold
        notifications_needed = []
        for principle, score in evaluation.scores.items():
            threshold = self._thresholds.get(principle)
            if threshold and score < threshold:
                notifications_needed.append({
                    'principle': principle,
                    'score': score,
                    'threshold': threshold
                })
        
        if notifications_needed:
            await self._send_notifications(account_id, notifications_needed)
            return True
        
        return False
    
    async def _send_notifications(
        self, 
        account_id: str, 
        notifications: List[Dict]
    ):
        """
        Send notifications for low scores.
        
        Args:
            account_id: Account with low scores
            notifications: List of threshold violations
        """
        # TODO: Implement actual notification delivery
        # For now, just log and store in database
        
        for notif in notifications:
            logger.warning(
                f"Low score detected for {account_id}: "
                f"{notif['principle']} = {notif['score']} "
                f"(threshold: {notif['threshold']})"
            )
            
            # Store notification in database
            query = """
                INSERT INTO ubec_main.ubec_notifications
                (account_id, principle, score, threshold, created_at)
                VALUES ($1, $2, $3, $4, $5)
            """
            await self._db.execute(
                query,
                account_id,
                notif['principle'],
                notif['score'],
                notif['threshold'],
                datetime.utcnow()
            )
    
    async def health_check(self) -> Dict:
        """
        Perform health check on notification service.
        
        Returns:
            Health status dictionary
        """
        try:
            # Check database connectivity
            await self._db.fetchval("SELECT 1")
            
            # Check thresholds are loaded
            if not self._thresholds:
                return {
                    'status': 'unhealthy',
                    'message': 'No notification thresholds configured'
                }
            
            return {
                'status': 'healthy',
                'thresholds_loaded': len(self._thresholds),
                'initialized': self._initialized
            }
        
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e)
            }
    
    async def cleanup(self):
        """
        Cleanup resources before shutdown.
        
        This is called by the service registry during shutdown.
        """
        logger.info("Cleaning up NotificationService...")
        self._initialized = False
        logger.info("âœ“ NotificationService cleaned up")


# Factory function for service registry
async def create_notification_service(registry):
    """
    Factory function to create notification service instance.
    
    Args:
        registry: Service registry instance
    
    Returns:
        Initialized NotificationService instance
    """
    database = await registry.get('database')
    holonic_evaluator = await registry.get('holonic_evaluator')
    
    service = NotificationService(database, holonic_evaluator)
    await service.initialize()
    
    return service
```

**Registration in `main.py`:**
```python
# In main.py, add to service registrations
from services.notification.notification_service import create_notification_service

async def setup_services(registry: ServiceRegistry):
    """Register all services with the registry."""
    
    # ... existing registrations ...
    
    # Register notification service
    registry.register_factory(
        'notification',
        create_notification_service,
        dependencies=['database', 'holonic_evaluator']
    )
```

**Database Schema Addition:**
```sql
-- Add notification tracking table
CREATE TABLE ubec_main.ubec_notifications (
    id SERIAL PRIMARY KEY,
    account_id VARCHAR(56) NOT NULL,
    principle VARCHAR(50) NOT NULL,
    score NUMERIC(5, 2) NOT NULL,
    threshold NUMERIC(5, 2) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    notified_at TIMESTAMP WITH TIME ZONE,
    
    FOREIGN KEY (account_id) REFERENCES ubec_main.stellar_accounts(account_id)
);

CREATE INDEX idx_notifications_account ON ubec_main.ubec_notifications(account_id);
CREATE INDEX idx_notifications_created ON ubec_main.ubec_notifications(created_at);

-- Add configuration thresholds
INSERT INTO ubec_main.ubec_config_settings (key, value, description) VALUES
    ('notification_threshold_autonomy', '0.40', 'Autonomy integration threshold'),
    ('notification_threshold_ubuntu', '0.40', 'Ubuntu alignment threshold'),
    ('notification_threshold_reciprocity', '0.40', 'Reciprocity health threshold'),
    ('notification_threshold_mutualism', '0.40', 'Mutualism capacity threshold'),
    ('notification_threshold_regeneration', '0.40', 'Regeneration impact threshold');
```

**Testing Your Service:**
```python
# test_notification_service.py
import pytest
import asyncio
from core.service_registry import ServiceRegistry

@pytest.mark.asyncio
async def test_notification_service_initialization():
    """Test that notification service initializes properly."""
    registry = ServiceRegistry()
    await registry.initialize_all()
    
    notifier = await registry.get('notification')
    assert notifier._initialized is True
    assert len(notifier._thresholds) > 0

@pytest.mark.asyncio
async def test_notification_service_health_check():
    """Test notification service health check."""
    registry = ServiceRegistry()
    await registry.initialize_all()
    
    notifier = await registry.get('notification')
    health = await notifier.health_check()
    
    assert health['status'] == 'healthy'
    assert health['thresholds_loaded'] > 0

@pytest.mark.asyncio
async def test_check_and_notify():
    """Test notification for low score account."""
    registry = ServiceRegistry()
    await registry.initialize_all()
    
    notifier = await registry.get('notification')
    
    # Test with known account (replace with actual test account)
    result = await notifier.check_and_notify('GABC123...')
    
    # Result depends on account scores
    assert isinstance(result, bool)
```

**Run Tests:**
```bash
pytest tests/test_notification_service.py -v
```

**Validation Checklist:**
- [ ] Service follows all 12 design principles
- [ ] Comprehensive docstrings with attribution
- [ ] Registered with service registry
- [ ] Dependencies declared correctly
- [ ] 100% async operations
- [ ] Health check implemented
- [ ] Unit tests pass
- [ ] No code duplication
- [ ] Configuration in database only

**Advanced Challenge:**
Extend the notification service to support multiple notification channels (email, webhook, SMS) while maintaining principle compliance.

---

#### Week 4: Database Mastery

**Focus Areas:**
1. Schema design and relationships
2. Query optimization with indexes
3. Transaction management
4. Connection pooling with `asyncpg`

**Key Tables to Study:**
```sql
-- Core tables
ubec_main.stellar_accounts
ubec_main.stellar_transactions
ubec_main.stellar_operations
ubec_main.ubec_balances
ubec_main.ubec_holonic_metrics
ubec_main.ubec_audit_log
```

**Exercise 3: Query Optimization**

Given this slow query:
```python
async def get_account_transaction_history(self, account_id: str) -> List[dict]:
    """Get all transactions for an account - SLOW!"""
    query = """
        SELECT t.*, o.type, o.amount
        FROM ubec_main.stellar_transactions t
        LEFT JOIN ubec_main.stellar_operations o ON t.transaction_hash = o.transaction_hash
        WHERE t.source_account = $1
        OR o.from_account = $1
        OR o.to_account = $1
        ORDER BY t.created_at DESC
    """
    return await self._db.fetch(query, account_id)
```

**Your Tasks:**
1. Analyze the query execution plan: `EXPLAIN ANALYZE`
2. Identify missing indexes
3. Rewrite for better performance
4. Create appropriate indexes
5. Measure performance improvement

**Solution Approach:**
```sql
-- Check current indexes
SELECT 
    tablename, 
    indexname, 
    indexdef 
FROM pg_indexes 
WHERE schemaname = 'ubec_main'
AND tablename IN ('stellar_transactions', 'stellar_operations');

-- Analyze query plan
EXPLAIN ANALYZE
SELECT t.*, o.type, o.amount
FROM ubec_main.stellar_transactions t
LEFT JOIN ubec_main.stellar_operations o ON t.transaction_hash = o.transaction_hash
WHERE t.source_account = 'GABC123...'
OR o.from_account = 'GABC123...'
OR o.to_account = 'GABC123...'
ORDER BY t.created_at DESC
LIMIT 100;

-- Create missing indexes
CREATE INDEX IF NOT EXISTS idx_stellar_transactions_source_account 
    ON ubec_main.stellar_transactions(source_account);

CREATE INDEX IF NOT EXISTS idx_stellar_operations_from_account 
    ON ubec_main.stellar_operations(from_account);

CREATE INDEX IF NOT EXISTS idx_stellar_operations_to_account 
    ON ubec_main.stellar_operations(to_account);

CREATE INDEX IF NOT EXISTS idx_stellar_transactions_created_at 
    ON ubec_main.stellar_transactions(created_at DESC);

-- Optimized query
SELECT t.*, o.type, o.amount
FROM ubec_main.stellar_transactions t
LEFT JOIN ubec_main.stellar_operations o 
    ON t.transaction_hash = o.transaction_hash
WHERE t.source_account = $1
UNION ALL
SELECT t.*, o.type, o.amount
FROM ubec_main.stellar_operations o
JOIN ubec_main.stellar_transactions t 
    ON o.transaction_hash = t.transaction_hash
WHERE o.from_account = $1 OR o.to_account = $1
ORDER BY created_at DESC
LIMIT 100;
```

**Performance Measurement:**
```python
import time

async def benchmark_query():
    """Benchmark query performance."""
    account_id = 'GABC123...'
    
    # Original query
    start = time.time()
    result1 = await get_account_transaction_history_original(account_id)
    duration1 = time.time() - start
    
    # Optimized query
    start = time.time()
    result2 = await get_account_transaction_history_optimized(account_id)
    duration2 = time.time() - start
    
    print(f"Original: {duration1:.3f}s ({len(result1)} rows)")
    print(f"Optimized: {duration2:.3f}s ({len(result2)} rows)")
    print(f"Improvement: {((duration1 - duration2) / duration1 * 100):.1f}%")
```

---

#### Week 5: Advanced Topics

**Topics:**
1. Circuit breaker patterns for resilience
2. Distributed tracing and observability
3. Database migrations and version control
4. Performance profiling and optimization

**Exercise 4: Implement Circuit Breaker**

```python
"""
Circuit Breaker Pattern Implementation
Prevents cascading failures when external services are down.
"""

from enum import Enum
from datetime import datetime, timedelta
import asyncio

class CircuitState(Enum):
    CLOSED = "closed"  # Normal operation
    OPEN = "open"      # Blocking calls due to failures
    HALF_OPEN = "half_open"  # Testing if service recovered

class CircuitBreaker:
    """
    Circuit breaker for protecting against failing services.
    
    States:
        CLOSED: Normal operation, requests pass through
        OPEN: Too many failures, requests fail immediately
        HALF_OPEN: Testing recovery, limited requests pass through
    """
    
    def __init__(
        self,
        failure_threshold: int = 5,
        timeout: int = 60,
        expected_exception: type = Exception
    ):
        """
        Initialize circuit breaker.
        
        Args:
            failure_threshold: Number of failures before opening circuit
            timeout: Seconds to wait before attempting recovery
            expected_exception: Exception type to catch
        """
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.expected_exception = expected_exception
        
        self._failure_count = 0
        self._last_failure_time = None
        self._state = CircuitState.CLOSED
    
    async def call(self, func, *args, **kwargs):
        """
        Execute function with circuit breaker protection.
        
        Args:
            func: Async function to execute
            *args: Positional arguments for function
            **kwargs: Keyword arguments for function
        
        Returns:
            Function result if successful
        
        Raises:
            CircuitBreakerOpenError: If circuit is open
            Original exception: If circuit is closed and function fails
        """
        if self._state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self._state = CircuitState.HALF_OPEN
            else:
                raise CircuitBreakerOpenError(
                    f"Circuit breaker is OPEN. "
                    f"Retry after {self._get_remaining_timeout()}s"
                )
        
        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        
        except self.expected_exception as e:
            self._on_failure()
            raise
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset."""
        return (
            self._last_failure_time is not None
            and datetime.now() - self._last_failure_time >= timedelta(seconds=self.timeout)
        )
    
    def _get_remaining_timeout(self) -> int:
        """Get remaining seconds until reset attempt."""
        if self._last_failure_time is None:
            return 0
        
        elapsed = (datetime.now() - self._last_failure_time).total_seconds()
        remaining = max(0, self.timeout - elapsed)
        return int(remaining)
    
    def _on_success(self):
        """Handle successful call."""
        self._failure_count = 0
        self._state = CircuitState.CLOSED
    
    def _on_failure(self):
        """Handle failed call."""
        self._failure_count += 1
        self._last_failure_time = datetime.now()
        
        if self._failure_count >= self.failure_threshold:
            self._state = CircuitState.OPEN
    
    @property
    def state(self) -> CircuitState:
        """Get current circuit state."""
        return self._state


class CircuitBreakerOpenError(Exception):
    """Raised when circuit breaker is open."""
    pass


# Usage example
class StellarClientWithCircuitBreaker:
    """Stellar client with circuit breaker protection."""
    
    def __init__(self, horizon_url: str):
        self.horizon_url = horizon_url
        self._circuit_breaker = CircuitBreaker(
            failure_threshold=5,
            timeout=60,
            expected_exception=aiohttp.ClientError
        )
    
    async def fetch_account(self, account_id: str) -> dict:
        """Fetch account with circuit breaker protection."""
        return await self._circuit_breaker.call(
            self._fetch_account_impl,
            account_id
        )
    
    async def _fetch_account_impl(self, account_id: str) -> dict:
        """Actual implementation of fetch."""
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.horizon_url}/accounts/{account_id}"
            ) as response:
                response.raise_for_status()
                return await response.json()
```

**Test Circuit Breaker:**
```python
@pytest.mark.asyncio
async def test_circuit_breaker():
    """Test circuit breaker behavior."""
    calls = 0
    
    async def failing_function():
        nonlocal calls
        calls += 1
        raise Exception("Service unavailable")
    
    breaker = CircuitBreaker(failure_threshold=3, timeout=5)
    
    # First 3 calls should go through and fail
    for i in range(3):
        with pytest.raises(Exception):
            await breaker.call(failing_function)
    
    assert breaker.state == CircuitState.OPEN
    assert calls == 3
    
    # Next call should fail immediately without calling function
    with pytest.raises(CircuitBreakerOpenError):
        await breaker.call(failing_function)
    
    assert calls == 3  # Function not called
    
    # After timeout, should attempt reset
    await asyncio.sleep(6)
    
    with pytest.raises(Exception):
        await breaker.call(failing_function)
    
    assert breaker.state == CircuitState.HALF_OPEN
    assert calls == 4  # Function called again
```

---

### Track 2: Integration Development

**Focus:** Stellar blockchain integration, transaction processing, token operations, and external API interactions.

#### Week 2-3: Stellar Network Mastery

**Study Modules:**
1. `services/stellar/stellar_client_service.py` - Stellar API client
2. `services/data/synchronizer_service.py` - Blockchain data sync
3. `protocols/air_protocol.py` through `fire_protocol.py` - Element protocols

**Stellar Fundamentals:**

**Accounts:**
```python
# Stellar account structure
{
    "id": "GABC123...",  # 56-character public key
    "account_id": "GABC123...",
    "sequence": "12345678901234",  # Transaction sequence number
    "balances": [
        {
            "asset_type": "native",  # XLM
            "balance": "100.0000000"
        },
        {
            "asset_type": "credit_alphanum12",
            "asset_code": "UBEC",
            "asset_issuer": "GDEF456...",
            "balance": "50.0000000"
        }
    ],
    "thresholds": {
        "low_threshold": 0,
        "med_threshold": 0,
        "high_threshold": 0
    }
}
```

**Transactions:**
```python
# Transaction structure
{
    "hash": "abc123...",
    "ledger": 45678901,
    "source_account": "GABC123...",
    "fee_charged": "100",  # in stroops (1 XLM = 10,000,000 stroops)
    "operation_count": 1,
    "successful": true,
    "created_at": "2025-11-02T12:00:00Z"
}
```

**Operations:**
```python
# Operation types relevant to UBEC
OPERATION_TYPES = {
    0: "CREATE_ACCOUNT",
    1: "PAYMENT",
    2: "PATH_PAYMENT_STRICT_RECEIVE",
    3: "MANAGE_SELL_OFFER",
    4: "CREATE_PASSIVE_SELL_OFFER",
    5: "SET_OPTIONS",
    6: "CHANGE_TRUST",  # For establishing trustlines
    7: "ALLOW_TRUST",
    8: "ACCOUNT_MERGE",
    13: "PATH_PAYMENT_STRICT_SEND"
}
```

**Exercise 5: Implement Account Analyzer**

Create a comprehensive account analysis tool:

```python
"""
Stellar Account Analyzer
Analyzes Stellar accounts for UBEC token holdings and transaction patterns.
"""

from typing import Dict, List, Optional
from decimal import Decimal
from datetime import datetime, timedelta

class AccountAnalyzer:
    """
    Comprehensive analyzer for Stellar accounts.
    
    Analyzes:
        - Token holdings (UBEC, UBECrc, UBECgpi, UBECtt)
        - Transaction patterns and frequency
        - Trustline establishment
        - Trading activity on DEX
        - Network connections and relationships
    """
    
    def __init__(self, stellar_client, database):
        """
        Initialize account analyzer.
        
        Args:
            stellar_client: Stellar client service
            database: Database manager service
        """
        self._stellar = stellar_client
        self._db = database
    
    async def analyze_account(self, account_id: str) -> Dict:
        """
        Perform comprehensive account analysis.
        
        Args:
            account_id: Stellar account ID to analyze
        
        Returns:
            Dictionary with complete analysis results
        """
        # Fetch current account state from blockchain
        account_data = await self._stellar.get_account(account_id)
        
        # Analyze balances
        balance_analysis = await self._analyze_balances(account_data)
        
        # Analyze transaction history
        transaction_analysis = await self._analyze_transactions(account_id)
        
        # Analyze trustlines
        trustline_analysis = await self._analyze_trustlines(account_data)
        
        # Analyze trading activity
        trading_analysis = await self._analyze_trading(account_id)
        
        # Analyze network connections
        network_analysis = await self._analyze_network(account_id)
        
        return {
            'account_id': account_id,
            'balances': balance_analysis,
            'transactions': transaction_analysis,
            'trustlines': trustline_analysis,
            'trading': trading_analysis,
            'network': network_analysis,
            'analyzed_at': datetime.utcnow().isoformat()
        }
    
    async def _analyze_balances(self, account_data: dict) -> Dict:
        """
        Analyze account token balances.
        
        Returns:
            Balance analysis including UBEC tokens and XLM
        """
        balances = {}
        
        for balance in account_data['balances']:
            if balance['asset_type'] == 'native':
                balances['XLM'] = {
                    'balance': Decimal(balance['balance']),
                    'asset_type': 'native'
                }
            elif balance.get('asset_code', '').startswith('UBEC'):
                balances[balance['asset_code']] = {
                    'balance': Decimal(balance['balance']),
                    'asset_type': balance['asset_type'],
                    'asset_issuer': balance['asset_issuer'],
                    'limit': Decimal(balance.get('limit', '0'))
                }
        
        # Calculate total UBEC ecosystem participation
        ubec_tokens = [k for k in balances.keys() if k.startswith('UBEC')]
        total_ubec_value = sum(
            balances[token]['balance'] 
            for token in ubec_tokens
        )
        
        return {
            'individual_balances': balances,
            'ubec_tokens_held': len(ubec_tokens),
            'total_ubec_value': total_ubec_value,
            'has_xlm': 'XLM' in balances,
            'xlm_balance': balances.get('XLM', {}).get('balance', Decimal('0'))
        }
    
    async def _analyze_transactions(self, account_id: str) -> Dict:
        """
        Analyze transaction history for patterns.
        
        Returns:
            Transaction pattern analysis
        """
        # Query recent transactions (last 30 days)
        query = """
            SELECT 
                COUNT(*) as total_transactions,
                COUNT(DISTINCT DATE(created_at)) as active_days,
                AVG(operation_count) as avg_operations_per_tx,
                SUM(fee_charged) as total_fees_paid,
                MIN(created_at) as first_transaction,
                MAX(created_at) as latest_transaction
            FROM ubec_main.stellar_transactions
            WHERE source_account = $1
            AND created_at >= NOW() - INTERVAL '30 days'
        """
        
        stats = await self._db.fetchrow(query, account_id)
        
        # Analyze operation types
        ops_query = """
            SELECT 
                type,
                COUNT(*) as count,
                SUM(CASE WHEN amount IS NOT NULL THEN amount ELSE 0 END) as total_amount
            FROM ubec_main.stellar_operations
            WHERE source_account = $1
            OR from_account = $1
            OR to_account = $1
            GROUP BY type
        """
        
        operations = await self._db.fetch(ops_query, account_id)
        
        return {
            'period_days': 30,
            'total_transactions': stats['total_transactions'],
            'active_days': stats['active_days'],
            'avg_operations_per_tx': float(stats['avg_operations_per_tx'] or 0),
            'total_fees_paid': int(stats['total_fees_paid'] or 0),
            'first_transaction': stats['first_transaction'],
            'latest_transaction': stats['latest_transaction'],
            'operation_breakdown': [
                {
                    'type': op['type'],
                    'count': op['count'],
                    'total_amount': float(op['total_amount'])
                }
                for op in operations
            ]
        }
    
    async def _analyze_trustlines(self, account_data: dict) -> Dict:
        """
        Analyze trustline configuration.
        
        Returns:
            Trustline analysis
        """
        trustlines = []
        
        for balance in account_data['balances']:
            if balance['asset_type'] != 'native':
                trustlines.append({
                    'asset_code': balance.get('asset_code'),
                    'asset_issuer': balance.get('asset_issuer'),
                    'limit': Decimal(balance.get('limit', '0')),
                    'balance': Decimal(balance['balance'])
                })
        
        ubec_trustlines = [
            tl for tl in trustlines 
            if tl['asset_code'] and tl['asset_code'].startswith('UBEC')
        ]
        
        return {
            'total_trustlines': len(trustlines),
            'ubec_trustlines': len(ubec_trustlines),
            'trustlines': trustlines,
            'has_ubec_air': any(tl['asset_code'] == 'UBEC' for tl in trustlines),
            'has_ubec_water': any(tl['asset_code'] == 'UBECrc' for tl in trustlines),
            'has_ubec_earth': any(tl['asset_code'] == 'UBECgpi' for tl in trustlines),
            'has_ubec_fire': any(tl['asset_code'] == 'UBECtt' for tl in trustlines)
        }
    
    async def _analyze_trading(self, account_id: str) -> Dict:
        """
        Analyze DEX trading activity.
        
        Returns:
            Trading activity analysis
        """
        query = """
            SELECT 
                COUNT(*) as total_offers,
                COUNT(DISTINCT selling_asset) as unique_selling_assets,
                COUNT(DISTINCT buying_asset) as unique_buying_assets,
                SUM(amount) as total_offer_amount
            FROM ubec_main.stellar_offers
            WHERE seller_account = $1
            AND status = 'active'
        """
        
        stats = await self._db.fetchrow(query, account_id)
        
        return {
            'total_active_offers': stats['total_offers'] or 0,
            'unique_selling_assets': stats['unique_selling_assets'] or 0,
            'unique_buying_assets': stats['unique_buying_assets'] or 0,
            'total_offer_amount': float(stats['total_offer_amount'] or 0),
            'is_market_maker': (stats['total_offers'] or 0) > 5
        }
    
    async def _analyze_network(self, account_id: str) -> Dict:
        """
        Analyze network connections and relationships.
        
        Returns:
            Network analysis
        """
        # Find accounts this account has transacted with
        query = """
            SELECT DISTINCT
                CASE 
                    WHEN from_account = $1 THEN to_account
                    WHEN to_account = $1 THEN from_account
                END as connected_account,
                COUNT(*) as interaction_count
            FROM ubec_main.stellar_operations
            WHERE (from_account = $1 OR to_account = $1)
            AND type = 'payment'
            GROUP BY connected_account
            HAVING connected_account IS NOT NULL
            ORDER BY interaction_count DESC
            LIMIT 20
        """
        
        connections = await self._db.fetch(query, account_id)
        
        return {
            'total_connections': len(connections),
            'top_connections': [
                {
                    'account_id': conn['connected_account'],
                    'interactions': conn['interaction_count']
                }
                for conn in connections[:5]
            ],
            'network_degree': len(connections)
        }


# Usage example
async def analyze_account_example():
    """Example usage of AccountAnalyzer."""
    registry = ServiceRegistry()
    await registry.initialize_all()
    
    stellar_client = await registry.get('stellar_client')
    database = await registry.get('database')
    
    analyzer = AccountAnalyzer(stellar_client, database)
    analysis = await analyzer.analyze_account('GABC123...')
    
    print(f"Account Analysis for {analysis['account_id']}")
    print(f"UBEC Tokens Held: {analysis['balances']['ubec_tokens_held']}")
    print(f"Total Transactions (30d): {analysis['transactions']['total_transactions']}")
    print(f"Network Connections: {analysis['network']['total_connections']}")
```

**Test Your Analyzer:**
```python
@pytest.mark.asyncio
async def test_account_analyzer():
    """Test account analyzer functionality."""
    registry = ServiceRegistry()
    await registry.initialize_all()
    
    stellar_client = await registry.get('stellar_client')
    database = await registry.get('database')
    
    analyzer = AccountAnalyzer(stellar_client, database)
    
    # Test with known account
    analysis = await analyzer.analyze_account('GABC123...')
    
    # Verify structure
    assert 'balances' in analysis
    assert 'transactions' in analysis
    assert 'trustlines' in analysis
    assert 'trading' in analysis
    assert 'network' in analysis
    
    # Verify balance analysis
    assert 'ubec_tokens_held' in analysis['balances']
    assert 'total_ubec_value' in analysis['balances']
```

---

#### Week 4: Transaction Processing

**Focus:**
- Creating and submitting transactions
- Operation composition
- Error handling and retries
- Transaction signing and security

**Exercise 6: Implement Payment Distribution System**

```python
"""
UBEC Payment Distribution System
Handles batch payments and distributions of UBEC tokens.
"""

from stellar_sdk import Server, TransactionBuilder, Network, Asset
from stellar_sdk.exceptions import BadRequestError
from typing import List, Dict
from decimal import Decimal

class PaymentDistributor:
    """
    Handles distribution of UBEC tokens to multiple recipients.
    
    Features:
        - Batch payments (up to 100 operations per transaction)
        - Automatic retry on failure
        - Transaction fee optimization
        - Comprehensive error handling
    """
    
    def __init__(self, stellar_client, database):
        self._stellar = stellar_client
        self._db = database
        self._server = Server(horizon_url="https://horizon.stellar.org")
    
    async def distribute_tokens(
        self,
        source_keypair,  # Signing keypair for source account
        token_code: str,
        token_issuer: str,
        recipients: List[Dict[str, Decimal]],  # [{"account_id": "G...", "amount": Decimal("10.0")}]
        memo: str = None
    ) -> List[str]:
        """
        Distribute tokens to multiple recipients.
        
        Args:
            source_keypair: Signing keypair for source account
            token_code: Token to distribute (UBEC, UBECrc, etc.)
            token_issuer: Issuer account for token
            recipients: List of {"account_id": address, "amount": amount}
            memo: Optional transaction memo
        
        Returns:
            List of transaction hashes
        
        Raises:
            ValueError: If recipients list is invalid
            TransactionError: If transaction submission fails
        """
        if not recipients:
            raise ValueError("Recipients list cannot be empty")
        
        # Create asset
        asset = Asset(token_code, token_issuer)
        
        # Batch recipients into groups of 100 (Stellar limit)
        batches = self._create_batches(recipients, batch_size=100)
        
        transaction_hashes = []
        
        for batch in batches:
            tx_hash = await self._distribute_batch(
                source_keypair,
                asset,
                batch,
                memo
            )
            transaction_hashes.append(tx_hash)
        
        return transaction_hashes
    
    def _create_batches(
        self, 
        recipients: List[Dict], 
        batch_size: int
    ) -> List[List[Dict]]:
        """Split recipients into batches."""
        batches = []
        for i in range(0, len(recipients), batch_size):
            batches.append(recipients[i:i + batch_size])
        return batches
    
    async def _distribute_batch(
        self,
        source_keypair,
        asset: Asset,
        recipients: List[Dict],
        memo: str
    ) -> str:
        """
        Distribute tokens to a single batch of recipients.
        
        Returns:
            Transaction hash
        """
        source_account = source_keypair.public_key
        
        # Load source account from network
        account = await self._server.load_account(source_account)
        
        # Calculate base fee (minimum 100 stroops per operation)
        base_fee = await self._server.fetch_base_fee()
        
        # Build transaction
        transaction_builder = TransactionBuilder(
            source_account=account,
            network_passphrase=Network.PUBLIC_NETWORK_PASSPHRASE,
            base_fee=base_fee
        )
        
        # Add memo if provided
        if memo:
            transaction_builder.add_text_memo(memo)
        
        # Add payment operation for each recipient
        for recipient in recipients:
            transaction_builder.append_payment_op(
                destination=recipient['account_id'],
                asset=asset,
                amount=str(recipient['amount'])
            )
        
        # Build and sign transaction
        transaction = transaction_builder.build()
        transaction.sign(source_keypair)
        
        # Submit transaction with retry logic
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = await self._server.submit_transaction(transaction)
                tx_hash = response['hash']
                
                # Store in database
                await self._record_distribution(
                    tx_hash,
                    source_account,
                    recipients,
                    asset
                )
                
                return tx_hash
            
            except BadRequestError as e:
                if attempt == max_retries - 1:
                    raise TransactionError(f"Failed after {max_retries} attempts: {e}")
                
                # Wait before retry
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
    
    async def _record_distribution(
        self,
        tx_hash: str,
        source: str,
        recipients: List[Dict],
        asset: Asset
    ):
        """Record distribution in database."""
        query = """
            INSERT INTO ubec_main.ubec_distributions
            (transaction_hash, source_account, token_code, recipient_count, total_amount, created_at)
            VALUES ($1, $2, $3, $4, $5, $6)
        """
        
        total_amount = sum(r['amount'] for r in recipients)
        
        await self._db.execute(
            query,
            tx_hash,
            source,
            asset.code,
            len(recipients),
            total_amount,
            datetime.utcnow()
        )


class TransactionError(Exception):
    """Raised when transaction submission fails."""
    pass
```

**Advanced Challenge:**
Implement a smart distribution algorithm that optimizes for:
1. Minimum transaction fees
2. Maximum throughput
3. Fair distribution based on Ubuntu principles

---

### Track 3: Protocol Research

**Focus:** Ubuntu philosophy, economic systems design, holonic evaluation, and network analysis.

#### Week 2-3: Ubuntu Philosophy & Holonic Systems

**Study Modules:**
1. `services/analytics/holonic_evaluator_service.py` - Ubuntu assessment
2. `protocols/` - All four element protocols
3. `visualization/holonic_visualizer.py` - Data visualization

**Core Concepts:**

**Ubuntu Principles:**
1. **Autonomy-Integration:** Balance between individual agency and collective participation
2. **Ubuntu Alignment:** Embodiment of "I am because we are"
3. **Reciprocity Health:** Quality of mutual exchange
4. **Mutualism Capacity:** Ability to create collective benefit
5. **Regeneration Impact:** Contribution to ecosystem renewal

**Holonic Structure:**
- **Holon:** Entity that is simultaneously a whole and a part
- **Holarchy:** Nested hierarchy of holons
- **Emergence:** System properties arising from interactions

**Exercise 7: Design New Ubuntu Metric**

Create a new metric that evaluates **"Generosity Quotient"** - measuring the propensity to give without expectation of return.

**Requirements:**
1. Define mathematical formula
2. Implement calculation method
3. Integrate with holonic evaluator
4. Create visualization
5. Write comprehensive documentation

**Template:**
```python
"""
Generosity Quotient Metric
Measures account's propensity for unconditional giving within the UBEC ecosystem.

Formula:
    GQ = (outbound_gifts / total_outbound) * diversity_factor * consistency_factor
    
Where:
    - outbound_gifts: Payments with no reciprocal return within 30 days
    - total_outbound: All outbound payments
    - diversity_factor: sqrt(unique_recipients / total_transactions)
    - consistency_factor: (transactions_with_gifts / total_periods) ^ 0.5

Score Range: 0.0 to 1.0
    - 0.0-0.3: Low generosity (transactional mindset)
    - 0.3-0.6: Moderate generosity (balanced approach)
    - 0.6-0.8: High generosity (giving-oriented)
    - 0.8-1.0: Exceptional generosity (unconditional giver)
"""

from typing import Dict, List
from decimal import Decimal
from datetime import datetime, timedelta
import math

class GenerosityEvaluator:
    """
    Evaluates generosity quotient for UBEC network participants.
    """
    
    def __init__(self, database, analytics):
        self._db = database
        self._analytics = analytics
    
    async def calculate_generosity_quotient(
        self, 
        account_id: str,
        lookback_days: int = 90
    ) -> Dict:
        """
        Calculate generosity quotient for an account.
        
        Args:
            account_id: Account to evaluate
            lookback_days: Historical period to analyze
        
        Returns:
            Dictionary with GQ score and component metrics
        """
        # Fetch transaction data
        transactions = await self._get_transactions(account_id, lookback_days)
        
        if not transactions:
            return self._zero_score()
        
        # Calculate components
        gift_ratio = await self._calculate_gift_ratio(
            account_id, 
            transactions
        )
        
        diversity_factor = self._calculate_diversity_factor(transactions)
        consistency_factor = await self._calculate_consistency_factor(
            account_id,
            lookback_days
        )
        
        # Calculate final score
        gq_score = gift_ratio * diversity_factor * consistency_factor
        
        return {
            'generosity_quotient': float(gq_score),
            'gift_ratio': float(gift_ratio),
            'diversity_factor': float(diversity_factor),
            'consistency_factor': float(consistency_factor),
            'total_gifts': len([t for t in transactions if t['is_gift']]),
            'total_transactions': len(transactions),
            'evaluation_period_days': lookback_days,
            'category': self._categorize_score(gq_score)
        }
    
    async def _get_transactions(
        self, 
        account_id: str, 
        lookback_days: int
    ) -> List[Dict]:
        """Fetch outbound transactions for account."""
        query = """
            SELECT 
                o.operation_id,
                o.to_account as recipient,
                o.amount,
                o.created_at,
                t.transaction_hash
            FROM ubec_main.stellar_operations o
            JOIN ubec_main.stellar_transactions t 
                ON o.transaction_hash = t.transaction_hash
            WHERE o.from_account = $1
            AND o.type = 'payment'
            AND o.created_at >= NOW() - $2::interval
            ORDER BY o.created_at
        """
        
        rows = await self._db.fetch(
            query, 
            account_id, 
            f'{lookback_days} days'
        )
        
        return [dict(row) for row in rows]
    
    async def _calculate_gift_ratio(
        self, 
        account_id: str,
        transactions: List[Dict]
    ) -> Decimal:
        """
        Calculate ratio of gifts to total outbound payments.
        
        A payment is considered a gift if there's no reciprocal
        payment from recipient within 30 days.
        """
        if not transactions:
            return Decimal('0')
        
        gifts = []
        
        for tx in transactions:
            is_gift = await self._is_gift_payment(
                account_id,
                tx['recipient'],
                tx['created_at']
            )
            
            if is_gift:
                gifts.append(tx)
        
        return Decimal(len(gifts)) / Decimal(len(transactions))
    
    async def _is_gift_payment(
        self,
        sender: str,
        recipient: str,
        payment_time: datetime
    ) -> bool:
        """
        Check if payment is a gift (no reciprocal return).
        """
        # Look for reciprocal payment within 30 days
        query = """
            SELECT COUNT(*)
            FROM ubec_main.stellar_operations
            WHERE from_account = $1
            AND to_account = $2
            AND type = 'payment'
            AND created_at BETWEEN $3 AND $3 + INTERVAL '30 days'
        """
        
        count = await self._db.fetchval(
            query,
            recipient,  # From recipient
            sender,     # To sender
            payment_time
        )
        
        return count == 0  # No reciprocal payment = gift
    
    def _calculate_diversity_factor(
        self, 
        transactions: List[Dict]
    ) -> Decimal:
        """
        Calculate diversity of recipients.
        
        Higher diversity = more generosity spread across network.
        """
        if not transactions:
            return Decimal('0')
        
        unique_recipients = len(set(tx['recipient'] for tx in transactions))
        total_transactions = len(transactions)
        
        # Square root scaling for more gradual increase
        diversity = math.sqrt(unique_recipients / total_transactions)
        
        return Decimal(str(diversity))
    
    async def _calculate_consistency_factor(
        self,
        account_id: str,
        lookback_days: int
    ) -> Decimal:
        """
        Calculate consistency of giving behavior.
        
        Measures regularity of gift-giving across time periods.
        """
        # Divide lookback period into weeks
        num_weeks = lookback_days // 7
        
        query = """
            SELECT 
                DATE_TRUNC('week', o.created_at) as week,
                COUNT(*) as gift_count
            FROM ubec_main.stellar_operations o
            WHERE o.from_account = $1
            AND o.type = 'payment'
            AND o.created_at >= NOW() - $2::interval
            GROUP BY week
            ORDER BY week
        """
        
        rows = await self._db.fetch(
            query,
            account_id,
            f'{lookback_days} days'
        )
        
        weeks_with_gifts = len(rows)
        
        if num_weeks == 0:
            return Decimal('0')
        
        consistency = weeks_with_gifts / num_weeks
        
        # Square root scaling for more gradual increase
        return Decimal(str(math.sqrt(consistency)))
    
    def _categorize_score(self, score: Decimal) -> str:
        """Categorize GQ score into descriptive label."""
        score = float(score)
        
        if score >= 0.8:
            return "exceptional_generosity"
        elif score >= 0.6:
            return "high_generosity"
        elif score >= 0.3:
            return "moderate_generosity"
        else:
            return "low_generosity"
    
    def _zero_score(self) -> Dict:
        """Return zero score for accounts with no data."""
        return {
            'generosity_quotient': 0.0,
            'gift_ratio': 0.0,
            'diversity_factor': 0.0,
            'consistency_factor': 0.0,
            'total_gifts': 0,
            'total_transactions': 0,
            'evaluation_period_days': 0,
            'category': 'no_data'
        }
```

**Visualization Integration:**
```python
async def visualize_generosity(
    self,
    account_id: str,
    gq_data: Dict
) -> str:
    """
    Create visualization for generosity quotient.
    
    Returns:
        Base64-encoded PNG image
    """
    import matplotlib.pyplot as plt
    import io
    import base64
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # Component breakdown (left chart)
    components = ['Gift Ratio', 'Diversity', 'Consistency']
    values = [
        gq_data['gift_ratio'],
        gq_data['diversity_factor'],
        gq_data['consistency_factor']
    ]
    
    ax1.barh(components, values, color='#4CAF50')
    ax1.set_xlabel('Score')
    ax1.set_title('Generosity Components')
    ax1.set_xlim(0, 1.0)
    
    # Overall score gauge (right chart)
    gq_score = gq_data['generosity_quotient']
    
    ax2.bar(['Overall GQ'], [gq_score], color='#2196F3', width=0.5)
    ax2.set_ylim(0, 1.0)
    ax2.set_ylabel('Score')
    ax2.set_title(f'Generosity Quotient: {gq_score:.2f}')
    ax2.axhline(y=0.8, color='g', linestyle='--', label='Exceptional')
    ax2.axhline(y=0.6, color='y', linestyle='--', label='High')
    ax2.axhline(y=0.3, color='r', linestyle='--', label='Moderate')
    ax2.legend()
    
    plt.tight_layout()
    
    # Convert to base64
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.read()).decode()
    plt.close()
    
    return f"data:image/png;base64,{image_base64}"
```

**Test Your Metric:**
```python
@pytest.mark.asyncio
async def test_generosity_evaluator():
    """Test generosity quotient calculation."""
    registry = ServiceRegistry()
    await registry.initialize_all()
    
    database = await registry.get('database')
    analytics = await registry.get('analytics')
    
    evaluator = GenerosityEvaluator(database, analytics)
    
    # Test with known accounts
    high_giver = await evaluator.calculate_generosity_quotient('GABC123...')
    assert high_giver['generosity_quotient'] > 0.6
    assert high_giver['category'] in ['high_generosity', 'exceptional_generosity']
    
    low_giver = await evaluator.calculate_generosity_quotient('GDEF456...')
    assert low_giver['generosity_quotient'] < 0.3
    assert low_giver['category'] == 'low_generosity'
```

---

#### Week 4-5: Network Analysis & Research Methods

**Focus:**
- Graph theory and network metrics
- Statistical analysis of token distributions
- Research methodologies for economic systems
- Publishing findings and recommendations

**Exercise 8: Network Topology Analysis**

Analyze the UBEC network topology to identify:
1. Central nodes (most connected accounts)
2. Community clusters
3. Bottlenecks and vulnerabilities
4. Network resilience metrics

```python
"""
UBEC Network Topology Analyzer
Analyzes network structure and identifies patterns.
"""

import networkx as nx
from typing import Dict, List, Tuple
import numpy as np

class NetworkTopologyAnalyzer:
    """
    Analyzes UBEC network topology using graph theory.
    """
    
    def __init__(self, database):
        self._db = database
        self._graph = None
    
    async def build_network_graph(self) -> nx.DiGraph:
        """
        Build directed graph from transaction data.
        
        Returns:
            NetworkX directed graph
        """
        query = """
            SELECT DISTINCT
                from_account as source,
                to_account as target,
                COUNT(*) as weight,
                SUM(amount) as total_amount
            FROM ubec_main.stellar_operations
            WHERE type = 'payment'
            AND from_account IS NOT NULL
            AND to_account IS NOT NULL
            GROUP BY from_account, to_account
        """
        
        edges = await self._db.fetch(query)
        
        G = nx.DiGraph()
        
        for edge in edges:
            G.add_edge(
                edge['source'],
                edge['target'],
                weight=edge['weight'],
                total_amount=float(edge['total_amount'])
            )
        
        self._graph = G
        return G
    
    async def analyze_network(self) -> Dict:
        """
        Perform comprehensive network analysis.
        
        Returns:
            Dictionary with network metrics
        """
        if self._graph is None:
            await self.build_network_graph()
        
        G = self._graph
        
        # Basic metrics
        num_nodes = G.number_of_nodes()
        num_edges = G.number_of_edges()
        density = nx.density(G)
        
        # Centrality measures
        degree_centrality = nx.degree_centrality(G)
        betweenness_centrality = nx.betweenness_centrality(G)
        eigenvector_centrality = nx.eigenvector_centrality(G, max_iter=1000)
        
        # Identify key nodes
        top_degree = sorted(
            degree_centrality.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:10]
        
        top_betweenness = sorted(
            betweenness_centrality.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        # Community detection
        communities = list(nx.algorithms.community.greedy_modularity_communities(
            G.to_undirected()
        ))
        
        # Network resilience
        connected_components = list(nx.weakly_connected_components(G))
        largest_component = max(connected_components, key=len)
        
        return {
            'basic_metrics': {
                'nodes': num_nodes,
                'edges': num_edges,
                'density': density,
                'avg_degree': sum(dict(G.degree()).values()) / num_nodes
            },
            'centrality': {
                'top_degree_nodes': [
                    {'account': node, 'score': score}
                    for node, score in top_degree
                ],
                'top_betweenness_nodes': [
                    {'account': node, 'score': score}
                    for node, score in top_betweenness
                ]
            },
            'communities': {
                'total_communities': len(communities),
                'avg_community_size': np.mean([len(c) for c in communities]),
                'largest_community_size': max(len(c) for c in communities)
            },
            'resilience': {
                'connected_components': len(connected_components),
                'largest_component_size': len(largest_component),
                'network_cohesion': len(largest_component) / num_nodes
            }
        }
    
    def visualize_network(
        self,
        output_path: str = 'network_graph.png',
        layout: str = 'spring'
    ):
        """
        Create network visualization.
        
        Args:
            output_path: Path to save visualization
            layout: Layout algorithm ('spring', 'circular', 'kamada_kawai')
        """
        import matplotlib.pyplot as plt
        
        if self._graph is None:
            raise RuntimeError("Graph not built. Call build_network_graph() first.")
        
        G = self._graph
        
        # Choose layout
        if layout == 'spring':
            pos = nx.spring_layout(G, k=0.5, iterations=50)
        elif layout == 'circular':
            pos = nx.circular_layout(G)
        elif layout == 'kamada_kawai':
            pos = nx.kamada_kawai_layout(G)
        else:
            pos = nx.spring_layout(G)
        
        # Node sizes based on degree
        node_sizes = [G.degree(node) * 20 for node in G.nodes()]
        
        # Node colors based on betweenness centrality
        betweenness = nx.betweenness_centrality(G)
        node_colors = [betweenness[node] for node in G.nodes()]
        
        plt.figure(figsize=(16, 12))
        
        nx.draw_networkx_nodes(
            G, pos,
            node_size=node_sizes,
            node_color=node_colors,
            cmap=plt.cm.viridis,
            alpha=0.7
        )
        
        nx.draw_networkx_edges(
            G, pos,
            alpha=0.2,
            arrows=True,
            arrowsize=10
        )
        
        plt.title('UBEC Network Topology', fontsize=20)
        plt.axis('off')
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
```

---

## Practical Exercises

### Exercise 9: Complete Service Health Dashboard

Create a real-time health monitoring dashboard for all 14 services:

**Requirements:**
1. Web interface (HTML + JavaScript)
2. Real-time updates via WebSocket or polling
3. Visual indicators (green/yellow/red)
4. Historical health data
5. Alert system for degraded services

**Technologies:**
- Backend: Python async web framework (e.g., FastAPI)
- Frontend: HTML, CSS, JavaScript (vanilla or React)
- Database: PostgreSQL (existing tables)

**Deliverables:**
- Working web dashboard
- API endpoints for health data
- Automated testing
- Documentation

---

### Exercise 10: Multi-Element Transaction Composer

Build a system that composes complex transactions involving multiple UBEC elements:

**Scenario:**
User wants to:
1. Establish trustline to UBECrc (Water)
2. Receive UBECrc tokens
3. Trade UBECrc for UBECgpi (Earth)
4. Send partial UBECgpi to another account

All in a single transaction.

**Requirements:**
1. Compose multi-operation transaction
2. Handle fees and sequencing
3. Validate all operations
4. Atomic execution (all or nothing)
5. Error handling and rollback

---

### Exercise 11: Ubuntu Score Optimization Advisor

Create an AI advisor that analyzes an account's Ubuntu scores and provides actionable recommendations:

**Features:**
1. Analyze current scores across 5 principles
2. Identify weak areas
3. Generate specific recommendations
4. Simulate impact of actions
5. Track improvement over time

**Example Output:**
```
Ubuntu Score Analysis for GABC123...
====================================

Current Scores:
- Autonomy-Integration: 0.72 (Good)
- Ubuntu Alignment: 0.45 (Needs Improvement)
- Reciprocity Health: 0.88 (Excellent)
- Mutualism Capacity: 0.51 (Moderate)
- Regeneration Impact: 0.39 (Needs Improvement)

Overall Ubuntu Score: 0.59 (Moderate)

Recommendations:
1. Ubuntu Alignment (Priority: HIGH)
   - Action: Increase transactions with community members
   - Expected Impact: +0.15 score increase
   - Timeframe: 30 days

2. Regeneration Impact (Priority: HIGH)
   - Action: Participate in Fire (UBECtt) transformation protocols
   - Expected Impact: +0.20 score increase
   - Timeframe: 60 days

3. Mutualism Capacity (Priority: MEDIUM)
   - Action: Join or create liquidity pools
   - Expected Impact: +0.10 score increase
   - Timeframe: 45 days

Predicted Score in 90 days: 0.79 (Good)
```

---

## Common Patterns & Anti-Patterns

### Pattern: Async Context Manager for Services

**âœ… GOOD:**
```python
class DatabaseManager:
    """Database service with proper resource management."""
    
    async def __aenter__(self):
        """Initialize connection pool."""
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Cleanup connection pool."""
        await self.cleanup()

# Usage
async with DatabaseManager() as db:
    result = await db.query("SELECT * FROM accounts")
    # Connection automatically cleaned up
```

### Anti-Pattern: Blocking Operations in Async Context

**âŒ BAD:**
```python
async def fetch_data():
    # BLOCKING call in async function!
    data = requests.get(url)  # This blocks the entire event loop!
    return data.json()
```

**âœ… GOOD:**
```python
async def fetch_data():
    # Proper async operation
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()
```

### Pattern: Dependency Injection via Factory

**âœ… GOOD:**
```python
async def create_service(registry):
    """Factory function with dependency injection."""
    db = await registry.get('database')
    config = await registry.get('config')
    return MyService(db, config)

# Register
registry.register_factory('my_service', create_service, dependencies=['database', 'config'])
```

### Anti-Pattern: Direct Service Instantiation

**âŒ BAD:**
```python
# Tight coupling!
db = DatabaseManager()
config = ConfigManager(db)
service = MyService(db, config)
```

### Pattern: Comprehensive Error Handling

**âœ… GOOD:**
```python
async def safe_operation():
    """Operation with comprehensive error handling."""
    try:
        result = await risky_operation()
        return result
    
    except SpecificError as e:
        logger.error(f"Specific error occurred: {e}")
        # Handle specifically
        raise
    
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        # Generic fallback
        raise OperationError("Operation failed") from e
    
    finally:
        # Cleanup always happens
        await cleanup_resources()
```

### Anti-Pattern: Silent Failures

**âŒ BAD:**
```python
async def unsafe_operation():
    """Swallows errors silently!"""
    try:
        result = await risky_operation()
        return result
    except:
        pass  # Silent failure - terrible!
```

---

## Resources & Support

### Documentation

**Official Docs:**
- [Stellar Developer Documentation](https://developers.stellar.org/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Python Async/Await Guide](https://docs.python.org/3/library/asyncio.html)

**Project Docs:**
- `docs/` directory in repository
- Architecture diagrams
- API documentation
- Deployment guides

### Community & Support

**Channels:**
- Internal Slack: `#ubec-development`
- Code Reviews: Pull request discussions
- Office Hours: Weekly tech talks

**Mentorship:**
- Assigned mentor for each track
- Pair programming sessions
- Code review buddies

### Continuous Learning

**Recommended Reading:**
1. "Ubuntu: I Am Because We Are" - Philosophical foundations
2. "Designing Data-Intensive Applications" - System design
3. "The Stellar Consensus Protocol" - Blockchain fundamentals

**Courses:**
- Async Python Programming
- Blockchain Development on Stellar
- PostgreSQL Performance Tuning

### Getting Help

**Debugging Checklist:**
1. Check service health: `python main.py health`
2. Review logs: `tail -f logs/ubec.log`
3. Verify database connectivity
4. Check principle compliance
5. Ask for help (it's encouraged!)

**When Stuck:**
1. Review relevant design principle
2. Check for similar code patterns
3. Consult project documentation
4. Ask your mentor
5. Post in development channel

---

## Next Steps

### Week 1 Goals (All Developers)
- [ ] Complete environment setup
- [ ] Run all health checks successfully
- [ ] Understand service registry
- [ ] Review all 12 design principles
- [ ] Complete Exercise 1

### Track-Specific Milestones

**Core Developers:**
- [ ] Create first service (Exercise 2)
- [ ] Optimize database query (Exercise 3)
- [ ] Implement circuit breaker (Exercise 4)

**Integration Developers:**
- [ ] Implement account analyzer (Exercise 5)
- [ ] Build payment distributor (Exercise 6)
- [ ] Deploy test transaction to Stellar

**Protocol Research:**
- [ ] Design new Ubuntu metric (Exercise 7)
- [ ] Analyze network topology (Exercise 8)
- [ ] Create research paper

### Certification

**Junior Developer (Weeks 1-3):**
- Complete common foundation
- Pass design principles quiz
- Complete 2 basic exercises

**Developer (Weeks 4-6):**
- Complete track-specific exercises
- Contribute to codebase
- Pass code review

**Senior Developer (Weeks 7-10):**
- Design and implement new service
- Mentor junior developer
- Present technical talk

---

## Final Notes

### Design Principle Compliance Checklist

Before submitting any code, verify compliance with all 12 principles:

```
â–¡ #1  Modular Design: Clear boundaries?
â–¡ #2  Service Pattern: No standalone execution?
â–¡ #3  Service Registry: Dependencies via registry?
â–¡ #4  Single Source of Truth: Database-backed?
â–¡ #5  Strict Async: 100% async/await?
â–¡ #6  No Sync Fallbacks: Pure async?
â–¡ #7  Per-Asset Monitoring: Individual tracking?
â–¡ #8  No Duplicate Configuration: Single source?
â–¡ #9  Integrated Rate Limiting: Protected APIs?
â–¡ #10 Separation of Concerns: Clear layers?
â–¡ #11 Comprehensive Documentation: Complete docs?
â–¡ #12 Method Singularity: No duplication?
```

### Attribution Requirement

**Every file must include:**
```python
"""
Attribution:
    This project uses the services of Claude and Anthropic PBC to inform our 
    decisions and recommendations. This project was made possible with the 
    assistance of Claude and Anthropic PBC.
"""
```

### Code of Conduct

1. **Quality over speed:** Take time to do it right
2. **Ask questions:** No question is too small
3. **Review code:** Learn from others' work
4. **Share knowledge:** Help your fellow developers
5. **Embrace Ubuntu:** "I am because we are"

---

**Welcome to the UBEC development team! Let's build something extraordinary together.**

*"I am because we are" - Ubuntu ðŸŒ*

---

**Attribution:**
This project uses the services of Claude and Anthropic PBC to inform our decisions and recommendations. This project was made possible with the assistance of Claude and Anthropic PBC.
