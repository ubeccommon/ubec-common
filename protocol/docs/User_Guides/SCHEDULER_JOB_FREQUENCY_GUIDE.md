# UBEC Scheduler Job Frequency Guide

*This project uses the services of Claude and Anthropic PBC to inform our decisions and recommendations. This project was made possible with the assistance of Claude and Anthropic PBC.*

**Version:** 1.0.0  
**Last Updated:** November 20, 2025

---

## Table of Contents

1. [Overview](#overview)
2. [Supported Interval Formats](#supported-interval-formats)
3. [Current Job Configuration](#current-job-configuration)
4. [Viewing Job Frequencies](#viewing-job-frequencies)
5. [Changing Job Frequencies](#changing-job-frequencies)
6. [Common Interval Examples](#common-interval-examples)
7. [Recommended Frequencies](#recommended-frequencies)
8. [Best Practices](#best-practices)
9. [SQL Scripts](#sql-scripts)
10. [Troubleshooting](#troubleshooting)

---

## Overview

The UBEC Protocol Scheduler manages automated tasks through database-driven job configuration. Job execution frequency is controlled by the `schedule_interval` column in the `ubec_main.scheduler_jobs` table.

**Key Features:**
- ✅ Hot-reloadable: Changes take effect within 60 seconds (no restart required)
- ✅ Multiple format support: Seconds, minutes, hours, days
- ✅ Database as single source of truth (Design Principle #4)
- ✅ Real-time monitoring through `next_run` calculations

**Database Location:**
```
Database: ubec
Schema: ubec_main
Table: scheduler_jobs
```

---

## Supported Interval Formats

The scheduler supports multiple interval formats for flexibility:

| Format | Syntax | Example | Equivalent Seconds |
|--------|--------|---------|-------------------|
| **Raw Seconds** | Integer string | `"300"` | 300 seconds |
| **Seconds with Unit** | Number + `s` | `"300s"` | 300 seconds |
| **Minutes** | Number + `m` | `"15m"` | 900 seconds |
| **Hours** | Number + `h` | `"6h"` | 21,600 seconds |
| **Days** | Number + `d` | `"1d"` | 86,400 seconds |

**Examples:**
```sql
-- All of these are equivalent to 5 minutes:
schedule_interval = '300'   -- Raw seconds
schedule_interval = '300s'  -- Seconds with unit
schedule_interval = '5m'    -- Minutes

-- All of these are equivalent to 1 hour:
schedule_interval = '3600'  -- Raw seconds
schedule_interval = '60m'   -- Minutes
schedule_interval = '1h'    -- Hours
```

---

## Current Job Configuration

Default job frequencies in the UBEC Protocol Suite:

| Job Name | Interval | Frequency | Purpose |
|----------|----------|-----------|---------|
| `blockchain_sync` | `300` | Every 5 minutes | Sync blockchain data from Stellar |
| `analytics_update` | `900` | Every 15 minutes | Update ecosystem metrics |
| `holonic_evaluation` | `1800` | Every 30 minutes | Evaluate Ubuntu principles |
| `protocol_health_check` | `600` | Every 10 minutes | Monitor service health |
| `report_generation` | `21600` | Every 6 hours | Generate HTML reports |
| `database_cleanup` | `86400` | Daily at 2 AM | Archive old data, vacuum |

**Daily Execution Totals:**
- Blockchain syncs: 288 executions/day
- Analytics updates: 96 executions/day
- Holonic evaluations: 48 executions/day
- Health checks: 144 executions/day
- Reports: 4 executions/day
- Database cleanup: 1 execution/day

**Total:** ~581 automated job executions per day

---

## Viewing Job Frequencies

### View All Jobs

```bash
psql -U ubec_admin -d ubec -h localhost << 'EOSQL'
SELECT 
    job_name,
    schedule_interval,
    enabled,
    last_run,
    next_run,
    (next_run - NOW()) as time_until_next_run
FROM ubec_main.scheduler_jobs
ORDER BY job_name;
EOSQL
```

**Expected Output:**
```
       job_name        | schedule_interval | enabled |         last_run          |         next_run          | time_until_next_run
-----------------------+-------------------+---------+---------------------------+---------------------------+---------------------
 analytics_update      | 900              | t       | 2025-11-20 04:15:04.161   | 2025-11-20 04:30:04.161   | 00:14:32.456
 blockchain_sync       | 300              | t       | 2025-11-20 04:15:03.993   | 2025-11-20 04:20:03.993   | 00:04:32.456
 holonic_evaluation    | 1800             | t       | 2025-11-20 04:15:11.356   | 2025-11-20 04:45:11.356   | 00:29:39.456
 protocol_health_check | 600              | t       | 2025-11-20 04:15:04.094   | 2025-11-20 04:25:04.094   | 00:09:32.456
 report_generation     | 21600            | t       | 2025-11-20 04:15:04.091   | 2025-11-20 10:15:04.091   | 05:59:32.456
```

### View Single Job

```bash
psql -U ubec_admin -d ubec -h localhost << 'EOSQL'
SELECT 
    job_name,
    schedule_interval,
    enabled,
    last_run,
    next_run
FROM ubec_main.scheduler_jobs
WHERE job_name = 'blockchain_sync';
EOSQL
```

### Check Execution History

```bash
psql -U ubec_admin -d ubec -h localhost << 'EOSQL'
-- View recent executions for a job
SELECT 
    job_name,
    executed_at,
    duration_ms,
    success,
    error_message
FROM ubec_main.scheduler_execution_log
WHERE job_name = 'blockchain_sync'
ORDER BY executed_at DESC
LIMIT 10;
EOSQL
```

---

## Changing Job Frequencies

### Important Notes Before Changing

✅ **Changes are live immediately** - No restart required  
⚠️ **Respect rate limits** - Stellar API: 3 requests/second  
⚠️ **Consider system load** - Very frequent jobs increase CPU/memory usage  
✅ **Minimum interval** - Recommended: 60 seconds (1 minute)

### Basic Frequency Change

```bash
# Change blockchain sync to 10 minutes
psql -U ubec_admin -d ubec -h localhost << 'EOSQL'
UPDATE ubec_main.scheduler_jobs
SET schedule_interval = '600'  -- 10 minutes in seconds
WHERE job_name = 'blockchain_sync';

-- Verify the change
SELECT job_name, schedule_interval FROM ubec_main.scheduler_jobs 
WHERE job_name = 'blockchain_sync';
EOSQL
```

### Change Multiple Jobs at Once

```bash
# Reduce frequency for all resource-intensive jobs
psql -U ubec_admin -d ubec -h localhost << 'EOSQL'
-- Double the interval for sync and analytics
UPDATE ubec_main.scheduler_jobs
SET schedule_interval = (schedule_interval::INTEGER * 2)::TEXT
WHERE job_name IN ('blockchain_sync', 'analytics_update', 'holonic_evaluation');

-- Verify changes
SELECT job_name, schedule_interval 
FROM ubec_main.scheduler_jobs 
WHERE job_name IN ('blockchain_sync', 'analytics_update', 'holonic_evaluation');
EOSQL
```

### Change with Immediate Execution

```bash
# Change interval AND trigger immediate run
psql -U ubec_admin -d ubec -h localhost << 'EOSQL'
UPDATE ubec_main.scheduler_jobs
SET schedule_interval = '1800',  -- New: 30 minutes
    next_run = NOW()              -- Run immediately
WHERE job_name = 'analytics_update';
EOSQL
```

---

## Common Interval Examples

### High-Frequency Jobs (1-5 minutes)

```sql
-- Every 1 minute (use sparingly - high load)
UPDATE ubec_main.scheduler_jobs
SET schedule_interval = '60'
WHERE job_name = 'critical_monitoring';

-- Every 2 minutes
UPDATE ubec_main.scheduler_jobs
SET schedule_interval = '120'
WHERE job_name = 'health_check';

-- Every 5 minutes (blockchain sync default)
UPDATE ubec_main.scheduler_jobs
SET schedule_interval = '300'
WHERE job_name = 'blockchain_sync';
```

### Medium-Frequency Jobs (10-30 minutes)

```sql
-- Every 10 minutes (protocol health check default)
UPDATE ubec_main.scheduler_jobs
SET schedule_interval = '600'
WHERE job_name = 'protocol_health_check';

-- Every 15 minutes (analytics default)
UPDATE ubec_main.scheduler_jobs
SET schedule_interval = '15m'
WHERE job_name = 'analytics_update';

-- Every 30 minutes (holonic evaluation default)
UPDATE ubec_main.scheduler_jobs
SET schedule_interval = '30m'
WHERE job_name = 'holonic_evaluation';
```

### Low-Frequency Jobs (1-12 hours)

```sql
-- Every hour
UPDATE ubec_main.scheduler_jobs
SET schedule_interval = '1h'
WHERE job_name = 'hourly_summary';

-- Every 3 hours
UPDATE ubec_main.scheduler_jobs
SET schedule_interval = '3h'
WHERE job_name = 'data_aggregation';

-- Every 6 hours (report generation default)
UPDATE ubec_main.scheduler_jobs
SET schedule_interval = '6h'
WHERE job_name = 'report_generation';

-- Every 12 hours
UPDATE ubec_main.scheduler_jobs
SET schedule_interval = '12h'
WHERE job_name = 'deep_analysis';
```

### Daily Jobs

```sql
-- Daily (24 hours)
UPDATE ubec_main.scheduler_jobs
SET schedule_interval = '1d',
    next_run = (CURRENT_DATE + INTERVAL '1 day' + TIME '02:00:00')  -- Next 2 AM
WHERE job_name = 'database_cleanup';

-- Daily at specific time (alternative method)
UPDATE ubec_main.scheduler_jobs
SET schedule_interval = '86400',  -- 24 hours in seconds
    next_run = date_trunc('day', NOW()) + INTERVAL '26 hours'  -- Next day at 2 AM
WHERE job_name = 'nightly_backup';
```

---

## Recommended Frequencies

### By Job Type

| Job Type | Recommended Interval | Rationale |
|----------|---------------------|-----------|
| **Blockchain Sync** | 5-10 minutes (`300`-`600`) | Balance freshness vs API limits |
| **Analytics** | 15-30 minutes (`900`-`1800`) | Computationally intensive |
| **Holonic Evaluation** | 30-60 minutes (`1800`-`3600`) | Complex calculations |
| **Health Checks** | 5-10 minutes (`300`-`600`) | Early issue detection |
| **Reports** | 6-12 hours (`6h`-`12h`) | Resource-intensive, human consumption |
| **Database Maintenance** | Daily (`1d`) | Maintenance during off-peak |

### By System Load

| System Load | Blockchain Sync | Analytics | Holonic Eval | Health Check |
|-------------|----------------|-----------|--------------|--------------|
| **High Load** | 10 min (`600`) | 30 min (`1800`) | 60 min (`3600`) | 10 min (`600`) |
| **Normal** | 5 min (`300`) | 15 min (`900`) | 30 min (`1800`) | 10 min (`600`) |
| **Low Load** | 3 min (`180`) | 10 min (`600`) | 15 min (`900`) | 5 min (`300`) |

### By Network Activity

| Network Activity | Sync Frequency | Rationale |
|-----------------|----------------|-----------|
| **High** (>100 tx/hour) | 3-5 minutes | Keep data current |
| **Medium** (10-100 tx/hour) | 5-10 minutes | Standard monitoring |
| **Low** (<10 tx/hour) | 10-15 minutes | Reduce unnecessary syncs |

---

## Best Practices

### 1. Start Conservative, Then Optimize

```sql
-- Start with longer intervals
UPDATE ubec_main.scheduler_jobs
SET schedule_interval = '900'  -- 15 minutes
WHERE job_name = 'new_job';

-- Monitor performance for 24 hours
-- Then adjust based on actual needs
```

### 2. Respect API Rate Limits

**Stellar Horizon API:** 3,600 requests/hour (3 requests/second)

```sql
-- Calculate safe sync frequency:
-- If sync makes ~10 API calls per execution
-- Max frequency: 3600 requests/hour ÷ 10 calls = 360 executions/hour
-- Safe interval: 3600 seconds ÷ 360 = 10 seconds minimum

-- Recommended: 5 minutes (300 seconds) for safety margin
UPDATE ubec_main.scheduler_jobs
SET schedule_interval = '300'
WHERE job_name = 'blockchain_sync';
```

### 3. Stagger Job Execution

```sql
-- Avoid all jobs running simultaneously
-- Offset next_run times by a few minutes

-- Job 1: Runs at :00
UPDATE ubec_main.scheduler_jobs
SET next_run = date_trunc('hour', NOW()) + INTERVAL '1 hour'
WHERE job_name = 'job_1';

-- Job 2: Runs at :05
UPDATE ubec_main.scheduler_jobs
SET next_run = date_trunc('hour', NOW()) + INTERVAL '1 hour 5 minutes'
WHERE job_name = 'job_2';

-- Job 3: Runs at :10
UPDATE ubec_main.scheduler_jobs
SET next_run = date_trunc('hour', NOW()) + INTERVAL '1 hour 10 minutes'
WHERE job_name = 'job_3';
```

### 4. Monitor Job Performance

```sql
-- Check average execution times
SELECT 
    job_name,
    AVG(duration_ms) as avg_ms,
    MAX(duration_ms) as max_ms,
    COUNT(*) as executions
FROM ubec_main.scheduler_execution_log
WHERE executed_at > NOW() - INTERVAL '24 hours'
    AND success = true
GROUP BY job_name
ORDER BY avg_ms DESC;

-- Adjust intervals if jobs are slow
UPDATE ubec_main.scheduler_jobs
SET schedule_interval = (schedule_interval::INTEGER * 2)::TEXT
WHERE job_name IN (
    SELECT job_name 
    FROM ubec_main.scheduler_execution_log
    WHERE duration_ms > 10000  -- Jobs taking >10 seconds
    GROUP BY job_name
);
```

### 5. Use Appropriate Units

```sql
-- ✅ GOOD: Clear intent
UPDATE ubec_main.scheduler_jobs
SET schedule_interval = '5m'   -- Obviously 5 minutes
WHERE job_name = 'quick_check';

UPDATE ubec_main.scheduler_jobs
SET schedule_interval = '6h'   -- Obviously 6 hours
WHERE job_name = 'reports';

-- ❌ AVOID: Less readable
UPDATE ubec_main.scheduler_jobs
SET schedule_interval = '300'  -- Is this minutes? seconds?
WHERE job_name = 'quick_check';
```

---

## SQL Scripts

### Script 1: View All Job Frequencies with Conversions

Save as: `view_job_frequencies.sql`

```sql
-- ============================================================================
-- View Job Frequencies with Human-Readable Conversions
-- ============================================================================

SELECT 
    job_name,
    schedule_interval as raw_interval,
    CASE 
        WHEN schedule_interval ~ '^[0-9]+$' THEN 
            CASE
                WHEN schedule_interval::INTEGER >= 86400 THEN 
                    (schedule_interval::INTEGER / 86400)::TEXT || ' days'
                WHEN schedule_interval::INTEGER >= 3600 THEN 
                    (schedule_interval::INTEGER / 3600)::TEXT || ' hours'
                WHEN schedule_interval::INTEGER >= 60 THEN 
                    (schedule_interval::INTEGER / 60)::TEXT || ' minutes'
                ELSE 
                    schedule_interval || ' seconds'
            END
        ELSE schedule_interval
    END as human_readable,
    enabled,
    last_run,
    next_run,
    AGE(next_run, NOW()) as time_until_next
FROM ubec_main.scheduler_jobs
ORDER BY 
    CASE 
        WHEN schedule_interval ~ '^[0-9]+$' THEN schedule_interval::INTEGER
        WHEN schedule_interval ~ '^[0-9]+s$' THEN SUBSTRING(schedule_interval FROM 1 FOR LENGTH(schedule_interval)-1)::INTEGER
        WHEN schedule_interval ~ '^[0-9]+m$' THEN SUBSTRING(schedule_interval FROM 1 FOR LENGTH(schedule_interval)-1)::INTEGER * 60
        WHEN schedule_interval ~ '^[0-9]+h$' THEN SUBSTRING(schedule_interval FROM 1 FOR LENGTH(schedule_interval)-1)::INTEGER * 3600
        WHEN schedule_interval ~ '^[0-9]+d$' THEN SUBSTRING(schedule_interval FROM 1 FOR LENGTH(schedule_interval)-1)::INTEGER * 86400
    END;
```

### Script 2: Bulk Frequency Adjustment

Save as: `adjust_frequencies.sql`

```sql
-- ============================================================================
-- Bulk Adjust Job Frequencies
-- ============================================================================

BEGIN;

-- Show current state
SELECT 'BEFORE CHANGES:' as status;
SELECT job_name, schedule_interval FROM ubec_main.scheduler_jobs ORDER BY job_name;

-- Adjust frequencies based on system load profile
-- High-frequency monitoring jobs (every 5-10 minutes)
UPDATE ubec_main.scheduler_jobs
SET schedule_interval = '5m'
WHERE job_name IN ('blockchain_sync', 'protocol_health_check');

-- Medium-frequency analysis jobs (every 15-30 minutes)
UPDATE ubec_main.scheduler_jobs
SET schedule_interval = '15m'
WHERE job_name IN ('analytics_update');

UPDATE ubec_main.scheduler_jobs
SET schedule_interval = '30m'
WHERE job_name IN ('holonic_evaluation');

-- Low-frequency reporting jobs (every 6-12 hours)
UPDATE ubec_main.scheduler_jobs
SET schedule_interval = '6h'
WHERE job_name IN ('report_generation');

-- Daily maintenance jobs
UPDATE ubec_main.scheduler_jobs
SET schedule_interval = '1d'
WHERE job_name IN ('database_cleanup');

-- Show new state
SELECT 'AFTER CHANGES:' as status;
SELECT job_name, schedule_interval FROM ubec_main.scheduler_jobs ORDER BY job_name;

-- Commit changes (or ROLLBACK if incorrect)
COMMIT;
-- ROLLBACK;
```

### Script 3: Set Jobs to Off-Peak Hours

Save as: `schedule_off_peak.sql`

```sql
-- ============================================================================
-- Schedule Resource-Intensive Jobs During Off-Peak Hours
-- ============================================================================

-- Assumption: Off-peak hours are 2 AM - 6 AM local time

BEGIN;

-- Schedule reports for 2 AM daily
UPDATE ubec_main.scheduler_jobs
SET 
    schedule_interval = '1d',
    next_run = (CURRENT_DATE + INTERVAL '1 day' + TIME '02:00:00')
WHERE job_name = 'report_generation';

-- Schedule database cleanup for 3 AM daily
UPDATE ubec_main.scheduler_jobs
SET 
    schedule_interval = '1d',
    next_run = (CURRENT_DATE + INTERVAL '1 day' + TIME '03:00:00')
WHERE job_name = 'database_cleanup';

-- Schedule holonic evaluation for every 4 hours starting at 4 AM
UPDATE ubec_main.scheduler_jobs
SET 
    schedule_interval = '4h',
    next_run = (CURRENT_DATE + INTERVAL '1 day' + TIME '04:00:00')
WHERE job_name = 'holonic_evaluation';

-- Verify scheduling
SELECT 
    job_name,
    schedule_interval,
    next_run,
    EXTRACT(HOUR FROM next_run) as run_hour
FROM ubec_main.scheduler_jobs
WHERE job_name IN ('report_generation', 'database_cleanup', 'holonic_evaluation')
ORDER BY next_run;

COMMIT;
```

### Script 4: Emergency Frequency Reduction

Save as: `emergency_reduce_frequency.sql`

```sql
-- ============================================================================
-- Emergency: Reduce All Job Frequencies During System Stress
-- ============================================================================

-- Use this script when system is under high load
-- Doubles all intervals to reduce resource consumption

BEGIN;

-- Backup current configuration
CREATE TEMP TABLE scheduler_jobs_backup AS
SELECT * FROM ubec_main.scheduler_jobs;

-- Double all intervals
UPDATE ubec_main.scheduler_jobs
SET schedule_interval = (
    CASE 
        WHEN schedule_interval ~ '^[0-9]+$' THEN 
            (schedule_interval::INTEGER * 2)::TEXT
        WHEN schedule_interval ~ '^[0-9]+s$' THEN 
            (SUBSTRING(schedule_interval FROM 1 FOR LENGTH(schedule_interval)-1)::INTEGER * 2)::TEXT || 's'
        WHEN schedule_interval ~ '^[0-9]+m$' THEN 
            (SUBSTRING(schedule_interval FROM 1 FOR LENGTH(schedule_interval)-1)::INTEGER * 2)::TEXT || 'm'
        WHEN schedule_interval ~ '^[0-9]+h$' THEN 
            (SUBSTRING(schedule_interval FROM 1 FOR LENGTH(schedule_interval)-1)::INTEGER * 2)::TEXT || 'h'
        WHEN schedule_interval ~ '^[0-9]+d$' THEN 
            (SUBSTRING(schedule_interval FROM 1 FOR LENGTH(schedule_interval)-1)::INTEGER * 2)::TEXT || 'd'
        ELSE schedule_interval
    END
);

-- Show changes
SELECT 
    b.job_name,
    b.schedule_interval as old_interval,
    j.schedule_interval as new_interval
FROM scheduler_jobs_backup b
JOIN ubec_main.scheduler_jobs j ON b.job_name = j.job_name
ORDER BY b.job_name;

-- To restore original frequencies if needed:
-- UPDATE ubec_main.scheduler_jobs j
-- SET schedule_interval = b.schedule_interval
-- FROM scheduler_jobs_backup b
-- WHERE j.job_name = b.job_name;

COMMIT;
```

### Script 5: Performance-Based Auto-Adjustment

Save as: `auto_adjust_by_performance.sql`

```sql
-- ============================================================================
-- Auto-Adjust Frequencies Based on Job Performance
-- ============================================================================

-- This script analyzes job execution times and adjusts frequencies
-- to maintain optimal system performance

WITH job_performance AS (
    SELECT 
        job_name,
        AVG(duration_ms) as avg_duration,
        MAX(duration_ms) as max_duration,
        COUNT(*) as execution_count,
        SUM(CASE WHEN success THEN 1 ELSE 0 END)::FLOAT / COUNT(*) as success_rate
    FROM ubec_main.scheduler_execution_log
    WHERE executed_at > NOW() - INTERVAL '24 hours'
    GROUP BY job_name
),
current_jobs AS (
    SELECT 
        job_name,
        schedule_interval,
        CASE 
            WHEN schedule_interval ~ '^[0-9]+$' THEN schedule_interval::INTEGER
            WHEN schedule_interval ~ '^[0-9]+s$' THEN 
                SUBSTRING(schedule_interval FROM 1 FOR LENGTH(schedule_interval)-1)::INTEGER
            WHEN schedule_interval ~ '^[0-9]+m$' THEN 
                SUBSTRING(schedule_interval FROM 1 FOR LENGTH(schedule_interval)-1)::INTEGER * 60
            WHEN schedule_interval ~ '^[0-9]+h$' THEN 
                SUBSTRING(schedule_interval FROM 1 FOR LENGTH(schedule_interval)-1)::INTEGER * 3600
            WHEN schedule_interval ~ '^[0-9]+d$' THEN 
                SUBSTRING(schedule_interval FROM 1 FOR LENGTH(schedule_interval)-1)::INTEGER * 86400
        END as interval_seconds
    FROM ubec_main.scheduler_jobs
)
SELECT 
    p.job_name,
    c.schedule_interval as current_interval,
    ROUND(p.avg_duration) as avg_ms,
    ROUND(p.max_duration) as max_ms,
    ROUND(p.success_rate * 100, 1) as success_pct,
    CASE 
        -- If job takes >10s on average, increase interval by 50%
        WHEN p.avg_duration > 10000 THEN 
            (c.interval_seconds * 1.5)::INTEGER || 's'
        -- If job takes >5s on average, increase interval by 25%
        WHEN p.avg_duration > 5000 THEN 
            (c.interval_seconds * 1.25)::INTEGER || 's'
        -- If job is very fast (<1s) and reliable, could run more frequently
        WHEN p.avg_duration < 1000 AND p.success_rate > 0.99 THEN 
            (c.interval_seconds * 0.75)::INTEGER || 's'
        -- Otherwise keep current
        ELSE c.schedule_interval
    END as recommended_interval,
    CASE 
        WHEN p.avg_duration > 10000 THEN 'INCREASE frequency (slow job)'
        WHEN p.avg_duration > 5000 THEN 'Slightly increase frequency'
        WHEN p.avg_duration < 1000 AND p.success_rate > 0.99 THEN 'Could run more frequently'
        ELSE 'Current frequency OK'
    END as recommendation
FROM job_performance p
JOIN current_jobs c ON p.job_name = c.job_name
ORDER BY p.avg_duration DESC;

-- To apply recommendations, run:
-- UPDATE ubec_main.scheduler_jobs j
-- SET schedule_interval = recommended_interval
-- FROM (...above query...) recommendations
-- WHERE j.job_name = recommendations.job_name;
```

### Script 6: Reset to Default Frequencies

Save as: `reset_to_defaults.sql`

```sql
-- ============================================================================
-- Reset All Jobs to Default UBEC Frequencies
-- ============================================================================

BEGIN;

-- Backup current configuration
SELECT 'CURRENT CONFIGURATION:' as status;
SELECT job_name, schedule_interval, enabled FROM ubec_main.scheduler_jobs ORDER BY job_name;

-- Reset to UBEC Protocol Suite defaults
UPDATE ubec_main.scheduler_jobs
SET schedule_interval = '300'  -- 5 minutes
WHERE job_name = 'blockchain_sync';

UPDATE ubec_main.scheduler_jobs
SET schedule_interval = '900'  -- 15 minutes
WHERE job_name = 'analytics_update';

UPDATE ubec_main.scheduler_jobs
SET schedule_interval = '1800'  -- 30 minutes
WHERE job_name = 'holonic_evaluation';

UPDATE ubec_main.scheduler_jobs
SET schedule_interval = '600'  -- 10 minutes
WHERE job_name = 'protocol_health_check';

UPDATE ubec_main.scheduler_jobs
SET schedule_interval = '21600'  -- 6 hours
WHERE job_name = 'report_generation';

UPDATE ubec_main.scheduler_jobs
SET schedule_interval = '86400'  -- 24 hours (daily)
WHERE job_name = 'database_cleanup';

-- Verify reset
SELECT 'AFTER RESET:' as status;
SELECT job_name, schedule_interval, enabled FROM ubec_main.scheduler_jobs ORDER BY job_name;

COMMIT;
```

---

## Troubleshooting

### Problem: Job Not Running at Expected Time

**Diagnosis:**
```sql
SELECT 
    job_name,
    schedule_interval,
    last_run,
    next_run,
    enabled,
    (next_run - NOW()) as time_until_run
FROM ubec_main.scheduler_jobs
WHERE job_name = 'your_job_name';
```

**Common Issues:**
1. **Job disabled**: `enabled = false`
2. **Next run in future**: `next_run` is later than expected
3. **Invalid interval format**: Check `schedule_interval` syntax

**Fix:**
```sql
-- Re-enable and schedule immediate run
UPDATE ubec_main.scheduler_jobs
SET 
    enabled = true,
    next_run = NOW()
WHERE job_name = 'your_job_name';
```

### Problem: Interval Change Not Taking Effect

**Cause:** Scheduler checks database every 60 seconds

**Solution:** Wait up to 60 seconds, or restart server:
```bash
# Stop server (Ctrl+C)
# Restart
python main.py serve
```

### Problem: Too Many Jobs Running Simultaneously

**Diagnosis:**
```sql
-- Check which jobs are scheduled to run close together
SELECT 
    job_name,
    next_run,
    EXTRACT(MINUTE FROM next_run) as minute_of_hour
FROM ubec_main.scheduler_jobs
WHERE enabled = true
ORDER BY next_run;
```

**Fix - Stagger execution:**
```sql
-- Offset jobs by 5-minute increments
UPDATE ubec_main.scheduler_jobs
SET next_run = date_trunc('hour', NOW()) + INTERVAL '1 hour'
WHERE job_name = 'job_1';

UPDATE ubec_main.scheduler_jobs
SET next_run = date_trunc('hour', NOW()) + INTERVAL '1 hour 5 minutes'
WHERE job_name = 'job_2';

UPDATE ubec_main.scheduler_jobs
SET next_run = date_trunc('hour', NOW()) + INTERVAL '1 hour 10 minutes'
WHERE job_name = 'job_3';
```

### Problem: Job Running Too Frequently (High Load)

**Diagnosis:**
```sql
-- Count executions in last hour
SELECT 
    job_name,
    COUNT(*) as executions_last_hour,
    AVG(duration_ms) as avg_duration_ms
FROM ubec_main.scheduler_execution_log
WHERE executed_at > NOW() - INTERVAL '1 hour'
GROUP BY job_name
ORDER BY executions_last_hour DESC;
```

**Fix:**
```sql
-- Double the interval for high-frequency jobs
UPDATE ubec_main.scheduler_jobs
SET schedule_interval = (schedule_interval::INTEGER * 2)::TEXT
WHERE job_name IN (
    SELECT job_name 
    FROM ubec_main.scheduler_execution_log
    WHERE executed_at > NOW() - INTERVAL '1 hour'
    GROUP BY job_name
    HAVING COUNT(*) > 10  -- More than 10 executions per hour
);
```

### Problem: Need to Convert Between Formats

**Conversion Table:**

| Seconds | Minutes | Hours | Days |
|---------|---------|-------|------|
| 60 | 1m | - | - |
| 300 | 5m | - | - |
| 600 | 10m | - | - |
| 900 | 15m | - | - |
| 1800 | 30m | - | - |
| 3600 | 60m | 1h | - |
| 21600 | 360m | 6h | - |
| 43200 | 720m | 12h | - |
| 86400 | 1440m | 24h | 1d |

**SQL Conversion Helper:**
```sql
-- Convert any interval to all formats
WITH interval_conversion AS (
    SELECT 
        '600' as raw_seconds,  -- Change this value
        600 as seconds
)
SELECT 
    seconds || 's' as seconds_format,
    (seconds / 60) || 'm' as minutes_format,
    (seconds / 3600) || 'h' as hours_format,
    (seconds / 86400) || 'd' as days_format
FROM interval_conversion;
```

---

## Quick Reference

### Command Shortcuts

```bash
# View all jobs
psql -U ubec_admin -d ubec -h localhost -c "SELECT job_name, schedule_interval, enabled FROM ubec_main.scheduler_jobs ORDER BY job_name;"

# Change specific job
psql -U ubec_admin -d ubec -h localhost -c "UPDATE ubec_main.scheduler_jobs SET schedule_interval = '600' WHERE job_name = 'blockchain_sync';"

# Disable job
psql -U ubec_admin -d ubec -h localhost -c "UPDATE ubec_main.scheduler_jobs SET enabled = false WHERE job_name = 'job_name';"

# Enable job
psql -U ubec_admin -d ubec -h localhost -c "UPDATE ubec_main.scheduler_jobs SET enabled = true WHERE job_name = 'job_name';"

# Trigger immediate run
psql -U ubec_admin -d ubec -h localhost -c "UPDATE ubec_main.scheduler_jobs SET next_run = NOW() WHERE job_name = 'job_name';"
```

### Common Intervals Reference Card

```
1 minute    = 60 seconds   = 60 or 1m
5 minutes   = 300 seconds  = 300 or 5m
10 minutes  = 600 seconds  = 600 or 10m
15 minutes  = 900 seconds  = 900 or 15m
30 minutes  = 1800 seconds = 1800 or 30m
1 hour      = 3600 seconds = 3600 or 1h
6 hours     = 21600 seconds = 21600 or 6h
12 hours    = 43200 seconds = 43200 or 12h
24 hours    = 86400 seconds = 86400 or 1d
```

---

## Support

For additional help:
- Check logs: `tail -f /var/log/ubec/application.log | grep scheduler`
- View scheduler status: `python main.py scheduler-status`
- Consult main documentation: `docs/Technical/UBEC_Scheduler_User_Guide.md`

---

**Document Version:** 1.0.0  
**Last Updated:** November 20, 2025  
**Maintained By:** UBEC Protocol Suite Team
