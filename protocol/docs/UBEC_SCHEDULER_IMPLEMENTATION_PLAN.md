# UBEC Protocol Scheduler Service - Implementation Plan

**Attribution**: This project uses the services of Claude and Anthropic PBC to inform our decisions and recommendations. This project was made possible with the assistance of Claude and Anthropic PBC.

---

## Executive Summary

Implement a comprehensive scheduler service that runs automated synchronization, analytics, and reporting when `python main.py serve` is initiated. This service will ensure continuous operation of the UBEC protocol with minimal manual intervention.

**Status**: Ready for implementation  
**Complexity**: Medium  
**Time Estimate**: 4-6 hours  
**Priority**: HIGH - Core operational requirement

---

## Design Principles Compliance

This implementation adheres strictly to all 12 design principles:

✅ **#1 Modular Design** - Self-contained scheduler service module  
✅ **#2 Service Pattern** - Registered in service registry, no standalone execution  
✅ **#3 Service Registry** - Full dependency injection via registry  
✅ **#4 Single Source of Truth** - Configuration stored in database scheduler_jobs table  
✅ **#5 Strict Async** - 100% async/await operations  
✅ **#6 No Sync Fallbacks** - Pure async implementation  
✅ **#7 Per-Asset Monitoring** - Individual task health tracking  
✅ **#8 No Duplicate Configuration** - Jobs defined once in database  
✅ **#9 Integrated Rate Limiting** - Respects existing rate limits  
✅ **#10 Separation of Concerns** - Scheduler orchestrates, doesn't execute  
✅ **#11 Comprehensive Documentation** - Full docstrings  
✅ **#12 Method Singularity** - Reuses existing service methods  

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     MAIN.PY SERVE                            │
│  (Single Entry Point - Principle #2)                         │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ├──> Service Registry Initialization
                  │    - Database Manager
                  │    - Configuration Service
                  │    - Stellar Client
                  │    - Protocol Services (Air/Water/Earth/Fire)
                  │    - Sync Service
                  │    - Analytics Service
                  │    - Holonic Evaluator
                  │    - Visualizer
                  │    - API Service
                  │    - [NEW] Scheduler Service ⬅ ADD THIS
                  │
                  ├──> FastAPI Server Start
                  │    - REST API endpoints active
                  │    - Health monitoring endpoints
                  │
                  └──> Scheduler Service Start ⬅ NEW
                       - Background task loop
                       - Job scheduling
                       - Periodic execution

┌─────────────────────────────────────────────────────────────┐
│              SCHEDULER SERVICE ARCHITECTURE                  │
└─────────────────────────────────────────────────────────────┘

                  ┌─────────────────────┐
                  │  Scheduler Service  │
                  │  (Background Loop)  │
                  └──────────┬──────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        v                    v                    v
  ┌──────────┐        ┌──────────┐        ┌──────────┐
  │   Sync   │        │Analytics │        │ Reports  │
  │  Jobs    │        │   Jobs   │        │   Jobs   │
  └────┬─────┘        └────┬─────┘        └────┬─────┘
       │                   │                    │
       v                   v                    v
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│ Sync Service │    │ Analytics    │    │ Visualizer   │
│ (existing)   │    │ Service      │    │ Service      │
└──────────────┘    └──────────────┘    └──────────────┘
```

---

## Database Schema Extension

The `scheduler_jobs` table already exists. We'll populate it with our scheduled jobs:

```sql
-- Schema already exists in database
CREATE TABLE IF NOT EXISTS ubec_main.scheduler_jobs (
    id SERIAL PRIMARY KEY,
    job_name VARCHAR(100) UNIQUE NOT NULL,
    schedule_interval VARCHAR(50) NOT NULL,  -- cron-like or interval
    next_run TIMESTAMP NOT NULL,
    last_run TIMESTAMP,
    job_function TEXT NOT NULL,  -- Python function reference
    parameters JSONB,
    enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

---

## Scheduled Jobs Definition

### Job 1: Blockchain Synchronization
**Frequency**: Every 5 minutes  
**Function**: `sync_service.sync_incremental()`  
**Purpose**: Keep blockchain data current

### Job 2: Analytics Update
**Frequency**: Every 15 minutes  
**Function**: `analytics_service.update_analytics()`  
**Purpose**: Refresh token and network metrics

### Job 3: Holonic Evaluation
**Frequency**: Every 30 minutes  
**Function**: `holonic_evaluator.evaluate_all()`  
**Purpose**: Assess Ubuntu principles compliance

### Job 4: Report Generation
**Frequency**: Every 6 hours  
**Function**: `visualizer.generate_html_report()`  
**Purpose**: Create visual dashboards

### Job 5: Protocol Health Check
**Frequency**: Every 10 minutes  
**Function**: `protocol_manager.check_all_health()`  
**Purpose**: Monitor protocol service health

### Job 6: Database Cleanup
**Frequency**: Daily at 2 AM  
**Function**: `database.cleanup_old_records()`  
**Purpose**: Archive old data, vacuum tables

---

## Implementation Steps

### Step 1: Create Scheduler Service Module

**File**: `services/scheduler/ubec_scheduler_service.py`

Key components:
- Job queue management
- Interval-based scheduling (no external dependencies)
- Task execution with error handling
- Health monitoring
- Database-backed job persistence

### Step 2: Register Scheduler Service

**File**: `main.py` (modify existing registration)

Add to `register_core_services()`:
```python
async def create_scheduler_service():
    from services.scheduler.ubec_scheduler_service import create_scheduler_service
    logger.info("  ├─ Scheduler Service: Automated task execution")
    return await create_scheduler_service(registry)

registry.register_factory(
    'scheduler',
    create_scheduler_service,
    dependencies=['database', 'sync', 'analytics', 'holonic', 'visualizer']
)
```

### Step 3: Modify serve Command

**File**: `main.py` (modify `handle_serve()`)

Add scheduler startup:
```python
async def handle_serve(registry, host, port, reload):
    # ... existing API server code ...
    
    # Start scheduler service
    scheduler = await registry.get('scheduler')
    await scheduler.start()
    
    # Run server
    await server.serve()
```

### Step 4: Populate Database with Jobs

**File**: `database/migrations/add_scheduler_jobs.sql`

Insert default job configurations.

### Step 5: Create Health Monitoring

Add scheduler health endpoint to API service:
```python
@app.get("/api/v1/scheduler/status")
async def scheduler_status():
    scheduler = await registry.get('scheduler')
    return await scheduler.get_status()
```

---

## Scheduler Service Implementation

### Core Features

1. **Interval-Based Scheduling**
   - No external dependencies (no APScheduler)
   - Simple asyncio.sleep loops
   - Configurable intervals from database

2. **Error Handling**
   - Try-catch for each job
   - Logging of failures
   - Automatic retry with backoff
   - Circuit breaker for persistent failures

3. **Health Monitoring**
   - Track last successful run per job
   - Monitor execution duration
   - Alert on failures
   - Export metrics

4. **Database Persistence**
   - Job configuration in scheduler_jobs table
   - Execution history tracking
   - Enable/disable jobs via database
   - Dynamic job reloading

5. **Graceful Shutdown**
   - Finish current jobs before exit
   - Save state to database
   - Clean task cancellation

---

## Job Execution Flow

```
┌─────────────────────────────────────────────────────┐
│          SCHEDULER MAIN LOOP (async)                 │
└─────────────────────────────────────────────────────┘
                        │
                        v
           ┌────────────────────────┐
           │ Load Jobs from DB      │
           │ (scheduler_jobs table) │
           └────────┬───────────────┘
                    │
                    v
        ┌───────────────────────────┐
        │ For Each Enabled Job:     │
        │   - Check if due to run   │
        │   - Check dependencies    │
        │   - Check circuit breaker │
        └────────┬──────────────────┘
                 │
                 v
     ┌───────────────────────────────┐
     │ Create Job Execution Task     │
     │ (asyncio.create_task)         │
     └────────┬──────────────────────┘
              │
              v
  ┌───────────────────────────────────┐
  │ Execute Job Function              │
  │   - Get service from registry     │
  │   - Call service method           │
  │   - Handle errors                 │
  │   - Record metrics                │
  └────────┬──────────────────────────┘
           │
           v
  ┌────────────────────────────────────┐
  │ Update Database                    │
  │   - Set last_run timestamp         │
  │   - Calculate next_run             │
  │   - Log execution result           │
  └────────────────────────────────────┘
```

---

## Configuration

### Environment Variables
```bash
# .env additions
SCHEDULER_ENABLED=true
SCHEDULER_CHECK_INTERVAL=60  # seconds
SCHEDULER_MAX_CONCURRENT_JOBS=5
SCHEDULER_ERROR_THRESHOLD=3
```

### Database Configuration
All job schedules defined in `scheduler_jobs` table following Principle #4 (Single Source of Truth).

---

## Testing Strategy

### Unit Tests
- Job loading from database
- Interval calculation
- Error handling
- Health check reporting

### Integration Tests
- Full scheduler lifecycle
- Job execution with real services
- Database persistence
- Graceful shutdown

### End-to-End Tests
- Start server with scheduler
- Verify jobs execute on schedule
- Check reports are generated
- Verify API endpoints work

---

## Monitoring and Observability

### Health Check Endpoint
```
GET /api/v1/scheduler/health

Response:
{
  "status": "healthy",
  "jobs_count": 6,
  "active_jobs": 2,
  "last_check": "2025-11-05T10:30:00Z",
  "jobs": [
    {
      "name": "sync_blockchain",
      "enabled": true,
      "last_run": "2025-11-05T10:25:00Z",
      "next_run": "2025-11-05T10:30:00Z",
      "success_rate": 0.98,
      "avg_duration_ms": 1234
    },
    ...
  ]
}
```

### Logging
```python
# Example log output
2025-11-05 10:25:00 INFO  Scheduler: Starting job 'sync_blockchain'
2025-11-05 10:25:02 INFO  Scheduler: Job 'sync_blockchain' completed (2.1s)
2025-11-05 10:25:02 INFO  Scheduler: Next run: 2025-11-05 10:30:00
```

### Metrics
- Jobs executed per hour
- Success/failure rates
- Execution duration percentiles
- Queue depth
- Error types and frequencies

---

## Error Handling

### Error Categories

1. **Transient Errors** (retry immediately)
   - Network timeouts
   - Database connection lost
   - Rate limit exceeded

2. **Recoverable Errors** (retry with backoff)
   - Service temporarily unavailable
   - Partial data sync failure
   - Report generation timeout

3. **Fatal Errors** (disable job)
   - Invalid job configuration
   - Missing dependencies
   - Persistent service failure

### Circuit Breaker Pattern

```python
if job.consecutive_failures >= ERROR_THRESHOLD:
    job.circuit_state = 'OPEN'
    job.enabled = False
    send_alert(f"Job {job.name} disabled after {ERROR_THRESHOLD} failures")
```

---

## Maintenance Operations

### Add New Job
```sql
INSERT INTO ubec_main.scheduler_jobs 
(job_name, schedule_interval, next_run, job_function, parameters, enabled)
VALUES 
('new_job', '3600', NOW(), 'module.function', '{}', true);
```

### Disable Job
```sql
UPDATE ubec_main.scheduler_jobs 
SET enabled = false 
WHERE job_name = 'job_to_disable';
```

### View Job Status
```sql
SELECT 
    job_name,
    last_run,
    next_run,
    enabled,
    (next_run - NOW()) as time_until_next_run
FROM ubec_main.scheduler_jobs
ORDER BY next_run;
```

---

## Benefits

1. **Automation**: No manual intervention required
2. **Reliability**: Self-healing with error recovery
3. **Observability**: Full visibility into operations
4. **Scalability**: Easy to add new scheduled tasks
5. **Maintainability**: Database-driven configuration
6. **Compliance**: Follows all 12 design principles

---

## Next Steps

1. ✅ Create `services/scheduler/ubec_scheduler_service.py`
2. ✅ Populate `scheduler_jobs` table with default jobs
3. ✅ Register scheduler in service registry
4. ✅ Modify `handle_serve()` to start scheduler
5. ✅ Add scheduler health endpoints
6. ✅ Create unit tests
7. ✅ Test with `python main.py serve`
8. ✅ Monitor and adjust intervals as needed

---

## Success Criteria

- [ ] Scheduler service starts with `main.py serve`
- [ ] All jobs execute on schedule
- [ ] Reports generate automatically
- [ ] Health endpoints return accurate status
- [ ] No manual intervention needed
- [ ] Logs show clear job execution history
- [ ] API remains responsive during job execution
- [ ] Graceful shutdown with CTRL+C

---

**Ready to implement!** 🚀
