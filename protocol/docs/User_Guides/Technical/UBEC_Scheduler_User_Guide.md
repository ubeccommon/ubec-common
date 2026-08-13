# UBEC Protocol Suite Scheduler - User Guide
**Automated Task Management for Continuous Operations**

**Version:** 1.0  
**Last Updated:** November 7, 2025  
**Target Audience:** System Administrators, Operators, Technical Users

---

## Attribution

This project uses the services of Claude and Anthropic PBC to inform our decisions and recommendations. This project was made possible with the assistance of Claude and Anthropic PBC.

---

## Table of Contents

1. [Overview](#overview)
2. [What the Scheduler Does](#what-the-scheduler-does)
3. [Scheduled Jobs & Frequencies](#scheduled-jobs--frequencies)
4. [Starting & Stopping the Scheduler](#starting--stopping-the-scheduler)
5. [Checking Scheduler Status](#checking-scheduler-status)
6. [Configuring Jobs](#configuring-jobs)
7. [Monitoring & Logs](#monitoring--logs)
8. [Troubleshooting](#troubleshooting)
9. [Advanced Operations](#advanced-operations)

---

## Overview

The UBEC Protocol Suite Scheduler is an **automated task management service** that runs critical system operations continuously in the background. It eliminates the need for manual intervention by executing periodic tasks like blockchain synchronization, analytics updates, holonic evaluations, and report generation on predefined schedules.

### Key Features

- ✅ **Database-Driven Configuration** - All jobs stored in database, no code changes needed
- ✅ **Automatic Error Recovery** - Circuit breaker pattern prevents cascade failures
- ✅ **Health Monitoring** - Per-job metrics and success tracking
- ✅ **Graceful Shutdown** - Completes running jobs before stopping
- ✅ **No External Dependencies** - Built on pure asyncio, no cron required
- ✅ **100% Async** - Non-blocking operations throughout
- ✅ **Respects Rate Limits** - Coordinates with Stellar API limits

### Architecture Compliance

The scheduler follows all 12 UBEC design principles:
- **Modular Design** - Self-contained service with clear boundaries
- **Service Pattern** - Accessed only through service registry
- **Single Source of Truth** - Jobs configured in database
- **Strict Async** - 100% async/await operations
- **No Duplicate Configuration** - Jobs defined once
- **Integrated Rate Limiting** - Respects all service limits

---

## What the Scheduler Does

The scheduler manages **6 core automated tasks** that keep the UBEC Protocol Suite operational:

### 1. Blockchain Synchronization
**Purpose:** Keeps local database in sync with Stellar blockchain  
**Impact:** Ensures all token balances, transactions, and account data are current  
**Without It:** System would show stale data, analytics would be outdated

### 2. Analytics Updates
**Purpose:** Refreshes token metrics, holder statistics, and network analytics  
**Impact:** Dashboard and reports show current state of the ecosystem  
**Without It:** Metrics would be frozen at last manual update

### 3. Holonic Evaluation
**Purpose:** Assesses all accounts against Ubuntu principles (autonomy, integration, reciprocity, mutualism, regeneration)  
**Impact:** Provides current scores for community health and alignment  
**Without It:** Holonic scores would become outdated, evaluations stale

### 4. Report Generation
**Purpose:** Creates visual dashboards with charts, graphs, and analysis  
**Impact:** Provides comprehensive HTML reports for stakeholders  
**Without It:** No automated reporting, manual generation required

### 5. Protocol Health Checks
**Purpose:** Monitors the four element protocols (Air, Water, Earth, Fire)  
**Impact:** Early detection of service degradation or failures  
**Without It:** Problems might go unnoticed until critical failure

### 6. Database Maintenance
**Purpose:** Archives old data, vacuums tables, optimizes performance  
**Impact:** Keeps database running smoothly, prevents bloat  
**Without It:** Database performance would degrade over time

---

## Scheduled Jobs & Frequencies

The following table shows all scheduled jobs, their execution frequencies, and what they do:

| Job Name | Frequency | Function Called | Purpose |
|----------|-----------|-----------------|---------|
| **sync_blockchain** | Every 5 minutes | `sync_service.sync_incremental()` | Keep blockchain data current with latest transactions |
| **update_analytics** | Every 15 minutes | `analytics_service.update_analytics()` | Refresh token statistics and holder metrics |
| **evaluate_holonic** | Every 30 minutes | `holonic_evaluator.evaluate_all()` | Assess Ubuntu principle compliance for all accounts |
| **generate_reports** | Every 6 hours | `visualizer.generate_html_report()` | Create comprehensive visual dashboards |
| **check_protocol_health** | Every 10 minutes | `protocol_manager.check_all_health()` | Monitor Air, Water, Earth, Fire protocol status |
| **database_cleanup** | Daily at 2 AM | `database.cleanup_old_records()` | Archive old data and vacuum tables |

### Job Frequency Details

#### High-Frequency Jobs (Every 5-10 minutes)
**sync_blockchain** and **check_protocol_health** run most frequently because:
- Blockchain data changes constantly
- Early detection of protocol issues is critical
- 5-10 minute intervals balance freshness with API rate limits

#### Medium-Frequency Jobs (Every 15-30 minutes)
**update_analytics** and **evaluate_holonic** run at moderate intervals because:
- Analytics calculations are computationally intensive
- Holonic evaluations require multiple database queries
- 15-30 minute intervals provide good balance of currency vs. load

#### Low-Frequency Jobs (Every 6 hours)
**generate_reports** runs infrequently because:
- Report generation is resource-intensive (creates multiple charts)
- Reports are for human consumption, don't need minute-by-minute updates
- 6-hour intervals (4 reports per day) provide adequate visibility

#### Daily Jobs (Once per day at 2 AM)
**database_cleanup** runs daily during off-peak hours because:
- Maintenance operations can be slow on large datasets
- 2 AM minimizes impact on users
- Daily cleanup prevents accumulation of stale data

### Total Scheduled Activity

In a typical day, the scheduler executes:
- **288 blockchain syncs** (every 5 minutes × 24 hours)
- **96 analytics updates** (every 15 minutes × 24 hours)
- **48 holonic evaluations** (every 30 minutes × 24 hours)
- **144 protocol health checks** (every 10 minutes × 24 hours)
- **4 report generations** (every 6 hours)
- **1 database cleanup** (daily at 2 AM)

**Total: ~581 automated job executions per day**

---

## Starting & Stopping the Scheduler

### Starting the Scheduler

The scheduler starts automatically when you run the UBEC server:

```bash
# Start the API server (automatically starts scheduler)
python main.py serve

# Expected output:
# ====================================================================
# STARTING UBEC PROTOCOL SERVER
# API: http://0.0.0.0:8000
# ====================================================================
# 
# 🔄 Initializing Scheduler Service...
# ✅ Scheduler started - automated tasks active
# ✅ API Server ready
# 📊 Swagger docs: http://0.0.0.0:8000/docs
# ⏰ Scheduler: Active (background tasks running)
# 
# 👉 Press Ctrl+C to stop
```

**What Happens During Startup:**

1. Service registry initializes all dependencies
2. Scheduler service loads job configuration from database
3. Scheduler validates all 6 jobs are properly configured
4. Background task loop starts checking for due jobs
5. Jobs begin executing according to their schedules

**Startup Verification:**

Check that scheduler started successfully:

```bash
# In another terminal (while server is running)
python main.py scheduler-status

# Expected output:
# ====================================================================
# SCHEDULER STATUS
# ====================================================================
# 
# ✅ Status: HEALTHY
# Running: Yes
# 
# Metrics:
#   Total Jobs: 6
#   Enabled: 6
#   Currently Running: 0
#   Success Rate: 98.5%
```

### Stopping the Scheduler

The scheduler stops gracefully when you stop the server:

```bash
# Press Ctrl+C in the terminal running the server

# Expected output:
# 
# ⚠️  Shutting down...
# Stopping scheduler...
# ✅ Scheduler stopped
# ✅ Server stopped
```

**What Happens During Shutdown:**

1. Scheduler receives stop signal
2. No new jobs are started
3. Running jobs are allowed to complete (with 60-second timeout)
4. Job state is saved to database
5. Service cleanly terminates

**Graceful Shutdown Timeout:**

If a job is still running after 60 seconds:
- Job is force-cancelled
- Partial results may be saved
- Job will be retried on next scheduler start

---

## Checking Scheduler Status

### Quick Status Check

View overall scheduler health:

```bash
python main.py scheduler-status
```

**Sample Output:**

```
====================================================================
SCHEDULER STATUS
====================================================================

✅ Status: HEALTHY
Running: Yes

Metrics:
  Total Jobs: 6
  Enabled: 6
  Currently Running: 2
  Success Rate: 97.8%

Jobs:

  ✅ sync_blockchain
     Next Run: 2025-11-07 14:35:00
     Success Rate: 99.2%
     Avg Duration: 1,234ms
     Circuit: ✅ closed

  ✅ update_analytics
     Next Run: 2025-11-07 14:40:00
     Success Rate: 98.5%
     Avg Duration: 3,567ms
     Circuit: ✅ closed

  ✅ evaluate_holonic
     Next Run: 2025-11-07 15:00:00
     Success Rate: 97.1%
     Avg Duration: 5,432ms
     Circuit: ✅ closed

  ✅ generate_reports
     Next Run: 2025-11-07 18:00:00
     Success Rate: 96.8%
     Avg Duration: 12,456ms
     Circuit: ✅ closed

  ✅ check_protocol_health
     Next Run: 2025-11-07 14:40:00
     Success Rate: 99.8%
     Avg Duration: 234ms
     Circuit: ✅ closed

  ✅ database_cleanup
     Next Run: 2025-11-08 02:00:00
     Success Rate: 100.0%
     Avg Duration: 8,765ms
     Circuit: ✅ closed

====================================================================
```

### Understanding Status Output

#### Overall Status
- **✅ HEALTHY** - All jobs operational, no issues
- **⚠️ DEGRADED** - Some jobs failing or disabled, system partially functional
- **❌ UNHEALTHY** - Multiple critical jobs failing, manual intervention required

#### Job Status Fields

**Next Run:** When the job will execute next  
- Shows timestamp in local time
- Calculated based on job's schedule interval

**Success Rate:** Percentage of successful executions  
- 100% = Perfect (no failures)
- 95-99% = Excellent (minor issues)
- 90-95% = Good (occasional problems)
- <90% = Concerning (investigate)

**Avg Duration:** Average execution time in milliseconds  
- Helps identify performance issues
- Compare against typical values:
  - sync_blockchain: 1,000-2,000ms
  - update_analytics: 3,000-5,000ms
  - evaluate_holonic: 4,000-6,000ms
  - generate_reports: 10,000-15,000ms
  - check_protocol_health: 200-500ms
  - database_cleanup: 5,000-10,000ms

**Circuit State:** Error protection status
- **✅ closed** - Normal operation
- **⚠️ half_open** - Testing recovery after failures
- **❌ open** - Too many failures, job disabled

### Detailed Job Inspection

View detailed information about a specific job:

```bash
# Query database directly for job details
psql -U ubec_admin -d ubec -c "
SELECT 
    job_name,
    schedule_interval,
    next_run,
    last_run,
    enabled,
    (next_run - NOW()) as time_until_next_run
FROM ubec_main.scheduler_jobs
WHERE job_name = 'sync_blockchain';
"
```

---

## Configuring Jobs

All job configuration is stored in the `scheduler_jobs` table in the database. This follows **Principle #4: Single Source of Truth**.

### Viewing All Jobs

```sql
-- Connect to database
psql -U ubec_admin -d ubec

-- View all jobs
SELECT 
    job_name,
    schedule_interval,
    enabled,
    last_run,
    next_run
FROM ubec_main.scheduler_jobs
ORDER BY next_run;
```

### Disabling a Job

Temporarily stop a job from running:

```sql
-- Disable job
UPDATE ubec_main.scheduler_jobs
SET enabled = false
WHERE job_name = 'generate_reports';

-- Verify
SELECT job_name, enabled FROM ubec_main.scheduler_jobs;
```

**Note:** Changes take effect on next scheduler check cycle (within 60 seconds).

### Re-enabling a Job

Resume a disabled job:

```sql
-- Enable job
UPDATE ubec_main.scheduler_jobs
SET 
    enabled = true,
    next_run = NOW() + INTERVAL '5 minutes'  -- Set next run time
WHERE job_name = 'generate_reports';
```

### Changing Job Frequency

Modify how often a job runs:

```sql
-- Change interval (in seconds)
-- Example: Change analytics from 15 minutes (900s) to 30 minutes (1800s)
UPDATE ubec_main.scheduler_jobs
SET schedule_interval = '1800'  -- 30 minutes in seconds
WHERE job_name = 'update_analytics';

-- Recalculate next run
UPDATE ubec_main.scheduler_jobs
SET next_run = NOW() + (schedule_interval || ' seconds')::INTERVAL
WHERE job_name = 'update_analytics';
```

**Supported Interval Formats:**

| Format | Example | Description |
|--------|---------|-------------|
| Seconds (integer) | `300` | 300 seconds (5 minutes) |
| Seconds with unit | `300s` | 300 seconds |
| Minutes | `15m` | 15 minutes |
| Hours | `6h` | 6 hours |
| Days | `1d` | 1 day |

### Adding a New Job

Add a custom scheduled task:

```sql
INSERT INTO ubec_main.scheduler_jobs 
(
    job_name,
    schedule_interval,
    next_run,
    job_function,
    parameters,
    enabled
)
VALUES 
(
    'custom_backup',                          -- Unique job name
    '3600',                                   -- Every hour (3600 seconds)
    NOW() + INTERVAL '1 hour',                -- First run in 1 hour
    'backup_service.create_backup',           -- Function to call
    '{"retention_days": 30}'::jsonb,          -- Optional parameters
    true                                      -- Enabled
);
```

**Required Fields:**
- `job_name` - Unique identifier (no spaces)
- `schedule_interval` - How often to run
- `next_run` - When to run first time
- `job_function` - Python function reference (service.method format)
- `enabled` - Whether job is active

### Removing a Job

Delete a job from the schedule:

```sql
-- Delete job permanently
DELETE FROM ubec_main.scheduler_jobs
WHERE job_name = 'custom_backup';

-- Or just disable it (safer - can re-enable later)
UPDATE ubec_main.scheduler_jobs
SET enabled = false
WHERE job_name = 'custom_backup';
```

### Reloading Configuration

After making changes, the scheduler automatically picks them up within 60 seconds. To force immediate reload:

```bash
# Restart the server
# Press Ctrl+C, then:
python main.py serve
```

---

## Monitoring & Logs

### Log Files

The scheduler writes detailed logs to the application log:

```bash
# View all scheduler logs
tail -f /var/log/ubec/application.log | grep "scheduler"

# View job execution logs
tail -f /var/log/ubec/application.log | grep "Executing job"

# View job completion logs
tail -f /var/log/ubec/application.log | grep "Job.*completed"

# View errors only
tail -f /var/log/ubec/application.log | grep "scheduler" | grep "ERROR"
```

### Log Format

**Successful Job Execution:**
```
2025-11-07 14:30:00 INFO  Executing job: sync_blockchain
2025-11-07 14:30:02 INFO  Job 'sync_blockchain' completed (2.1s)
2025-11-07 14:30:02 INFO  Next run: 2025-11-07 14:35:00
```

**Failed Job Execution:**
```
2025-11-07 14:30:00 INFO  Executing job: sync_blockchain
2025-11-07 14:30:05 ERROR Job 'sync_blockchain' failed: Connection timeout
2025-11-07 14:30:05 WARN  Consecutive failures: 1/3 (circuit still closed)
2025-11-07 14:30:05 INFO  Next run: 2025-11-07 14:35:00 (retry scheduled)
```

**Circuit Breaker Triggered:**
```
2025-11-07 14:45:00 ERROR Job 'sync_blockchain' failed: Connection timeout
2025-11-07 14:45:00 ERROR Consecutive failures: 3/3
2025-11-07 14:45:00 WARN  Circuit breaker OPENED for job 'sync_blockchain'
2025-11-07 14:45:00 WARN  Job 'sync_blockchain' disabled (too many failures)
2025-11-07 14:45:00 INFO  Will retry in 300 seconds (circuit recovery time)
```

### Monitoring Metrics

Track scheduler performance over time:

```sql
-- Job execution history
SELECT 
    job_name,
    COUNT(*) as total_runs,
    SUM(CASE WHEN success THEN 1 ELSE 0 END) as successful_runs,
    AVG(duration_ms) as avg_duration_ms,
    MAX(duration_ms) as max_duration_ms
FROM ubec_main.scheduler_execution_log
WHERE executed_at > NOW() - INTERVAL '24 hours'
GROUP BY job_name
ORDER BY job_name;

-- Recent failures
SELECT 
    job_name,
    executed_at,
    duration_ms,
    error_message
FROM ubec_main.scheduler_execution_log
WHERE success = false
    AND executed_at > NOW() - INTERVAL '7 days'
ORDER BY executed_at DESC;

-- Success rate trend
SELECT 
    DATE(executed_at) as date,
    job_name,
    COUNT(*) as total,
    SUM(CASE WHEN success THEN 1 ELSE 0 END) as successful,
    ROUND(100.0 * SUM(CASE WHEN success THEN 1 ELSE 0 END) / COUNT(*), 2) as success_rate
FROM ubec_main.scheduler_execution_log
WHERE executed_at > NOW() - INTERVAL '30 days'
GROUP BY DATE(executed_at), job_name
ORDER BY date DESC, job_name;
```

### Health Check Endpoint

When the server is running, check scheduler health via API:

```bash
# Check scheduler status via HTTP
curl http://localhost:8000/api/v1/scheduler/status

# Expected response:
{
  "status": "healthy",
  "jobs_count": 6,
  "active_jobs": 2,
  "last_check": "2025-11-07T14:30:00Z",
  "jobs": [
    {
      "name": "sync_blockchain",
      "enabled": true,
      "last_run": "2025-11-07T14:25:00Z",
      "next_run": "2025-11-07T14:30:00Z",
      "success_rate": 0.98,
      "avg_duration_ms": 1234
    },
    ...
  ]
}
```

---

## Troubleshooting

### Problem: Scheduler Not Starting

**Symptoms:**
```
⚠️  Failed to start scheduler: [error message]
Server will continue without scheduler
```

**Diagnosis:**

1. Check if scheduler_jobs table exists:
```sql
SELECT * FROM ubec_main.scheduler_jobs LIMIT 1;
```

2. Check for database connection issues:
```bash
python main.py health --detailed
```

3. Verify service dependencies:
```bash
python main.py health | grep -E "(sync|analytics|holonic|visualizer)"
```

**Solutions:**

**If table doesn't exist:**
```bash
# Run database migrations
psql -U ubec_admin -d ubec -f database/migrations/add_scheduler_jobs.sql
```

**If services are unhealthy:**
```bash
# Fix underlying service issues first
python main.py sync --status
python main.py health --detailed
```

**If permissions issue:**
```sql
-- Grant permissions to app user
GRANT SELECT, UPDATE ON ubec_main.scheduler_jobs TO ubec_app;
```

### Problem: Jobs Not Running

**Symptoms:**
- Jobs show in status but `last_run` never updates
- No job execution logs appearing

**Diagnosis:**

1. Check if jobs are enabled:
```sql
SELECT job_name, enabled, next_run 
FROM ubec_main.scheduler_jobs;
```

2. Check if next_run is in the past:
```sql
SELECT job_name, next_run, NOW(), (NOW() - next_run) as overdue
FROM ubec_main.scheduler_jobs
WHERE enabled = true;
```

3. Check for scheduler loop errors:
```bash
tail -100 /var/log/ubec/application.log | grep -i "scheduler loop"
```

**Solutions:**

**If jobs disabled:**
```sql
UPDATE ubec_main.scheduler_jobs
SET enabled = true;
```

**If next_run is way in the future:**
```sql
UPDATE ubec_main.scheduler_jobs
SET next_run = NOW()
WHERE enabled = true;
```

**If scheduler loop crashed:**
```bash
# Restart the server
pkill -f "python main.py serve"
python main.py serve
```

### Problem: Job Failing Repeatedly

**Symptoms:**
```
Job 'sync_blockchain' failed: [error]
Consecutive failures: 3/3
Circuit breaker OPENED for job 'sync_blockchain'
```

**Diagnosis:**

1. Check error details:
```sql
SELECT 
    executed_at,
    duration_ms,
    error_message,
    error_traceback
FROM ubec_main.scheduler_execution_log
WHERE job_name = 'sync_blockchain'
    AND success = false
ORDER BY executed_at DESC
LIMIT 5;
```

2. Test the job function manually:
```bash
# For sync_blockchain
python main.py sync --sync-type all

# For update_analytics
python main.py analytics --update

# For evaluate_holonic
python main.py holonic --evaluate-all
```

3. Check service health:
```bash
python main.py health --detailed
```

**Solutions:**

**If Stellar API issues:**
```bash
# Check rate limit status
python main.py stellar --rate-limit-status

# Wait for rate limit reset, or adjust sync interval:
UPDATE ubec_main.scheduler_jobs
SET schedule_interval = '600'  -- Increase to 10 minutes
WHERE job_name = 'sync_blockchain';
```

**If database issues:**
```bash
# Check database connections
python main.py database --pool-status

# Check for locks
psql -U ubec_admin -d ubec -c "
SELECT * FROM pg_stat_activity 
WHERE state = 'active' AND wait_event IS NOT NULL;
"
```

**If service dependency unavailable:**
```bash
# Restart required services
python main.py health
# Fix any unhealthy services first
```

**Reset circuit breaker:**
```sql
-- Clear failure count and re-enable job
UPDATE ubec_main.scheduler_jobs
SET 
    enabled = true,
    next_run = NOW() + INTERVAL '5 minutes'
WHERE job_name = 'sync_blockchain';
```

### Problem: Job Running Too Slowly

**Symptoms:**
- Job duration increasing over time
- Jobs backing up (next run keeps getting delayed)
- System performance degraded

**Diagnosis:**

1. Check execution times:
```sql
SELECT 
    job_name,
    AVG(duration_ms) as avg_ms,
    MAX(duration_ms) as max_ms,
    MIN(duration_ms) as min_ms
FROM ubec_main.scheduler_execution_log
WHERE executed_at > NOW() - INTERVAL '7 days'
    AND success = true
GROUP BY job_name
ORDER BY avg_ms DESC;
```

2. Check database query performance:
```bash
# Run slow query log analysis
psql -U ubec_admin -d ubec -c "
SELECT query, calls, mean_exec_time, max_exec_time
FROM pg_stat_statements
WHERE query LIKE '%scheduler%'
ORDER BY mean_exec_time DESC
LIMIT 10;
"
```

3. Check system resources:
```bash
# CPU and memory
htop

# Disk I/O
iostat -x 5

# Database connections
python main.py database --pool-status
```

**Solutions:**

**Optimize database:**
```sql
-- Analyze tables
ANALYZE ubec_main.scheduler_jobs;
ANALYZE ubec_main.stellar_transactions;
ANALYZE ubec_main.ubec_holonic_metrics;

-- Vacuum if needed
VACUUM ANALYZE;
```

**Reduce job frequency temporarily:**
```sql
-- Double the interval for slow jobs
UPDATE ubec_main.scheduler_jobs
SET schedule_interval = (schedule_interval::INT * 2)::TEXT
WHERE job_name IN ('evaluate_holonic', 'generate_reports');
```

**Limit data processing:**
```sql
-- Add parameters to limit scope
UPDATE ubec_main.scheduler_jobs
SET parameters = '{"limit": 1000}'::jsonb
WHERE job_name = 'evaluate_holonic';
```

### Problem: Scheduler Won't Stop

**Symptoms:**
- Ctrl+C pressed but scheduler still running
- Jobs continue executing after stop signal
- Server process hangs

**Diagnosis:**

1. Check for stuck jobs:
```bash
# View running processes
ps aux | grep python

# Check what the process is doing
strace -p [PID]
```

2. Check logs for shutdown sequence:
```bash
tail -50 /var/log/ubec/application.log
```

**Solutions:**

**Wait for graceful shutdown timeout (60 seconds):**
```bash
# Give it a full minute
# If still stuck after 60 seconds, force kill:
pkill -9 -f "python main.py serve"
```

**If specific job stuck:**
```sql
-- Mark job as failed so it doesn't block shutdown
UPDATE ubec_main.scheduler_jobs
SET last_run = NOW()
WHERE job_name = 'stuck_job_name';
```

---

## Advanced Operations

### Temporarily Pausing All Scheduled Jobs

Disable all jobs without stopping the scheduler:

```sql
-- Disable all jobs
UPDATE ubec_main.scheduler_jobs
SET enabled = false;

-- Verify
SELECT job_name, enabled FROM ubec_main.scheduler_jobs;
```

Resume jobs:

```sql
-- Re-enable all jobs
UPDATE ubec_main.scheduler_jobs
SET 
    enabled = true,
    next_run = NOW() + (schedule_interval || ' seconds')::INTERVAL;
```

### Running a Job Immediately

Force a job to run now instead of waiting for next scheduled time:

```sql
-- Set next_run to current time
UPDATE ubec_main.scheduler_jobs
SET next_run = NOW()
WHERE job_name = 'sync_blockchain';

-- Job will execute within 60 seconds (next scheduler check cycle)
```

Or run the underlying function directly:

```bash
# Blockchain sync
python main.py sync --sync-type all

# Analytics update
python main.py analytics --update

# Holonic evaluation
python main.py holonic --evaluate-all

# Report generation
python main.py visualizer --generate-report

# Protocol health check
python main.py protocol-health
```

### Backing Up Job Configuration

Save current job configuration:

```bash
# Export to SQL file
pg_dump -U ubec_admin -d ubec \
    --table=ubec_main.scheduler_jobs \
    --data-only \
    --file=scheduler_jobs_backup_$(date +%Y%m%d).sql

# Or export to CSV
psql -U ubec_admin -d ubec -c "
COPY ubec_main.scheduler_jobs TO '/tmp/scheduler_jobs.csv' CSV HEADER;
"
```

Restore job configuration:

```bash
# From SQL backup
psql -U ubec_admin -d ubec -f scheduler_jobs_backup_20251107.sql

# From CSV
psql -U ubec_admin -d ubec -c "
COPY ubec_main.scheduler_jobs FROM '/tmp/scheduler_jobs.csv' CSV HEADER;
"
```

### Setting Up Alerts

Create alerts for job failures:

```sql
-- Create alerting function (example)
CREATE OR REPLACE FUNCTION notify_job_failure()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.success = false THEN
        -- Send notification (implement your notification method)
        RAISE NOTICE 'Job % failed: %', NEW.job_name, NEW.error_message;
        
        -- You could also:
        -- INSERT INTO alert_queue (job_name, error) VALUES (NEW.job_name, NEW.error_message);
        -- Or call an external API
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Attach trigger
CREATE TRIGGER job_failure_alert
AFTER INSERT ON ubec_main.scheduler_execution_log
FOR EACH ROW
EXECUTE FUNCTION notify_job_failure();
```

### Performance Tuning

Adjust scheduler check interval:

```python
# In ubec_scheduler_service.py __init__ method
self.check_interval = 30  # Change from 60 to 30 seconds

# More responsive to job schedules, but slightly higher CPU
```

Adjust maximum concurrent jobs:

```python
# In ubec_scheduler_service.py __init__ method
self.max_concurrent_jobs = 10  # Change from 5 to 10

# Allows more jobs to run in parallel, but uses more resources
```

Adjust circuit breaker threshold:

```python
# In ubec_scheduler_service.py __init__ method
self.error_threshold = 5  # Change from 3 to 5

# Allows more failures before disabling job
```

---

## Frequently Asked Questions

### Q: Can I run the scheduler without the API server?

**A:** No. The scheduler is designed to run as part of the `serve` command. It's a background service that requires the full application context. However, you can run scheduled tasks manually using direct commands (e.g., `python main.py sync`).

### Q: What happens if two jobs try to run at the same time?

**A:** The scheduler respects the `max_concurrent_jobs` limit (default: 5). If more than 5 jobs are due simultaneously, they're queued and executed as slots become available. Jobs are executed in the order they became due.

### Q: How do I know if a job failed?

**A:** Check:
1. Scheduler status: `python main.py scheduler-status`
2. Application logs: `grep "failed" /var/log/ubec/application.log`
3. Database execution log: Query `scheduler_execution_log` table
4. Job circuit state: If circuit is "open", job has failed repeatedly

### Q: Can I change job frequencies while the scheduler is running?

**A:** Yes! Update the `scheduler_jobs` table directly. Changes take effect within 60 seconds (next scheduler check cycle). No restart required.

### Q: What happens if the server crashes during a job?

**A:** The job is marked as incomplete in the database. On restart, the scheduler will reschedule the job according to its normal interval. No manual intervention needed.

### Q: How much does the scheduler impact system performance?

**A:** Minimal. The scheduler itself uses <1% CPU when idle. Jobs consume resources proportional to their work:
- Lightweight jobs (health checks): Negligible impact
- Medium jobs (sync, analytics): 5-10% CPU during execution
- Heavy jobs (reports): Up to 25% CPU for brief periods

### Q: Can I schedule jobs at specific times (like "2 AM daily")?

**A:** The current implementation uses interval-based scheduling. For specific times, set `next_run` to the desired time and use a 24-hour interval (`86400` seconds). The job will run approximately at that time each day.

### Q: What happens if rate limits are exceeded?

**A:** The underlying services (especially `sync_blockchain`) have built-in rate limiting and circuit breaker patterns. If Stellar API rate limits are hit:
1. Service waits for rate limit reset
2. Job execution time increases
3. Job may timeout and retry on next cycle
4. No data loss occurs

### Q: Can I add custom jobs that run my own code?

**A:** Yes! Add a new service to the system, then reference it in a scheduler job:
```sql
INSERT INTO ubec_main.scheduler_jobs (job_name, schedule_interval, next_run, job_function)
VALUES ('my_custom_job', '3600', NOW(), 'my_service.my_method');
```

The referenced service must be registered in the service registry.

---

## Quick Reference

### Common Commands

```bash
# Start scheduler
python main.py serve

# Check status
python main.py scheduler-status

# View logs
tail -f /var/log/ubec/application.log | grep scheduler

# Manual job execution
python main.py sync --sync-type all
python main.py analytics --update
python main.py holonic --evaluate-all
```

### Common SQL Queries

```sql
-- View all jobs
SELECT * FROM ubec_main.scheduler_jobs;

-- Disable a job
UPDATE ubec_main.scheduler_jobs SET enabled = false WHERE job_name = 'job_name';

-- Run job immediately
UPDATE ubec_main.scheduler_jobs SET next_run = NOW() WHERE job_name = 'job_name';

-- View recent failures
SELECT * FROM ubec_main.scheduler_execution_log WHERE success = false ORDER BY executed_at DESC LIMIT 10;
```

### Job Reference Card

| Job | Frequency | Duration | Purpose |
|-----|-----------|----------|---------|
| sync_blockchain | 5 min | 1-2 sec | Sync with blockchain |
| update_analytics | 15 min | 3-5 sec | Refresh statistics |
| evaluate_holonic | 30 min | 4-6 sec | Score accounts |
| generate_reports | 6 hours | 10-15 sec | Create dashboards |
| check_protocol_health | 10 min | 0.2-0.5 sec | Monitor protocols |
| database_cleanup | Daily 2 AM | 5-10 sec | Maintain database |

---

## Support & Resources

### Getting Help

1. **Check Logs:** `tail -f /var/log/ubec/application.log | grep scheduler`
2. **Check Status:** `python main.py scheduler-status`
3. **Check System Health:** `python main.py health --detailed`
4. **Review Documentation:** This guide + implementation plan

### Related Documentation

- **Main System Guide:** `/docs/User_Guides/SYSTEM_ADMINISTRATOR_ONBOARDING_GUIDE.md`
- **Technical Operator Guide:** `/docs/User_Guides/TECHNICAL_OPERATOR_ONBOARDING_GUIDE.md`
- **Implementation Plan:** `/docs/UBEC_SCHEDULER_IMPLEMENTATION_PLAN.md`
- **Main.py Integration:** `/docs/MAIN_PY_INTEGRATION_GUIDE.md`

### Version Information

**Scheduler Version:** 1.0.3  
**Last Updated:** November 7, 2025  
**Compatibility:** UBEC Protocol Suite v13.0.0+

---

*This guide covers all aspects of the UBEC Protocol Suite Scheduler. For questions not covered here, consult the technical documentation or contact the development team.*
