# Quick Deployment Guide - Scheduler Enhancement v1.0.4

**Date**: November 8, 2025  
**Time Required**: 20-30 minutes  
**Risk Level**: LOW (Enhancement, not fix)  
**Downtime**: 2-3 minutes for restart

---

## Pre-Deployment Checklist

- [ ] Backup current scheduler service file
- [ ] Verify database connection active
- [ ] Confirm service registry working
- [ ] Have access to logs directory
- [ ] Can restart services

---

## Step 1: Manual Sync (5 minutes) - DO THIS FIRST

**Purpose:** Refresh 63.4-hour-old stale data immediately

```bash
# Run manual sync
python main.py sync --sync-type all

# Verify completion (should take 2-5 minutes)
# Check logs for success:
tail -50 logs/ubec.log | grep -i "sync completed"

# Expected output:
# ✅ Blockchain sync completed
# ✅ Account balances updated
# ✅ Data freshness: < 5 minutes
```

**Verification:**
```sql
-- Check data freshness
SELECT 
    MAX(updated_at) as latest_sync,
    NOW() - MAX(updated_at) as age
FROM ubec_main.account_balances;

-- Expected: age < 10 minutes
```

---

## Step 2: Backup Current Files (2 minutes)

```bash
# Create backup directory
mkdir -p backups/scheduler_deployment_$(date +%Y%m%d)

# Backup scheduler service
cp services/ubec_scheduler_service.py \
   backups/scheduler_deployment_$(date +%Y%m%d)/

# Backup main.py (we'll modify this)
cp main.py backups/scheduler_deployment_$(date +%Y%m%d)/

# Verify backups
ls -lh backups/scheduler_deployment_$(date +%Y%m%d)/
```

---

## Step 3: Deploy Enhanced Scheduler (3 minutes)

```bash
# Copy enhanced version to services directory
cp outputs/ubec_scheduler_service.py services/

# Verify file was copied
ls -lh services/ubec_scheduler_service.py

# Check version number in file
head -55 services/ubec_scheduler_service.py | grep "Version:"
# Expected output: Version: 1.0.4
```

---

## Step 4: Update main.py (10 minutes)

### Option A: Manual Edit (Recommended)

Open `main.py` and locate the `handle_serve()` function.

**Find this section:**

```python
async def handle_serve(args):
    """Start API server."""
    try:
        # Initialize service registry
        registry = ServiceRegistry()
        await registry.initialize()
        
        # Start API server
        api_service = await registry.get('api')
        
        # ... existing code ...
```

**Add scheduler startup:**

```python
async def handle_serve(args):
    """Start API server with scheduler."""
    scheduler = None  # ← Add this
    
    try:
        # Initialize service registry
        registry = ServiceRegistry()
        await registry.initialize()
        
        # ============================================================
        # ADD THIS BLOCK: Start Scheduler
        # ============================================================
        logger.info("Starting scheduler service...")
        scheduler = await registry.get('scheduler')
        await scheduler.start()  # ← CRITICAL LINE
        logger.info("✅ Scheduler started - background jobs active")
        # ============================================================
        
        # Start API server
        api_service = await registry.get('api')
        logger.info("✅ API server ready")
        
        # Keep running
        logger.info("👉 Press Ctrl+C to stop")
        await scheduler.wait_for_completion()  # ← Add this (NEW method)
        
    except KeyboardInterrupt:
        logger.info("\n⚠️  Shutting down gracefully...")
        
    finally:
        # ============================================================
        # ADD THIS BLOCK: Graceful Shutdown
        # ============================================================
        if scheduler:
            await scheduler.stop()
            logger.info("✅ Scheduler stopped")
        # ============================================================
        
        if registry:
            await registry.close()
            logger.info("✅ All services closed")
```

**Save the file.**

### Option B: Patch File

If you have a patch file:

```bash
# Apply patch
patch main.py < patches/scheduler_startup.patch

# Verify changes
git diff main.py
```

---

## Step 5: Restart Service (2 minutes)

```bash
# Stop current service
pkill -f "python main.py serve"

# Wait 2 seconds for clean shutdown
sleep 2

# Verify no process running
ps aux | grep "main.py serve"
# Should return nothing

# Start service with new code
nohup python main.py serve > logs/serve_$(date +%Y%m%d_%H%M%S).log 2>&1 &

# Note the process ID
echo $! > scheduler_deployment.pid

# Tail logs to monitor startup
tail -f logs/ubec.log
```

**Expected startup logs:**

```
Initializing services...
✅ Database connected
✅ Configuration loaded
✅ Stellar client ready
✅ Sync service initialized
✅ Analytics service ready
✅ Holonic evaluator ready
Starting scheduler service...
✅ Scheduler started - background jobs active  ← LOOK FOR THIS
✅ API server ready
📊 Swagger docs: http://0.0.0.0:8000/docs
⏰ Scheduler: Active (background tasks running)  ← AND THIS
👉 Press Ctrl+C to stop
```

**If you DON'T see scheduler startup messages:**
- Check for errors in logs
- Verify main.py changes saved
- Check scheduler service file in place

---

## Step 6: Verify Deployment (5 minutes)

### 6.1: Check Health Endpoint

```bash
# Test health endpoint
curl http://localhost:8000/api/v1/health | jq '.scheduler'

# Expected output:
{
  "service": "UBECSchedulerService",
  "status": "healthy",       # ← NOT "not_started"
  "initialized": true,
  "running": true,           # ← Should be TRUE
  "metrics": {
    "total_jobs": 6,
    "enabled_jobs": 6,
    "running_jobs": 0,
    "overall_success_rate": 1.0
  },
  "timestamp": "2025-11-08T10:30:00"
}
```

**If status is "not_started":**
```bash
# Check if start() was called
grep "Scheduler started" logs/ubec.log

# If not found, main.py changes didn't take effect
# Verify file saved and restart again
```

### 6.2: Check Database for Job Execution

```sql
-- Wait 5-10 minutes, then check if jobs are executing
SELECT 
    job_name,
    last_run,
    next_run,
    enabled,
    NOW() - last_run as time_since_last
FROM ubec_main.scheduler_jobs
ORDER BY last_run DESC;

-- Expected: last_run timestamps should be recent
-- (within last 10 minutes for short-interval jobs)
```

### 6.3: Monitor Logs for Job Execution

```bash
# Watch logs for job execution
tail -f logs/ubec.log | grep -E "(Executing job|Job.*completed)"

# Expected output (every few minutes):
# Executing job: sync_blockchain
# ✅ Job 'sync_blockchain' completed (2,345ms)
# Executing job: update_analytics
# ✅ Job 'update_analytics' completed (4,567ms)
```

### 6.4: Verify Data Freshness

```bash
# Check data age via API
curl http://localhost:8000/api/v1/sync/status | jq '.last_sync'

# Expected: timestamp within last hour
```

---

## Rollback Procedure (If Needed)

**If deployment fails or causes issues:**

```bash
# Step 1: Stop current service
pkill -f "python main.py serve"

# Step 2: Restore backups
cp backups/scheduler_deployment_$(date +%Y%m%d)/ubec_scheduler_service.py \
   services/
cp backups/scheduler_deployment_$(date +%Y%m%d)/main.py .

# Step 3: Restart with old code
python main.py serve

# Step 4: Verify old version running
curl http://localhost:8000/api/v1/health | jq '.scheduler.status'

# Step 5: Document rollback reason
echo "Rollback at $(date): [REASON]" >> deployment_log.txt
```

---

## Post-Deployment Monitoring (First 24 Hours)

### Metrics to Watch

1. **Scheduler Running State**
   ```bash
   # Every 15 minutes
   curl http://localhost:8000/api/v1/health | jq '.scheduler.running'
   # Should always be: true
   ```

2. **Job Success Rate**
   ```sql
   -- Every hour
   SELECT 
       job_name,
       COUNT(*) FILTER (WHERE success = true) as successes,
       COUNT(*) as total,
       ROUND(
           100.0 * COUNT(*) FILTER (WHERE success = true) / COUNT(*),
           1
       ) as success_rate
   FROM ubec_main.scheduler_execution_log
   WHERE executed_at > NOW() - INTERVAL '1 hour'
   GROUP BY job_name;
   
   -- Expected: success_rate > 95% for all jobs
   ```

3. **Data Freshness**
   ```bash
   # Every 30 minutes
   curl http://localhost:8000/api/v1/sync/status | \
       jq '.last_sync, .data_age_minutes'
   
   # Expected: data_age_minutes < 60
   ```

4. **Error Log Monitoring**
   ```bash
   # Every hour
   grep -i "error\|fail" logs/ubec.log | tail -20
   
   # Should see minimal errors
   # Circuit breaker messages indicate persistent issues
   ```

### Alert Thresholds

Set up alerts for:

- **Scheduler Stopped**: `running == false` for > 5 min → CRITICAL
- **Jobs Not Executing**: No job execution logs for > 30 min → HIGH  
- **Data Stale**: `data_age > 2 hours` → HIGH
- **Circuit Breakers Open**: Any job disabled → MEDIUM

---

## Success Criteria

**Deployment is successful when ALL of the following are true:**

- [x] Health check shows `status: "healthy"` AND `running: true`
- [x] Jobs executing according to schedule (check logs)
- [x] Data freshness < 1 hour
- [x] No errors in logs related to scheduler
- [x] All 6 jobs have recent `last_run` timestamps
- [x] Circuit breakers all CLOSED
- [x] System metrics (CPU, memory) within normal ranges

**If all criteria met:**

```bash
# Document successful deployment
echo "✅ Scheduler v1.0.4 deployed successfully at $(date)" >> deployment_log.txt

# Create success marker
touch deployment_success_$(date +%Y%m%d_%H%M%S)

# Clean up old backups (optional, after 7 days)
find backups/ -name "scheduler_deployment_*" -mtime +7 -delete
```

---

## Common Issues & Solutions

### Issue 1: "Scheduler already running" Warning

**Cause:** Tried to start scheduler twice

**Solution:** Normal warning, can be ignored if health check shows running

### Issue 2: Jobs Execute Twice

**Cause:** Two scheduler instances running

**Solution:**
```bash
# Kill all main.py processes
pkill -f "python main.py serve"

# Verify all stopped
ps aux | grep main.py

# Start single instance
python main.py serve
```

### Issue 3: Job Stuck in "Running" State

**Cause:** Job hung or timed out

**Solution:**
```sql
-- Check for long-running jobs
SELECT 
    job_name,
    started_at,
    NOW() - started_at as runtime
FROM ubec_main.scheduler_execution_log
WHERE completed_at IS NULL
    AND started_at < NOW() - INTERVAL '1 hour';

-- If found, restart scheduler to cancel hung jobs
```

### Issue 4: High CPU Usage

**Cause:** Too many concurrent jobs or job logic inefficient

**Solution:**
```sql
-- Reduce concurrent job limit
UPDATE ubec_main.system_config
SET config_value = '3'
WHERE config_key = 'scheduler_max_concurrent_jobs';

-- Restart scheduler to apply
```

---

## Contact & Support

**If deployment fails or issues persist:**

1. **Collect diagnostic information:**
   ```bash
   # System status
   python main.py health --detailed > deployment_diagnostic.txt
   
   # Scheduler logs
   grep -i scheduler logs/ubec.log > scheduler_diagnostic.log
   
   # Database state
   psql -U ubec_admin -d ubec -c "SELECT * FROM ubec_main.scheduler_jobs;" \
       > jobs_diagnostic.txt
   ```

2. **Review technical analysis:**
   - Open `SCHEDULER_TECHNICAL_ANALYSIS.md`
   - Check "Troubleshooting Guide" section
   - Reference specific error codes

3. **Escalation path:**
   - Level 1: Check deployment logs and error messages
   - Level 2: Review technical analysis document
   - Level 3: Rollback and document issue for team review

---

## Appendix: Environment-Specific Notes

### Development Environment

```bash
# Can use direct Python execution
python main.py serve

# Logs go to console
# Easy to Ctrl+C and restart
```

### Staging Environment

```bash
# Use nohup for background execution
nohup python main.py serve > logs/staging.log 2>&1 &

# Monitor via logs
tail -f logs/staging.log

# Stop via PID
cat scheduler_deployment.pid | xargs kill
```

### Production Environment

```bash
# Use systemd service (preferred)
sudo systemctl restart ubec-scheduler

# Or supervisord
supervisorctl restart ubec-scheduler

# Monitor via service logs
journalctl -u ubec-scheduler -f
```

---

**Attribution:** This deployment guide was created with assistance from Claude and Anthropic PBC.

**Document Version:** 1.0  
**Last Updated:** November 8, 2025  
**Deployment Window:** Anytime (low risk)  
**Rollback Time:** < 5 minutes if needed
