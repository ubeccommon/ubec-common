# UBEC DAO Protocol Suite - Technical Operator Onboarding Guide

**Version:** 1.0  
**Last Updated:** November 2, 2025  
**Target Audience:** Database Administrators, Blockchain Operators, Systems Engineers  
**Estimated Onboarding Time:** 6-8 hours

---

## Document Overview

This guide provides comprehensive technical onboarding for operators responsible for database management, blockchain operations, and system-level troubleshooting of the UBEC (Ubuntu Bioregional Economic Commons) DAO Protocol Suite. This documentation assumes advanced technical knowledge and focuses on operational procedures, architecture internals, and hands-on troubleshooting.

**Attribution:** This project uses the services of Claude and Anthropic PBC to inform our decisions and recommendations. This project was made possible with the assistance of Claude and Anthropic PBC.

---

## Table of Contents

1. [Technical Architecture Deep Dive](#technical-architecture-deep-dive)
2. [Database Operations](#database-operations)
3. [Blockchain Integration](#blockchain-integration)
4. [Service Registry Internals](#service-registry-internals)
5. [Data Synchronization](#data-synchronization)
6. [Performance Tuning](#performance-tuning)
7. [Advanced Troubleshooting](#advanced-troubleshooting)
8. [System Internals](#system-internals)
9. [Development Operations](#development-operations)
10. [Emergency Procedures](#emergency-procedures)

---

## Technical Architecture Deep Dive

### Design Principles

The UBEC Protocol Suite is built on **12 core design principles** that govern all architectural decisions:

1. **Modular Design:** Self-contained holonic components with clear boundaries
2. **Service Pattern:** Only `main.py` executes; all modules are services
3. **Service Registry:** Centralized dependency injection with topological sorting
4. **Single Source of Truth:** Database-backed configuration, no duplication
5. **Strict Async:** 100% async/await, zero blocking operations
6. **No Sync Fallbacks:** Forward-looking codebase only
7. **Per-Asset Monitoring:** Individual tracking with execution minimums
8. **No Duplicate Configuration:** Each parameter defined exactly once
9. **Integrated Rate Limiting:** Built-in protection for all external APIs
10. **Clear Separation of Concerns:** Layered architecture
11. **Comprehensive Documentation:** Complete docstrings in all modules
12. **Method Singularity:** Each method implemented once (zero code duplication)

### Async-Only Architecture

**Critical:** The entire codebase operates on asyncio patterns. There are NO synchronous fallbacks.

```python
# Service Registry Pattern - All services async
async with registry:
    db = await registry.get('database')
    result = await db.execute("SELECT * FROM accounts")
    
# Database Operations - Always async
async def fetch_accounts(self):
    async with self.pool.acquire() as conn:
        return await conn.fetch("SELECT * FROM stellar_accounts")

# Stellar Operations - Always async  
async def get_account(self, account_id: str):
    return await self.server.accounts().account_id(account_id).call()
```

**Why This Matters:**
- No blocking I/O anywhere in the system
- Concurrent operations by default
- Efficient resource utilization
- Predictable performance characteristics

### Service Dependency Graph

The service registry uses topological sorting to resolve dependencies:

```
database (no dependencies)
  â”œâ”€â”€ config (requires: database)
  â”‚   â”œâ”€â”€ stellar_client (requires: config)
  â”‚   â”œâ”€â”€ air (requires: database, config)
  â”‚   â”œâ”€â”€ water (requires: database, config)
  â”‚   â”œâ”€â”€ earth (requires: database, config)
  â”‚   â”œâ”€â”€ fire (requires: database, config)
  â”‚   â””â”€â”€ monitoring (requires: database, config)
  â”‚
  â”œâ”€â”€ synchronizer (requires: database, stellar_client)
  â”œâ”€â”€ analytics (requires: database)
  â”œâ”€â”€ distribution (requires: database)
  â”œâ”€â”€ distribution_evaluator (requires: database, distribution)
  â”œâ”€â”€ holonic_evaluator (requires: database)
  â”œâ”€â”€ visualizer (requires: database, analytics)
  â””â”€â”€ audit (requires: database)
```

**Initialization Order:** Services initialize in dependency order automatically. Manual initialization is never required.

### Component Communication

**Inter-Service Communication Pattern:**

```python
# Services communicate through registry only
# NO direct imports between service modules

# âœ… CORRECT: Via registry
synchronizer = await registry.get('synchronizer')
stellar = await registry.get('stellar_client')
result = await synchronizer.sync_account(account_id)

# âŒ INCORRECT: Direct import
from modules.synchronizer import UBECDataSynchronizer
sync = UBECDataSynchronizer()  # NEVER DO THIS
```

**Database as Message Bus:**

The system uses the database as the authoritative communication layer:
- No in-memory state required
- Services can restart without state loss
- Multi-instance deployment possible (with coordination)
- Audit trail for all operations

---

## Database Operations

### Schema Architecture

**Primary Schema:** `ubec_main`  
**Analytics Schema:** `phenomenal` (optional, for advanced metrics)

**Table Categories:**

| Category | Tables | Purpose |
|----------|--------|---------|
| **Blockchain Mirror** | stellar_accounts, stellar_transactions, stellar_operations, stellar_ledgers | Direct Stellar blockchain data |
| **Token Balances** | ubec_balances, ubec_balance_history | Token holdings and changes |
| **Protocol Data** | ubec_air_metrics, ubec_water_flows, ubec_earth_distributions, ubec_fire_transformations | Element-specific tracking |
| **Evaluation** | ubec_holonic_metrics, ubec_holonic_history | Ubuntu principle assessments |
| **Distribution** | ubec_distributions, ubec_distribution_states, ubec_distribution_events | Tokenomics compliance |
| **System** | ubec_config, ubec_audit_log, ubec_system_state | Configuration and auditing |

### Connection Pool Management

**Pool Configuration:**

```python
# From .env
DB_POOL_MIN=5      # Minimum connections
DB_POOL_MAX=20     # Maximum connections
DB_POOL_TIMEOUT=30 # Connection timeout (seconds)
DB_COMMAND_TIMEOUT=60  # Query timeout (seconds)
```

**Pool Monitoring:**

```bash
# Check pool status
python main.py database --pool-status

# Output:
# Pool Status:
#   â€¢ Size: 15 connections
#   â€¢ Active: 12 connections
#   â€¢ Idle: 3 connections
#   â€¢ Max: 20 connections
#   â€¢ Utilization: 60%
```

**Managing Pool Exhaustion:**

```sql
-- View active connections
SELECT 
    pid,
    usename,
    application_name,
    client_addr,
    state,
    query_start,
    state_change,
    LEFT(query, 50) as query_preview
FROM pg_stat_activity
WHERE datname = 'ubec'
ORDER BY query_start DESC;

-- Terminate long-running queries (use with caution)
SELECT pg_terminate_backend(pid) 
FROM pg_stat_activity 
WHERE datname = 'ubec' 
  AND state = 'active' 
  AND query_start < NOW() - INTERVAL '10 minutes'
  AND pid <> pg_backend_pid();
```

### Database Maintenance

**Vacuum Operations:**

```sql
-- Standard vacuum (can run during operations)
VACUUM ANALYZE ubec_main.stellar_transactions;

-- Full vacuum (requires exclusive lock, schedule during maintenance window)
VACUUM FULL ANALYZE ubec_main.stellar_transactions;

-- Auto-vacuum configuration
ALTER TABLE ubec_main.stellar_transactions 
SET (autovacuum_vacuum_scale_factor = 0.1);

-- Check vacuum statistics
SELECT 
    schemaname,
    relname,
    last_vacuum,
    last_autovacuum,
    last_analyze,
    last_autoanalyze,
    n_tup_ins,
    n_tup_upd,
    n_tup_del
FROM pg_stat_user_tables
WHERE schemaname = 'ubec_main'
ORDER BY n_tup_upd DESC;
```

**Index Maintenance:**

```sql
-- Find unused indexes
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch,
    pg_size_pretty(pg_relation_size(indexrelid)) as index_size
FROM pg_stat_user_indexes
WHERE schemaname = 'ubec_main'
  AND idx_scan = 0
ORDER BY pg_relation_size(indexrelid) DESC;

-- Rebuild bloated indexes
REINDEX INDEX CONCURRENTLY ubec_main.idx_transactions_account_id;

-- Check index usage
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan as scans,
    pg_size_pretty(pg_relation_size(indexrelid)) as size
FROM pg_stat_user_indexes
WHERE schemaname = 'ubec_main'
ORDER BY idx_scan DESC
LIMIT 20;
```

**Query Performance Analysis:**

```sql
-- Enable query logging (postgresql.conf)
-- log_min_duration_statement = 1000  # Log queries > 1 second

-- Find slow queries
SELECT 
    userid::regrole,
    dbid,
    query,
    calls,
    total_time,
    mean_time,
    max_time,
    stddev_time
FROM pg_stat_statements
WHERE dbid = (SELECT oid FROM pg_database WHERE datname = 'ubec')
ORDER BY mean_time DESC
LIMIT 20;

-- Analyze specific query
EXPLAIN (ANALYZE, BUFFERS, VERBOSE) 
SELECT * FROM ubec_main.stellar_transactions 
WHERE account_id = 'GABC...' 
ORDER BY created_at DESC 
LIMIT 100;
```

### Data Integrity Checks

**Foreign Key Validation:**

```sql
-- Check orphaned records (transactions without accounts)
SELECT COUNT(*) as orphaned_transactions
FROM ubec_main.stellar_transactions t
LEFT JOIN ubec_main.stellar_accounts a ON t.account_id = a.account_id
WHERE a.account_id IS NULL;

-- Check balance consistency
SELECT 
    a.account_id,
    a.xlm_balance as account_xlm,
    COALESCE(SUM(b.balance), 0) as sum_balances
FROM ubec_main.stellar_accounts a
LEFT JOIN ubec_main.ubec_balances b ON a.account_id = b.account_id
GROUP BY a.account_id, a.xlm_balance
HAVING ABS(a.xlm_balance - COALESCE(SUM(b.balance), 0)) > 0.0001;
```

**Data Verification:**

```sql
-- Verify transaction count matches blockchain
SELECT 
    COUNT(*) as local_count,
    MAX(created_at) as latest_transaction
FROM ubec_main.stellar_transactions;

-- Check for gaps in sequence numbers
SELECT 
    t1.sequence + 1 as missing_start,
    MIN(t2.sequence) - 1 as missing_end
FROM ubec_main.stellar_transactions t1
LEFT JOIN ubec_main.stellar_transactions t2 ON t1.sequence + 1 = t2.sequence
WHERE t2.sequence IS NULL
GROUP BY t1.sequence
HAVING MIN(t2.sequence) IS NOT NULL
ORDER BY missing_start;
```

### Backup and Recovery Operations

**Hot Backup (No Downtime):**

```bash
#!/bin/bash
# Continuous archiving with WAL shipping

# postgresql.conf settings:
# wal_level = replica
# archive_mode = on
# archive_command = 'cp %p /var/backups/ubec/wal/%f'

# Perform base backup
pg_basebackup -D /var/backups/ubec/base -F tar -z -P -U ubec_admin

# Backup script with rotation
BACKUP_DIR=/var/backups/ubec
TIMESTAMP=$(date +%Y%m%d-%H%M%S)

pg_dump -U ubec_admin -F c -b -v -f $BACKUP_DIR/ubec-${TIMESTAMP}.dump ubec
gzip $BACKUP_DIR/ubec-${TIMESTAMP}.dump

# Verify backup
pg_restore --list $BACKUP_DIR/ubec-${TIMESTAMP}.dump.gz | head -20
```

**Point-in-Time Recovery (PITR):**

```bash
# Restore base backup
cd /var/lib/postgresql/15/main
rm -rf *
tar -xzf /var/backups/ubec/base/base.tar.gz

# Create recovery.conf (PostgreSQL 12+: postgresql.auto.conf)
cat > recovery.signal << EOF
restore_command = 'cp /var/backups/ubec/wal/%f %p'
recovery_target_time = '2025-11-02 10:30:00 UTC'
EOF

# Start PostgreSQL (will perform recovery)
sudo systemctl start postgresql

# Verify recovery
psql -U ubec_admin -d ubec -c "SELECT NOW();"
```

**Incremental Backup with pg_dump:**

```bash
# Schema-only backup (fast, small)
pg_dump -U ubec_admin -s -f ubec-schema-$(date +%Y%m%d).sql ubec

# Data-only backup by table
pg_dump -U ubec_admin -t ubec_main.stellar_transactions -a -f transactions.dump ubec

# Parallel dump (faster for large databases)
pg_dump -U ubec_admin -F d -j 4 -f ubec-parallel ubec
```

---

## Blockchain Integration

### Stellar Network Architecture

**Horizon API Endpoints:**

| Network | Horizon URL | Purpose |
|---------|-------------|---------|
| **Mainnet** | https://horizon.stellar.org | Production operations |
| **Testnet** | https://horizon-testnet.stellar.org | Testing |

**API Rate Limits:**
- **Public Horizon:** 3,600 requests/hour (72 requests/minute)
- **Custom Horizon:** Configurable (requires infrastructure)

### Rate Limiting Implementation

**Circuit Breaker Pattern:**

```python
class StellarClientService:
    def __init__(self):
        self._rate_limiter = RateLimiter(
            max_requests=3000,
            window_seconds=3600
        )
        self._circuit_breaker = CircuitBreaker(
            failure_threshold=5,
            recovery_timeout=60
        )
    
    async def _make_request(self, operation):
        # Wait for rate limit clearance
        await self._rate_limiter.acquire()
        
        try:
            # Check circuit breaker
            if self._circuit_breaker.is_open():
                raise ServiceUnavailableError("Circuit breaker open")
            
            # Make request
            result = await operation()
            
            # Record success
            self._circuit_breaker.record_success()
            
            return result
            
        except Exception as e:
            # Record failure
            self._circuit_breaker.record_failure()
            raise
```

**Rate Limit Monitoring:**

```bash
# Check current rate limit status
python main.py stellar --rate-limit-status

# Output:
# Stellar Horizon Rate Limit Status:
#   â€¢ Current: 2,456 / 3,000 requests used
#   â€¢ Remaining: 544 requests
#   â€¢ Window: 3,600 seconds
#   â€¢ Resets at: 2025-11-02 11:00:00 UTC
#   â€¢ Utilization: 81.9%
#   â€¢ Estimated time to exhaustion: 12 minutes

# View rate limit history
python main.py stellar --rate-limit-history --hours 24
```

**Handling Rate Limit Exhaustion:**

```python
# Automatic backoff strategy (built into client)
async def fetch_with_backoff(self, operation, max_retries=3):
    """Exponential backoff with jitter for rate limit handling."""
    for attempt in range(max_retries):
        try:
            return await operation()
        except RateLimitExceeded as e:
            if attempt == max_retries - 1:
                raise
            
            # Exponential backoff: 2^attempt * base_delay + jitter
            base_delay = 60  # 1 minute
            max_delay = 900  # 15 minutes
            jitter = random.uniform(0, 30)
            
            delay = min(
                (2 ** attempt) * base_delay + jitter,
                max_delay
            )
            
            logger.warning(
                f"Rate limit exceeded, retrying in {delay:.0f}s "
                f"(attempt {attempt + 1}/{max_retries})"
            )
            
            await asyncio.sleep(delay)
```

### Transaction Processing

**Transaction States:**

```sql
-- Transaction lifecycle states
CREATE TYPE transaction_state AS ENUM (
    'pending',      -- Submitted to blockchain
    'confirmed',    -- Included in ledger
    'failed',       -- Transaction failed
    'timeout'       -- No confirmation received
);

-- Monitor transaction states
SELECT 
    state,
    COUNT(*) as count,
    AVG(EXTRACT(EPOCH FROM (confirmed_at - created_at))) as avg_confirm_seconds
FROM ubec_main.stellar_transactions
WHERE created_at > NOW() - INTERVAL '24 hours'
GROUP BY state;
```

**Transaction Monitoring:**

```bash
# Monitor pending transactions
python main.py transactions --pending --watch

# Check transaction status
python main.py transactions --hash <transaction_hash>

# Retry failed transactions
python main.py transactions --retry-failed --since "1 hour ago"
```

**Streaming Blockchain Events:**

```python
# Built-in streaming capability
async def stream_operations(self, account_id: str, cursor: str = 'now'):
    """Stream operations for an account in real-time."""
    async for operation in self.server.operations() \
            .for_account(account_id) \
            .cursor(cursor) \
            .stream():
        
        # Process operation
        await self.process_operation(operation)
        
        # Update cursor for resume capability
        await self.db.execute(
            "UPDATE ubec_main.sync_state SET last_cursor = $1",
            operation['paging_token']
        )
```

### Account Management

**Account Discovery:**

```bash
# Discover accounts by asset
python main.py accounts --discover --asset UBEC

# Output: List of all accounts holding UBEC token

# Sync discovered accounts
python main.py sync --accounts <discovered-list>
```

**Account Health Monitoring:**

```sql
-- Check account health
SELECT 
    a.account_id,
    a.xlm_balance,
    a.trustline_count,
    COUNT(DISTINCT b.token_code) as token_count,
    SUM(b.balance) as total_balance,
    MAX(t.created_at) as last_transaction
FROM ubec_main.stellar_accounts a
LEFT JOIN ubec_main.ubec_balances b ON a.account_id = b.account_id
LEFT JOIN ubec_main.stellar_transactions t ON a.account_id = t.account_id
GROUP BY a.account_id, a.xlm_balance, a.trustline_count
HAVING a.xlm_balance < 1.5  -- Minimum reserve warning
ORDER BY a.xlm_balance ASC;
```

**Trustline Management:**

```python
# Check trustline status
async def check_trustlines(self, account_id: str) -> Dict[str, bool]:
    """Verify account has trustlines for all UBEC tokens."""
    account = await self.stellar.get_account(account_id)
    
    required_assets = ['UBEC', 'UBECrc', 'UBECgpi', 'UBECtt']
    trustlines = {}
    
    for balance in account['balances']:
        if balance['asset_type'] != 'native':
            asset_code = balance['asset_code']
            if asset_code in required_assets:
                trustlines[asset_code] = True
    
    return {asset: trustlines.get(asset, False) for asset in required_assets}
```

---

## Service Registry Internals

### Service Lifecycle Management

**Service States:**

```python
class ServiceState(Enum):
    UNINITIALIZED = "uninitialized"
    INITIALIZING = "initializing"
    READY = "ready"
    ERROR = "error"
    SHUTDOWN = "shutdown"
```

**Initialization Flow:**

```python
async def get(self, service_name: str):
    """Get service instance, initializing if necessary."""
    
    # Check if already initialized
    if service_name in self._services:
        return self._services[service_name]
    
    # Check if service is registered
    if service_name not in self._factories:
        raise ServiceNotFoundError(f"Service '{service_name}' not registered")
    
    # Mark as initializing
    self._states[service_name] = ServiceState.INITIALIZING
    
    try:
        # Get factory and dependencies
        factory = self._factories[service_name]
        deps = self._dependencies.get(service_name, [])
        
        # Initialize dependencies first (recursive)
        dep_services = {}
        for dep in deps:
            dep_services[dep] = await self.get(dep)
        
        # Create service instance
        service = await factory(**dep_services)
        
        # Store and mark ready
        self._services[service_name] = service
        self._states[service_name] = ServiceState.READY
        
        return service
        
    except Exception as e:
        self._states[service_name] = ServiceState.ERROR
        raise ServiceInitializationError(f"Failed to initialize '{service_name}': {e}")
```

### Health Check Patterns

**Three Health Check Patterns:**

1. **Database-Dependent Services:**

```python
async def health_check(self):
    return await ServiceHealthCheck.database_dependent_health(
        service_name='synchronizer',
        db_manager=self.db,
        is_initialized=self._initialized,
        operation_count=self._ops_count,
        error_count=self._error_count
    )
```

2. **API-Dependent Services:**

```python
async def health_check(self):
    return await ServiceHealthCheck.api_dependent_health(
        service_name='stellar_client',
        is_initialized=self._initialized,
        last_request_time=self._last_request,
        rate_limiter=self._rate_limiter
    )
```

3. **Config-Only Services:**

```python
def health_check(self):  # Note: Synchronous
    return ServiceHealthCheck.sync_basic_health_check(
        service_name='config',
        is_initialized=True,
        settings_count=len(self._settings)
    )
```

**Health Check Aggregation:**

```python
# System-wide health check
async def health_check(self, detailed=False):
    """Aggregate health from all services."""
    health_results = {}
    
    # Collect health from all initialized services
    for service_name, service in self._services.items():
        try:
            # Attempt async health check first
            if hasattr(service, 'health_check'):
                health_method = getattr(service, 'health_check')
                
                if asyncio.iscoroutinefunction(health_method):
                    # Async health check with timeout
                    health = await asyncio.wait_for(
                        health_method(),
                        timeout=5.0
                    )
                else:
                    # Sync health check (rare, config-only services)
                    health = health_method()
                
                health_results[service_name] = health
        
        except asyncio.TimeoutError:
            health_results[service_name] = {
                'status': 'unhealthy',
                'message': 'Health check timed out'
            }
        except Exception as e:
            health_results[service_name] = {
                'status': 'unhealthy',
                'message': str(e)
            }
    
    # Calculate overall status
    statuses = [h.get('status', 'unknown') for h in health_results.values()]
    
    if all(s == 'healthy' for s in statuses):
        overall = 'healthy'
    elif any(s == 'unhealthy' for s in statuses):
        overall = 'unhealthy'
    else:
        overall = 'degraded'
    
    return {
        'overall_status': overall,
        'services': health_results,
        'summary': {
            'total': len(health_results),
            'healthy': sum(1 for s in statuses if s == 'healthy'),
            'unhealthy': sum(1 for s in statuses if s == 'unhealthy'),
            'degraded': sum(1 for s in statuses if s == 'degraded')
        }
    }
```

### Dependency Resolution

**Topological Sorting:**

```python
def _resolve_dependencies(self):
    """Resolve service initialization order using topological sort."""
    
    # Build adjacency list
    graph = defaultdict(list)
    in_degree = defaultdict(int)
    
    for service, deps in self._dependencies.items():
        for dep in deps:
            graph[dep].append(service)
            in_degree[service] += 1
    
    # Kahn's algorithm for topological sort
    queue = deque([s for s in self._factories if in_degree[s] == 0])
    order = []
    
    while queue:
        service = queue.popleft()
        order.append(service)
        
        for dependent in graph[service]:
            in_degree[dependent] -= 1
            if in_degree[dependent] == 0:
                queue.append(dependent)
    
    # Check for circular dependencies
    if len(order) != len(self._factories):
        raise CircularDependencyError("Circular dependency detected")
    
    return order
```

---

## Data Synchronization

### Synchronization Architecture

**Three Synchronization Modes:**

1. **Incremental Sync:** Updates since last sync (default)
2. **Full Sync:** Complete resync from genesis
3. **Targeted Sync:** Specific accounts or time ranges

**Sync State Management:**

```sql
-- Sync state tracking
CREATE TABLE ubec_main.sync_state (
    id SERIAL PRIMARY KEY,
    account_id TEXT,
    last_sync_ledger INTEGER,
    last_sync_cursor TEXT,
    last_sync_time TIMESTAMPTZ,
    sync_status TEXT CHECK (sync_status IN ('synced', 'syncing', 'error')),
    error_count INTEGER DEFAULT 0,
    last_error TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Check sync status
SELECT 
    account_id,
    last_sync_time,
    sync_status,
    AGE(NOW(), last_sync_time) as sync_age,
    error_count
FROM ubec_main.sync_state
WHERE sync_status != 'synced'
   OR last_sync_time < NOW() - INTERVAL '1 hour'
ORDER BY last_sync_time ASC;
```

### Synchronization Procedures

**Incremental Sync:**

```python
async def sync_incremental(self, account_id: str):
    """Perform incremental sync from last known cursor."""
    
    # Get last cursor
    cursor = await self.db.fetchval(
        "SELECT last_sync_cursor FROM ubec_main.sync_state WHERE account_id = $1",
        account_id
    )
    
    # Default to 'now' if no cursor (first sync)
    cursor = cursor or 'now'
    
    # Fetch operations since cursor
    operations = await self.stellar.operations() \
        .for_account(account_id) \
        .cursor(cursor) \
        .order('asc') \
        .limit(200) \
        .call()
    
    # Process each operation
    for op in operations['_embedded']['records']:
        await self.process_operation(op)
        
        # Update cursor after each operation
        await self.db.execute(
            "UPDATE ubec_main.sync_state SET last_sync_cursor = $1 WHERE account_id = $2",
            op['paging_token'],
            account_id
        )
    
    # Mark sync complete
    await self.db.execute(
        """
        UPDATE ubec_main.sync_state 
        SET last_sync_time = NOW(), 
            sync_status = 'synced',
            error_count = 0
        WHERE account_id = $1
        """,
        account_id
    )
```

**Full Sync Strategy:**

```python
async def sync_full(self, account_id: str):
    """Perform complete resync from account creation."""
    
    logger.info(f"Starting full sync for {account_id}")
    
    # Clear existing data (with transaction)
    async with self.db.transaction():
        await self.db.execute(
            "DELETE FROM ubec_main.stellar_operations WHERE account_id = $1",
            account_id
        )
        await self.db.execute(
            "DELETE FROM ubec_main.stellar_transactions WHERE account_id = $1",
            account_id
        )
        await self.db.execute(
            "DELETE FROM ubec_main.ubec_balances WHERE account_id = $1",
            account_id
        )
    
    # Sync from beginning
    cursor = '0'  # Start from genesis
    total_ops = 0
    
    while True:
        # Fetch batch of operations
        operations = await self.stellar.operations() \
            .for_account(account_id) \
            .cursor(cursor) \
            .order('asc') \
            .limit(200) \
            .call()
        
        records = operations['_embedded']['records']
        
        if not records:
            break
        
        # Process batch
        for op in records:
            await self.process_operation(op)
            cursor = op['paging_token']
            total_ops += 1
        
        # Log progress
        if total_ops % 1000 == 0:
            logger.info(f"Synced {total_ops} operations for {account_id}")
        
        # Rate limiting pause
        await asyncio.sleep(0.1)
    
    logger.info(f"Full sync complete: {total_ops} operations for {account_id}")
```

### Handling Sync Failures

**Error Recovery:**

```python
async def sync_with_retry(self, account_id: str, max_retries=3):
    """Sync with automatic retry and exponential backoff."""
    
    for attempt in range(max_retries):
        try:
            # Mark as syncing
            await self.db.execute(
                "UPDATE ubec_main.sync_state SET sync_status = 'syncing' WHERE account_id = $1",
                account_id
            )
            
            # Perform sync
            await self.sync_incremental(account_id)
            
            return  # Success
            
        except Exception as e:
            logger.error(f"Sync failed for {account_id} (attempt {attempt + 1}): {e}")
            
            # Update error count
            await self.db.execute(
                """
                UPDATE ubec_main.sync_state 
                SET sync_status = 'error',
                    error_count = error_count + 1,
                    last_error = $1
                WHERE account_id = $2
                """,
                str(e),
                account_id
            )
            
            if attempt < max_retries - 1:
                # Exponential backoff
                delay = (2 ** attempt) * 10
                logger.info(f"Retrying in {delay}s...")
                await asyncio.sleep(delay)
            else:
                raise
```

**Monitoring Sync Performance:**

```sql
-- Sync performance metrics
SELECT 
    DATE_TRUNC('hour', last_sync_time) as sync_hour,
    COUNT(*) as accounts_synced,
    AVG(EXTRACT(EPOCH FROM (updated_at - created_at))) as avg_sync_duration,
    SUM(CASE WHEN sync_status = 'error' THEN 1 ELSE 0 END) as error_count
FROM ubec_main.sync_state
WHERE last_sync_time > NOW() - INTERVAL '24 hours'
GROUP BY sync_hour
ORDER BY sync_hour DESC;
```

---

## Performance Tuning

### Database Optimization

**Connection Pool Tuning:**

```python
# Optimal pool size calculation
# Formula: (2 * CPU_CORES) + effective_spindle_count

# For 8-core CPU with SSD:
DB_POOL_MIN = 5
DB_POOL_MAX = 20  # (2 * 8) + 4

# Monitor pool utilization
async def monitor_pool():
    pool_size = len(pool._holders)
    pool_free = pool.get_size() - pool.get_idle_size()
    utilization = (pool_free / pool_size) * 100
    
    if utilization > 80:
        logger.warning(f"Pool utilization high: {utilization:.1f}%")
```

**Query Optimization:**

```sql
-- Add appropriate indexes
CREATE INDEX CONCURRENTLY idx_transactions_account_created 
ON ubec_main.stellar_transactions (account_id, created_at DESC);

CREATE INDEX CONCURRENTLY idx_operations_type_created
ON ubec_main.stellar_operations (operation_type, created_at DESC);

-- Partial indexes for common queries
CREATE INDEX CONCURRENTLY idx_active_accounts
ON ubec_main.stellar_accounts (account_id)
WHERE last_modified > NOW() - INTERVAL '30 days';

-- Expression indexes
CREATE INDEX CONCURRENTLY idx_balances_significant
ON ubec_main.ubec_balances (account_id, token_code)
WHERE balance > 0.01;
```

**Configuration Tuning:**

```ini
# postgresql.conf optimizations for UBEC workload

# Memory settings (for 16GB RAM server)
shared_buffers = 4GB                 # 25% of RAM
effective_cache_size = 12GB          # 75% of RAM
maintenance_work_mem = 1GB           # For vacuum/index operations
work_mem = 64MB                      # Per query operation

# Checkpoint settings
checkpoint_completion_target = 0.9   # Spread out checkpoint writes
wal_buffers = 16MB
max_wal_size = 4GB
min_wal_size = 1GB

# Query planning
random_page_cost = 1.1               # For SSD
effective_io_concurrency = 200       # SSD concurrency

# Connections
max_connections = 100                # Application pool + admin

# Logging
log_min_duration_statement = 1000    # Log slow queries > 1s
log_line_prefix = '%t [%p]: [%l-1] user=%u,db=%d,app=%a,client=%h '
```

### Application Performance

**Async Batch Operations:**

```python
async def batch_sync_accounts(self, account_ids: List[str], concurrency=5):
    """Sync multiple accounts concurrently with controlled parallelism."""
    
    semaphore = asyncio.Semaphore(concurrency)
    
    async def sync_with_semaphore(account_id):
        async with semaphore:
            return await self.sync_incremental(account_id)
    
    # Execute in parallel batches
    tasks = [sync_with_semaphore(aid) for aid in account_ids]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Check for errors
    errors = [r for r in results if isinstance(r, Exception)]
    if errors:
        logger.error(f"Batch sync had {len(errors)} errors")
    
    return results
```

**Database Query Batching:**

```python
async def fetch_balances_batch(self, account_ids: List[str]):
    """Fetch balances for multiple accounts in single query."""
    
    # Single query instead of N queries
    query = """
        SELECT account_id, token_code, balance, last_modified
        FROM ubec_main.ubec_balances
        WHERE account_id = ANY($1)
    """
    
    rows = await self.db.fetch(query, account_ids)
    
    # Group by account
    balances = defaultdict(list)
    for row in rows:
        balances[row['account_id']].append(dict(row))
    
    return balances
```

**Caching Strategy:**

```python
from functools import lru_cache
from datetime import datetime, timedelta

class CachedDataService:
    def __init__(self):
        self._cache = {}
        self._cache_ttl = 300  # 5 minutes
    
    async def get_token_metrics(self, token_code: str):
        """Get token metrics with caching."""
        
        cache_key = f"metrics:{token_code}"
        
        # Check cache
        if cache_key in self._cache:
            cached_data, cached_time = self._cache[cache_key]
            
            if datetime.now() - cached_time < timedelta(seconds=self._cache_ttl):
                return cached_data
        
        # Cache miss - fetch from database
        metrics = await self._fetch_metrics_from_db(token_code)
        
        # Store in cache
        self._cache[cache_key] = (metrics, datetime.now())
        
        return metrics
```

### Monitoring Performance

**Application Metrics:**

```python
import time
from contextlib import asynccontextmanager

class PerformanceMonitor:
    def __init__(self):
        self._metrics = defaultdict(list)
    
    @asynccontextmanager
    async def measure(self, operation_name: str):
        """Context manager for timing operations."""
        start = time.perf_counter()
        
        try:
            yield
        finally:
            duration = time.perf_counter() - start
            self._metrics[operation_name].append(duration)
            
            # Log slow operations
            if duration > 1.0:
                logger.warning(f"Slow operation: {operation_name} took {duration:.2f}s")
    
    def get_stats(self, operation_name: str):
        """Get performance statistics."""
        timings = self._metrics[operation_name]
        
        if not timings:
            return None
        
        return {
            'count': len(timings),
            'min': min(timings),
            'max': max(timings),
            'avg': sum(timings) / len(timings),
            'p95': sorted(timings)[int(len(timings) * 0.95)],
            'p99': sorted(timings)[int(len(timings) * 0.99)]
        }

# Usage
monitor = PerformanceMonitor()

async with monitor.measure('sync_account'):
    await sync_account(account_id)

# Get stats
stats = monitor.get_stats('sync_account')
print(f"Average sync time: {stats['avg']:.3f}s, p95: {stats['p95']:.3f}s")
```

---

## Advanced Troubleshooting

### Diagnostic Tools

**Comprehensive System Diagnostic:**

```bash
# Run full diagnostic
python main.py diagnostic --comprehensive --output /tmp/diagnostic/

# Output includes:
# - System health snapshot
# - Database statistics
# - Blockchain connectivity
# - Service states
# - Recent errors
# - Performance metrics
```

**Database Diagnostics:**

```sql
-- Long-running queries
SELECT 
    pid,
    now() - query_start as duration,
    state,
    query
FROM pg_stat_activity
WHERE state != 'idle'
  AND query_start < now() - interval '30 seconds'
ORDER BY duration DESC;

-- Blocking queries
SELECT 
    blocked_locks.pid AS blocked_pid,
    blocked_activity.usename AS blocked_user,
    blocking_locks.pid AS blocking_pid,
    blocking_activity.usename AS blocking_user,
    blocked_activity.query AS blocked_statement,
    blocking_activity.query AS blocking_statement
FROM pg_catalog.pg_locks blocked_locks
JOIN pg_catalog.pg_stat_activity blocked_activity ON blocked_activity.pid = blocked_locks.pid
JOIN pg_catalog.pg_locks blocking_locks ON blocking_locks.locktype = blocked_locks.locktype
JOIN pg_catalog.pg_stat_activity blocking_activity ON blocking_activity.pid = blocking_locks.pid
WHERE NOT blocked_locks.granted
  AND blocking_locks.granted;

-- Table bloat
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename) - pg_relation_size(schemaname||'.'||tablename)) AS external_size
FROM pg_tables
WHERE schemaname = 'ubec_main'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
LIMIT 20;
```

### Network Troubleshooting

**Stellar Horizon Connectivity:**

```bash
# Test Horizon connectivity
curl -v https://horizon.stellar.org/

# Check Horizon health
curl https://horizon.stellar.org/ | jq '.horizon_version, .core_version'

# Test account endpoint
curl https://horizon.stellar.org/accounts/<ACCOUNT_ID> | jq '.balances'

# Stream operations (test streaming)
curl -N https://horizon.stellar.org/operations?cursor=now
```

**Network Latency Analysis:**

```bash
# Measure Horizon API latency
for i in {1..10}; do
    curl -w "@curl-format.txt" -o /dev/null -s https://horizon.stellar.org/
done

# curl-format.txt:
# time_namelookup: %{time_namelookup}\n
# time_connect: %{time_connect}\n
# time_starttransfer: %{time_starttransfer}\n
# time_total: %{time_total}\n

# Database latency
psql -U ubec_admin -d ubec -c "\timing on" -c "SELECT COUNT(*) FROM ubec_main.stellar_accounts;"
```

### Error Analysis

**Log Aggregation:**

```bash
# Extract and categorize errors
grep ERROR /var/log/ubec/application.log | \
    awk '{print $5}' | \
    sort | uniq -c | sort -rn

# Top error messages
grep ERROR /var/log/ubec/application.log | \
    cut -d' ' -f6- | \
    sort | uniq -c | sort -rn | head -20

# Error timeline
grep ERROR /var/log/ubec/application.log | \
    awk '{print $1}' | \
    cut -d'T' -f1 | \
    sort | uniq -c

# Service-specific errors
grep ERROR /var/log/ubec/application.log | grep "service=synchronizer"
```

**Database Error Tracking:**

```sql
-- Application errors from audit log
SELECT 
    DATE_TRUNC('hour', timestamp) as error_hour,
    action,
    COUNT(*) as error_count,
    array_agg(DISTINCT error_message) as error_types
FROM ubec_main.ubec_audit_log
WHERE action LIKE '%error%'
  AND timestamp > NOW() - INTERVAL '24 hours'
GROUP BY error_hour, action
ORDER BY error_hour DESC, error_count DESC;

-- Failed transactions
SELECT 
    DATE_TRUNC('hour', created_at) as failure_hour,
    COUNT(*) as failed_count,
    array_agg(DISTINCT error_message) as error_types
FROM ubec_main.stellar_transactions
WHERE state = 'failed'
  AND created_at > NOW() - INTERVAL '24 hours'
GROUP BY failure_hour
ORDER BY failure_hour DESC;
```

### Resolving Common Issues

**Issue: Database Deadlocks**

```sql
-- Identify deadlock patterns
SELECT 
    query,
    COUNT(*) as occurrence_count
FROM pg_stat_activity
WHERE wait_event_type = 'Lock'
GROUP BY query
ORDER BY occurrence_count DESC;

-- Solution: Ensure consistent lock ordering
-- BAD: Different order in different transactions
BEGIN;
UPDATE ubec_main.stellar_accounts SET ... WHERE account_id = 'A';
UPDATE ubec_main.ubec_balances SET ... WHERE account_id = 'B';
COMMIT;

-- GOOD: Same order in all transactions
BEGIN;
UPDATE ubec_main.stellar_accounts SET ... WHERE account_id IN ('A', 'B') ORDER BY account_id;
UPDATE ubec_main.ubec_balances SET ... WHERE account_id IN ('A', 'B') ORDER BY account_id;
COMMIT;
```

**Issue: Memory Leaks**

```python
# Monitor memory usage
import tracemalloc
import psutil

def monitor_memory():
    process = psutil.Process()
    memory_info = process.memory_info()
    
    print(f"RSS: {memory_info.rss / 1024 / 1024:.2f} MB")
    print(f"VMS: {memory_info.vms / 1024 / 1024:.2f} MB")
    
    # Tracemalloc for Python memory
    snapshot = tracemalloc.take_snapshot()
    top_stats = snapshot.statistics('lineno')
    
    for stat in top_stats[:10]:
        print(stat)

# Check for circular references
import gc
gc.collect()
print(f"Unreachable objects: {gc.collect()}")

# Common causes in async code:
# 1. Unclosed connections
# 2. Tasks not properly cancelled
# 3. Circular references in callbacks

# Solution: Use context managers and proper cleanup
async with registry:
    # Services auto-cleanup
    pass
```

---

## System Internals

### File Structure

```
ubec-protocol/
â”œâ”€â”€ main.py                    # SOLE ENTRY POINT
â”œâ”€â”€ core/
â”‚   â”œâ”€â”€ service_registry.py   # Service management
â”‚   â”œâ”€â”€ db/
â”‚   â”‚   â”œâ”€â”€ database_manager.py
â”‚   â”‚   â”œâ”€â”€ config_manager.py
â”‚   â”‚   â””â”€â”€ ubec_data_synchronizer.py
â”‚   â”œâ”€â”€ stellar/
â”‚   â”‚   â”œâ”€â”€ stellar_client.py
â”‚   â”‚   â””â”€â”€ rate_limiter.py
â”‚   â”œâ”€â”€ protocols/
â”‚   â”‚   â”œâ”€â”€ UBEC_protocol.py      # Air
â”‚   â”‚   â”œâ”€â”€ UBECrc_protocol.py    # Water
â”‚   â”‚   â”œâ”€â”€ UBECgpi_protocol.py   # Earth
â”‚   â”‚   â””â”€â”€ UBECtt_protocol.py    # Fire
â”‚   â”œâ”€â”€ analytics/
â”‚   â”‚   â”œâ”€â”€ analytics_service.py
â”‚   â”‚   â”œâ”€â”€ holonic_evaluator.py
â”‚   â”‚   â””â”€â”€ distribution_manager.py
â”‚   â””â”€â”€ utils/
â”‚       â”œâ”€â”€ service_health.py
â”‚       â””â”€â”€ logging_config.py
â”œâ”€â”€ database/
â”‚   â””â”€â”€ schema/
â”‚       â”œâ”€â”€ ubec_main_schema.sql
â”‚       â””â”€â”€ phenomenal_schema.sql
â”œâ”€â”€ .env                       # Configuration
â””â”€â”€ requirements.txt
```

### Configuration Management

**Database-Backed Configuration:**

```sql
-- Configuration table
CREATE TABLE ubec_main.ubec_config (
    id SERIAL PRIMARY KEY,
    config_key TEXT UNIQUE NOT NULL,
    config_value TEXT NOT NULL,
    config_type TEXT NOT NULL,  -- 'string', 'integer', 'boolean', 'json'
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Example configurations
INSERT INTO ubec_main.ubec_config (config_key, config_value, config_type, description)
VALUES 
    ('sync.batch_size', '200', 'integer', 'Number of operations per sync batch'),
    ('stellar.rate_limit', '3000', 'integer', 'Stellar API rate limit per hour'),
    ('evaluation.threshold', '0.5', 'float', 'Minimum holonic score threshold');

-- Retrieve configuration
SELECT config_value::integer 
FROM ubec_main.ubec_config 
WHERE config_key = 'sync.batch_size';
```

**Configuration Service:**

```python
class ConfigManager:
    """Database-backed configuration manager (Principle #4: Single Source of Truth)."""
    
    async def get(self, key: str, default=None):
        """Get configuration value."""
        row = await self.db.fetchrow(
            "SELECT config_value, config_type FROM ubec_main.ubec_config WHERE config_key = $1",
            key
        )
        
        if not row:
            return default
        
        # Type conversion
        value = row['config_value']
        config_type = row['config_type']
        
        if config_type == 'integer':
            return int(value)
        elif config_type == 'float':
            return float(value)
        elif config_type == 'boolean':
            return value.lower() in ('true', '1', 'yes')
        elif config_type == 'json':
            return json.loads(value)
        else:
            return value
    
    async def set(self, key: str, value, config_type: str, description: str = None):
        """Set configuration value."""
        await self.db.execute(
            """
            INSERT INTO ubec_main.ubec_config (config_key, config_value, config_type, description)
            VALUES ($1, $2, $3, $4)
            ON CONFLICT (config_key) 
            DO UPDATE SET 
                config_value = EXCLUDED.config_value,
                updated_at = NOW()
            """,
            key,
            str(value),
            config_type,
            description
        )
```

### Logging Architecture

**Structured Logging:**

```python
import logging
import json
from datetime import datetime

class StructuredLogger:
    """Structured logging for operational analysis."""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
    
    def log(self, level: str, message: str, **kwargs):
        """Log structured message."""
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': level,
            'service': self.logger.name,
            'message': message,
            **kwargs
        }
        
        # Log as JSON
        self.logger.log(
            getattr(logging, level.upper()),
            json.dumps(log_entry)
        )
    
    def operation(self, operation: str, duration: float, success: bool, **kwargs):
        """Log operation completion."""
        self.log(
            'INFO' if success else 'ERROR',
            f"Operation completed: {operation}",
            operation=operation,
            duration_ms=duration * 1000,
            success=success,
            **kwargs
        )

# Usage
logger = StructuredLogger('synchronizer')
logger.operation(
    operation='sync_account',
    duration=1.23,
    success=True,
    account_id='GABC...',
    operations_synced=150
)
```

**Log Analysis:**

```bash
# Parse JSON logs
cat /var/log/ubec/application.log | \
    jq -r 'select(.level == "ERROR") | "\(.timestamp) \(.service) \(.message)"'

# Operation performance
cat /var/log/ubec/application.log | \
    jq -r 'select(.operation) | [.operation, .duration_ms, .success] | @csv'

# Service health
cat /var/log/ubec/application.log | \
    jq -r 'select(.service) | .service' | \
    sort | uniq -c | sort -rn
```

---

## Development Operations

### Testing Framework

**Unit Tests:**

```python
# tests/test_synchronizer.py
import pytest
from unittest.mock import AsyncMock, MagicMock

@pytest.mark.asyncio
async def test_sync_account():
    """Test account synchronization."""
    
    # Mock dependencies
    mock_db = AsyncMock()
    mock_stellar = AsyncMock()
    
    # Create synchronizer
    sync = UBECDataSynchronizer(db=mock_db, stellar=mock_stellar)
    
    # Mock responses
    mock_stellar.operations.return_value.for_account.return_value.cursor.return_value.call = AsyncMock(
        return_value={'_embedded': {'records': []}}
    )
    
    # Execute test
    await sync.sync_incremental('GABC...')
    
    # Verify
    assert mock_stellar.operations.called
    assert mock_db.execute.called
```

**Integration Tests:**

```python
@pytest.mark.integration
@pytest.mark.asyncio
async def test_database_sync_integration():
    """Test full database synchronization workflow."""
    
    # Use test database
    db = await DatabaseManager.create(
        host='localhost',
        database='ubec_test',
        user='ubec_test'
    )
    
    try:
        # Initialize services
        async with ServiceRegistry() as registry:
            registry.register_instance('database', db)
            
            sync = await registry.get('synchronizer')
            
            # Perform sync
            result = await sync.sync_incremental('GABC...')
            
            # Verify data in database
            count = await db.fetchval(
                "SELECT COUNT(*) FROM ubec_main.stellar_operations WHERE account_id = $1",
                'GABC...'
            )
            
            assert count > 0
    finally:
        await db.close()
```

**Running Tests:**

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_synchronizer.py

# Run with coverage
pytest --cov=core tests/

# Run integration tests only
pytest -m integration tests/

# Run with verbose output
pytest -v tests/
```

### Code Quality Tools

**Linting:**

```bash
# Flake8
flake8 core/ --max-line-length=100

# PyLint
pylint core/ --disable=C0111,R0903

# Black (code formatting)
black core/ --line-length=100

# isort (import sorting)
isort core/ --profile black
```

**Type Checking:**

```bash
# MyPy
mypy core/ --strict

# Type hints example
from typing import List, Dict, Optional
import asyncpg

async def fetch_accounts(
    db: asyncpg.Pool,
    account_ids: List[str]
) -> Dict[str, Dict[str, any]]:
    """Fetch multiple accounts.
    
    Args:
        db: Database connection pool
        account_ids: List of account IDs to fetch
        
    Returns:
        Dictionary mapping account_id to account data
    """
    # Implementation
    pass
```

### Deployment Procedures

**Pre-Deployment Checklist:**

```bash
# 1. Run tests
pytest tests/ --cov=core

# 2. Check code quality
flake8 core/
pylint core/

# 3. Verify database migrations
psql -U ubec_admin -d ubec -f database/migrations/latest.sql --dry-run

# 4. Backup current deployment
tar -czf ubec-backup-$(date +%Y%m%d-%H%M%S).tar.gz /opt/ubec-protocol/

# 5. Backup database
pg_dump -U ubec_admin -F c ubec > ubec-backup-$(date +%Y%m%d-%H%M%S).dump
```

**Deployment Process:**

```bash
# 1. Pull latest code
cd /opt/ubec-protocol
git pull origin main

# 2. Update dependencies
source venv/bin/activate
pip install -r requirements.txt --upgrade

# 3. Run database migrations
psql -U ubec_admin -d ubec -f database/migrations/latest.sql

# 4. Restart services
sudo systemctl restart ubec-monitor.service

# 5. Verify health
python main.py health --detailed

# 6. Monitor logs
tail -f /var/log/ubec/application.log
```

**Rollback Procedure:**

```bash
# 1. Stop services
sudo systemctl stop ubec-monitor.service

# 2. Restore code
cd /opt/ubec-protocol
git checkout <previous-commit>

# 3. Restore dependencies
pip install -r requirements.txt

# 4. Restore database (if necessary)
pg_restore -U ubec_admin -d ubec -c ubec-backup-<timestamp>.dump

# 5. Restart services
sudo systemctl start ubec-monitor.service

# 6. Verify
python main.py health --detailed
```

---

## Emergency Procedures

### Critical Failure Response

**Incident Response Flowchart:**

```
1. DETECT: Alert triggered or user report
   â†“
2. ASSESS: Determine severity (P0-P3)
   â†“
3. NOTIFY: Alert on-call engineer
   â†“
4. INVESTIGATE: Gather diagnostics
   â†“
5. MITIGATE: Implement temporary fix
   â†“
6. RESOLVE: Deploy permanent solution
   â†“
7. DOCUMENT: Post-mortem analysis
```

**Severity Levels:**

| Priority | Description | Response Time | Example |
|----------|-------------|---------------|---------|
| **P0** | System down | 15 minutes | Database unreachable |
| **P1** | Critical degradation | 1 hour | Sync lag >4 hours |
| **P2** | Partial degradation | 4 hours | Single service failing |
| **P3** | Minor issue | 1 day | Slow query performance |

### Emergency Commands

**Database Emergency:**

```bash
# Check if PostgreSQL is running
sudo systemctl status postgresql

# Force restart PostgreSQL
sudo systemctl restart postgresql

# Check connections
psql -U postgres -c "SELECT * FROM pg_stat_activity WHERE datname = 'ubec';"

# Kill all connections (emergency only)
psql -U postgres -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = 'ubec' AND pid <> pg_backend_pid();"

# Start emergency read-only mode
psql -U postgres -c "ALTER DATABASE ubec SET default_transaction_read_only = on;"
```

**Application Emergency:**

```bash
# Force stop all Python processes
pkill -9 -f "python.*main.py"

# Check for zombie processes
ps aux | grep defunct

# Clear connection pool
python main.py database --reset-pool

# Emergency health check
python main.py health --emergency
```

**Blockchain Emergency:**

```bash
# Check Stellar network status
curl https://status.stellar.org/api/v2/status.json

# Switch to backup Horizon (if available)
# Update .env:
STELLAR_HORIZON_URL=https://horizon-backup.stellar.org

# Test new connection
curl https://horizon-backup.stellar.org/

# Restart with new configuration
sudo systemctl restart ubec-monitor.service
```

### Data Recovery

**Transaction Recovery:**

```sql
-- Find missing transactions
SELECT generate_series AS expected_id
FROM generate_series(
    (SELECT MIN(id) FROM ubec_main.stellar_transactions),
    (SELECT MAX(id) FROM ubec_main.stellar_transactions)
)
EXCEPT
SELECT id FROM ubec_main.stellar_transactions
ORDER BY expected_id;

-- Recover from backup
-- 1. Identify time range of missing data
SELECT MIN(created_at), MAX(created_at)
FROM ubec_main.stellar_transactions
WHERE created_at > '2025-11-01'
  AND created_at < '2025-11-02';

-- 2. Extract from backup
pg_restore -U ubec_admin -d ubec -t stellar_transactions -a backup.dump

-- 3. Verify recovery
SELECT COUNT(*) FROM ubec_main.stellar_transactions WHERE created_at BETWEEN '2025-11-01' AND '2025-11-02';
```

**Full System Recovery:**

```bash
#!/bin/bash
# Emergency full system recovery

echo "Starting emergency recovery..."

# 1. Stop all services
sudo systemctl stop ubec-monitor.service

# 2. Backup current state
timestamp=$(date +%Y%m%d-%H%M%S)
pg_dump -U ubec_admin -F c ubec > /tmp/pre-recovery-${timestamp}.dump

# 3. Restore from last known good backup
pg_restore -U ubec_admin -d ubec -c /var/backups/ubec/ubec-last-good.dump

# 4. Run database integrity check
psql -U ubec_admin -d ubec -c "SELECT COUNT(*) FROM ubec_main.stellar_accounts;"

# 5. Resync blockchain data
python main.py sync --full --accounts all

# 6. Verify health
python main.py health --detailed

# 7. Restart services
sudo systemctl start ubec-monitor.service

echo "Recovery complete. Check logs for verification."
```

---

## Appendix A: Database Schema Reference

### Core Tables

**stellar_accounts:**
```sql
CREATE TABLE ubec_main.stellar_accounts (
    id SERIAL PRIMARY KEY,
    account_id TEXT UNIQUE NOT NULL,
    sequence BIGINT,
    xlm_balance NUMERIC(20,7),
    trustline_count INTEGER,
    last_modified TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    INDEX idx_account_id (account_id),
    INDEX idx_last_modified (last_modified)
);
```

**stellar_transactions:**
```sql
CREATE TABLE ubec_main.stellar_transactions (
    id SERIAL PRIMARY KEY,
    transaction_hash TEXT UNIQUE NOT NULL,
    account_id TEXT REFERENCES ubec_main.stellar_accounts(account_id),
    sequence BIGINT,
    fee INTEGER,
    operation_count INTEGER,
    created_at TIMESTAMPTZ,
    state TEXT CHECK (state IN ('pending', 'confirmed', 'failed')),
    INDEX idx_tx_account (account_id, created_at),
    INDEX idx_tx_hash (transaction_hash),
    INDEX idx_tx_state (state)
);
```

**ubec_balances:**
```sql
CREATE TABLE ubec_main.ubec_balances (
    id SERIAL PRIMARY KEY,
    account_id TEXT REFERENCES ubec_main.stellar_accounts(account_id),
    token_code TEXT NOT NULL,
    issuer TEXT NOT NULL,
    balance NUMERIC(20,7),
    last_modified TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(account_id, token_code, issuer),
    INDEX idx_balance_account (account_id),
    INDEX idx_balance_token (token_code, balance)
);
```

---

## Appendix B: API Reference

### Service Registry API

```python
# Get service instance
service = await registry.get('service_name')

# Register service factory
registry.register_factory('name', factory_func, dependencies=['dep1', 'dep2'])

# Check health
health = await registry.health_check(detailed=True)

# Context manager
async with registry:
    # Auto-initialize and cleanup
    pass
```

### Database Manager API

```python
# Execute query
await db.execute("INSERT INTO ...")

# Fetch single row
row = await db.fetchrow("SELECT * FROM ...")

# Fetch multiple rows
rows = await db.fetch("SELECT * FROM ...")

# Fetch single value
count = await db.fetchval("SELECT COUNT(*) FROM ...")

# Transaction
async with db.transaction():
    await db.execute("INSERT ...")
    await db.execute("UPDATE ...")
```

### Synchronizer API

```python
# Incremental sync
await synchronizer.sync_incremental(account_id)

# Full sync
await synchronizer.sync_full(account_id)

# Batch sync
await synchronizer.sync_accounts([id1, id2, id3])

# Check sync status
status = await synchronizer.get_sync_status(account_id)
```

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-11-02 | UBEC DevOps | Initial release |

---

**End of Technical Operator Onboarding Guide**
