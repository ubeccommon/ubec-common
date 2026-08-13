# Scheduler v1.0.4 Deployment - Quick Checklist

**Date**: _______________  **Time Started**: _______________  **Deployer**: _______________

---

## ⚡ EMERGENCY SYNC FIRST (DO THIS NOW!)

```bash
□ python main.py sync --sync-type all
□ Wait for completion (2-5 minutes)
□ Verify: Data age < 10 minutes
```

---

## 📋 Pre-Flight Checks

□ Database connection: `psql -U ubec_admin -d ubec -c "SELECT 1;"`  
□ Service registry: `python main.py health`  
□ Backup directory exists: `mkdir -p backups/scheduler_deployment_$(date +%Y%m%d)`  
□ Can restart services: Verify permissions  
□ Logs accessible: `tail logs/ubec.log`

---

## 💾 Backup Current Files

```bash
□ cp services/ubec_scheduler_service.py backups/scheduler_deployment_$(date +%Y%m%d)/
□ cp main.py backups/scheduler_deployment_$(date +%Y%m%d)/
□ ls -lh backups/scheduler_deployment_$(date +%Y%m%d)/  # Verify 2 files
```

---

## 📦 Deploy New Code

```bash
□ cp outputs/ubec_scheduler_service.py services/
□ Verify version: head -55 services/ubec_scheduler_service.py | grep "Version:"
   Expected: Version: 1.0.4
```

---

## ✏️ Edit main.py

### Add to handle_serve() function:

**After registry.initialize():**

```python
□ scheduler = None  # Add at top of try block

□ logger.info("Starting scheduler service...")
□ scheduler = await registry.get('scheduler')
□ await scheduler.start()  # ← CRITICAL LINE
□ logger.info("✅ Scheduler started - background jobs active")
```

**Before existing code that starts API:**

```python
□ await scheduler.wait_for_completion()  # Replace or add after API start
```

**In finally block:**

```python
□ if scheduler:
□     await scheduler.stop()
□     logger.info("✅ Scheduler stopped")
```

□ Save file  
□ Verify changes: `git diff main.py` or review in editor

---

## 🔄 Restart Service

```bash
□ pkill -f "python main.py serve"
□ sleep 2
□ ps aux | grep "main.py serve"  # Verify nothing running
□ python main.py serve
□ Tail logs: tail -f logs/ubec.log
```

---

## ✅ Verify Deployment (Critical!)

### 1. Check Startup Logs

□ Logs show: `✅ Scheduler started - background jobs active`  
□ Logs show: `⏰ Scheduler: Active (background tasks running)`  
□ No error messages in logs

### 2. Check Health Endpoint

```bash
□ curl http://localhost:8000/api/v1/health | jq '.scheduler'
```

**Verify output contains:**

□ `"status": "healthy"` (NOT "not_started")  
□ `"initialized": true`  
□ `"running": true`  ← MUST BE TRUE  
□ `"total_jobs": 6`

### 3. Wait 5-10 Minutes, Check Job Execution

```bash
□ tail -f logs/ubec.log | grep -E "(Executing job|completed)"
```

**Should see:**

□ "Executing job: sync_blockchain"  
□ "✅ Job 'sync_blockchain' completed"  
□ Jobs executing every few minutes

### 4. Check Database

```sql
□ SELECT job_name, last_run, enabled 
  FROM ubec_main.scheduler_jobs 
  ORDER BY last_run DESC;
```

**Verify:**

□ All jobs have `last_run` within last 15 minutes  
□ All jobs show `enabled = true`

---

## 🎯 Success Criteria (ALL must be checked)

□ Health endpoint: `status = "healthy"` AND `running = true`  
□ Logs show job executions happening  
□ Database shows recent `last_run` timestamps  
□ No error messages in logs  
□ Data freshness < 1 hour  
□ System metrics normal (CPU, memory)

---

## 🔴 Rollback Procedure (If Deployment Fails)

```bash
□ pkill -f "python main.py serve"
□ cp backups/scheduler_deployment_$(date +%Y%m%d)/* .
□ python main.py serve
□ Document issue: echo "Rollback: [REASON]" >> deployment_log.txt
```

---

## 📊 Post-Deployment (First Hour)

**15 min:** □ Health check → `running = true`  
**30 min:** □ Job logs → Jobs executing  
**45 min:** □ Data check → Freshness < 1 hour  
**60 min:** □ Error scan → No critical errors

---

## 🚨 Emergency Contacts

**If deployment fails:**

□ Review: `SCHEDULER_TECHNICAL_ANALYSIS.md`  
□ Check: `DEPLOYMENT_GUIDE_SCHEDULER_v1.0.4.md` - "Common Issues"  
□ Collect diagnostics:
  ```bash
  python main.py health --detailed > diagnostic.txt
  grep scheduler logs/ubec.log > scheduler_logs.txt
  ```

---

## 📝 Sign-Off

**Deployment Status:**

□ ✅ SUCCESS - All checks passed  
□ ⚠️  PARTIAL - Issues noted: _________________________  
□ ❌ FAILED - Rolled back: ___________________________

**Completion Time**: _______________  
**Total Duration**: _______________  
**Next Review**: _______________ (24 hours after deployment)

**Notes:**

```
_________________________________________________________________

_________________________________________________________________

_________________________________________________________________

_________________________________________________________________
```

**Signature**: _____________________ **Date**: _______________

---

## 📋 24-Hour Follow-Up Checklist

**Date**: _______________  **Time**: _______________

□ Scheduler still running: `running = true`  
□ All 6 jobs executed successfully  
□ No circuit breakers open  
□ Data freshness maintained < 1 hour  
□ No repeated errors in logs  
□ System performance normal  

**Status:** □ Stable  □ Monitoring  □ Issues

**Follow-up Actions:**

```
_________________________________________________________________

_________________________________________________________________
```

---

**Version**: 1.0  
**Last Updated**: November 8, 2025  
**Print This Page**: Use as physical checklist during deployment
