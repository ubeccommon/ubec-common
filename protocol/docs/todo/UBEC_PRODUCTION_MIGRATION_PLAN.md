# UBEC Protocol Suite - Production Migration Plan

**Version**: 1.0.0  
**Date**: November 11, 2025  
**Target Completion**: Before December 15, 2025 production launch  
**Estimated Time**: 2-3 hours  
**Risk Level**: MEDIUM (with rollback plan)  

---

## Table of Contents

1. [Overview](#overview)
2. [Pre-Migration Checklist](#pre-migration-checklist)
3. [Directory Structure](#directory-structure)
4. [Migration Steps](#migration-steps)
5. [Service Configuration](#service-configuration)
6. [Testing & Verification](#testing--verification)
7. [Rollback Plan](#rollback-plan)
8. [Post-Migration Tasks](#post-migration-tasks)

---

## Overview

### Current State
```
Development: /home/triag/UBEC/projects/UBEC/
├── All code, data, logs mixed together
├── Development environment
└── Running as user 'triag'
```

### Target State
```
Production Layout:
├── /opt/ubec/              # Application code (read-only)
├── /var/lib/ubec/          # Variable application data
├── /var/log/ubec/          # Log files
├── /etc/ubec/              # System configuration
└── Development remains: /home/triag/UBEC/projects/UBEC/
```

### Key Benefits
- **Separation of Concerns**: Code, data, logs isolated
- **Security**: Proper permissions and ownership
- **Professional**: Standard Linux FHS layout
- **Maintainability**: Clear upgrade paths
- **Backup**: Easy to backup /var/lib/ubec and /etc/ubec

### Design Principles Applied
- **Principle #4**: Database remains single source of truth
- **Principle #8**: No duplicate configuration
- **Principle #10**: Clear separation of concerns

---

## Pre-Migration Checklist

### System Requirements

```bash
# 1. Check available disk space (need ~2GB)
df -h /opt /var

# Expected: At least 5GB free on each

# 2. Verify PostgreSQL is running
systemctl status postgresql

# Expected: active (running)

# 3. Check current database connection
psql -U ubec_admin -d ubec -c "SELECT COUNT(*) FROM ubec_main.account_balances;"

# Expected: Should return record count (87,567+)

# 4. Verify Python version
python3 --version

# Expected: Python 3.10 or higher

# 5. Check current service status
cd /home/triag/UBEC/projects/UBEC
python main.py health

# Expected: All services reporting health status
```

### Pre-Migration Backup

```bash
# 1. Create backup directory with timestamp
BACKUP_DIR="/home/triag/backups/ubec_migration_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

# 2. Backup entire project
cd /home/triag/UBEC/projects
tar -czf "$BACKUP_DIR/ubec_project_complete.tar.gz" UBEC/

# 3. Backup database
pg_dump -U ubec_admin -d ubec -F c -f "$BACKUP_DIR/ubec_database_$(date +%Y%m%d).dump"

# 4. Backup .env file separately (critical!)
cp /home/triag/UBEC/projects/UBEC/.env "$BACKUP_DIR/.env.backup"

# 5. Verify backups
ls -lh "$BACKUP_DIR"

# Expected: 3 files (project tar.gz, database dump, .env)
# Project size: ~50-200MB
# Database size: ~10-50MB
```

### Document Current State

```bash
# 1. Capture current service status
python main.py health > "$BACKUP_DIR/pre_migration_health.txt"

# 2. Document running processes
ps aux | grep python > "$BACKUP_DIR/pre_migration_processes.txt"

# 3. Check current log files
ls -lh logs/ > "$BACKUP_DIR/pre_migration_logs.txt"

# 4. Database statistics
psql -U ubec_admin -d ubec -c "\dt+ ubec_main.*" > "$BACKUP_DIR/pre_migration_db_stats.txt"
```

---

## Directory Structure

### Create Production Directories

```bash
# 1. Create main directories
sudo mkdir -p /opt/ubec
sudo mkdir -p /var/lib/ubec/{state,data}
sudo mkdir -p /var/log/ubec/{archive,services}
sudo mkdir -p /etc/ubec

# 2. Create subdirectories for logs
sudo mkdir -p /var/log/ubec/analytics
sudo mkdir -p /var/log/ubec/protocols
sudo mkdir -p /var/log/ubec/services

# 3. Create subdirectories for data
sudo mkdir -p /var/lib/ubec/data/reports
sudo mkdir -p /var/lib/ubec/data/visualizations
sudo mkdir -p /var/lib/ubec/state/protocols

# 4. Verify structure
tree -L 2 /opt/ubec /var/lib/ubec /var/log/ubec /etc/ubec

# Expected output:
# /opt/ubec/
# (empty for now)
# /var/lib/ubec/
# ├── data/
# │   ├── reports/
# │   └── visualizations/
# └── state/
#     └── protocols/
# /var/log/ubec/
# ├── analytics/
# ├── archive/
# ├── protocols/
# └── services/
# /etc/ubec/
# (empty for now)
```

### Production Directory Structure Details

```
/opt/ubec/                          # Application code (READ-ONLY in production)
├── main.py                         # Orchestrator
├── README.md                       # Documentation
├── requirements.txt                # Dependencies
├── config/                         # Config modules (code, not data)
├── core/                           # Core system
├── services/                       # Services
├── phenom/                         # Phenomenological modeling
├── tests/                          # Test suite
├── docs/                           # Documentation
└── venv/                           # Virtual environment

/var/lib/ubec/                      # Variable application data
├── data/
│   ├── reports/                    # Generated reports
│   └── visualizations/             # Charts and graphs
└── state/
    └── protocols/                  # Protocol state data

/var/log/ubec/                      # Log files
├── ubec.log                        # Main application log
├── service-health.log              # Health monitoring
├── analytics/                      # Analytics logs
├── protocols/                      # Protocol-specific logs
├── services/                       # Service logs
└── archive/                        # Rotated logs

/etc/ubec/                          # System configuration
├── environment                     # Environment variables
└── ubec.conf                       # System config (if needed)
```

---

## Migration Steps

### Phase 1: Create System User (5 minutes)

```bash
# 1. Create dedicated system user
sudo useradd -r -s /bin/false -d /opt/ubec -c "UBEC Protocol Service" ubec

# Verify user created
id ubec

# Expected output:
# uid=XXX(ubec) gid=XXX(ubec) groups=XXX(ubec)

# 2. Add triag to ubec group (for management access)
sudo usermod -a -G ubec triag

# Verify group membership
groups triag

# Expected: triag should include 'ubec' group

# 3. Create sudoers entry for service management (optional)
echo "triag ALL=(ubec) NOPASSWD: /bin/systemctl restart ubec-protocol" | sudo tee /etc/sudoers.d/ubec-admin

# Set proper permissions
sudo chmod 440 /etc/sudoers.d/ubec-admin
```

### Phase 2: Copy Application Code (10 minutes)

```bash
# 1. Stop any running services
cd /home/triag/UBEC/projects/UBEC
pkill -f "python main.py"

# Verify nothing running
ps aux | grep "main.py"

# 2. Copy application code to /opt/ubec
sudo cp -r /home/triag/UBEC/projects/UBEC/* /opt/ubec/

# 3. Exclude certain directories (we'll handle separately)
sudo rm -rf /opt/ubec/logs
sudo rm -rf /opt/ubec/reports
sudo rm -rf /opt/ubec/backups
sudo rm -rf /opt/ubec/.git

# 4. Verify copy
ls -la /opt/ubec/

# Expected: All application files present except logs, reports, backups

# 5. Set ownership
sudo chown -R ubec:ubec /opt/ubec

# 6. Set permissions - code is read-only
sudo chmod -R 755 /opt/ubec
sudo chmod 750 /opt/ubec  # Main directory more restrictive

# 7. Make main.py executable
sudo chmod 755 /opt/ubec/main.py

# 8. Verify permissions
ls -la /opt/ubec/
```

### Phase 3: Set Up Python Environment (10 minutes)

```bash
# 1. Create virtual environment as ubec user
sudo -u ubec python3 -m venv /opt/ubec/venv

# 2. Upgrade pip
sudo -u ubec /opt/ubec/venv/bin/pip install --upgrade pip

# 3. Install dependencies
sudo -u ubec /opt/ubec/venv/bin/pip install -r /opt/ubec/requirements.txt

# Note: Add --break-system-packages if needed for stellar-sdk
sudo -u ubec /opt/ubec/venv/bin/pip install stellar-sdk --break-system-packages

# 4. Verify installation
sudo -u ubec /opt/ubec/venv/bin/python -c "import stellar_sdk; print(stellar_sdk.__version__)"

# Expected: Version number (e.g., 8.x.x)

# 5. Verify all key packages
sudo -u ubec /opt/ubec/venv/bin/pip list | grep -E "stellar-sdk|asyncpg|fastapi|uvicorn"

# Expected: All packages present
```

### Phase 4: Configure Environment (15 minutes)

```bash
# 1. Copy .env to /etc/ubec/environment
sudo cp /home/triag/UBEC/projects/UBEC/.env /etc/ubec/environment

# 2. Update paths in environment file
sudo nano /etc/ubec/environment
```

Update the following in `/etc/ubec/environment`:

```bash
# Database connection (keep as-is)
DB_HOST=localhost
DB_PORT=5432
DB_NAME=ubec
DB_USER=ubec_admin
DB_PASSWORD=<your-password>
DB_SCHEMA=ubec_main

# Updated paths for production
UBEC_BASE_DIR=/opt/ubec
UBEC_DATA_DIR=/var/lib/ubec
UBEC_LOG_DIR=/var/log/ubec
UBEC_CONFIG_DIR=/etc/ubec

# Logging configuration
LOG_LEVEL=INFO
LOG_FILE=/var/log/ubec/ubec.log

# Environment
UBEC_ENV=production
```

```bash
# 3. Set proper permissions on environment file
sudo chown root:ubec /etc/ubec/environment
sudo chmod 640 /etc/ubec/environment

# 4. Verify file is readable by ubec user
sudo -u ubec cat /etc/ubec/environment | head -5

# Expected: Should display first 5 lines

# 5. Create symbolic link in application (optional, for backward compatibility)
sudo ln -s /etc/ubec/environment /opt/ubec/.env
```

### Phase 5: Update Code for New Paths (20 minutes)

```bash
# 1. Update logging configuration
sudo nano /opt/ubec/config/logging.py
```

Find the `setup_logging()` function and ensure it uses environment-aware paths:

```python
def setup_logging(
    name: str = 'ubec',
    log_level: Optional[str] = None,
    log_file: Optional[str] = None,
    log_to_file: Optional[bool] = None
) -> logging.Logger:
    """Setup and configure logger for UBEC protocols."""
    
    # Get log directory from environment
    log_dir = os.getenv('UBEC_LOG_DIR', '/var/log/ubec')
    default_log_file = os.path.join(log_dir, 'ubec.log')
    
    # Use provided log_file or default
    actual_log_file = log_file or os.getenv('LOG_FILE', default_log_file)
    
    # Ensure log directory exists
    os.makedirs(os.path.dirname(actual_log_file), exist_ok=True)
    
    # ... rest of function
```

```bash
# 2. Update any hardcoded paths in code
# Search for potential hardcoded paths
cd /opt/ubec
sudo grep -r "logs/" --include="*.py" | grep -v ".pyc" | grep -v "venv"

# For each found instance, update to use:
# - os.getenv('UBEC_LOG_DIR', '/var/log/ubec')
# - os.getenv('UBEC_DATA_DIR', '/var/lib/ubec')

# 3. Update main.py if it has any path references
sudo nano /opt/ubec/main.py

# Ensure any path references use environment variables

# 4. Update reports/visualization output paths
# Find files that write reports
sudo grep -r "reports/" --include="*.py" /opt/ubec/services/
sudo grep -r "visualization/" --include="*.py" /opt/ubec/

# Update to use: os.path.join(os.getenv('UBEC_DATA_DIR', '/var/lib/ubec'), 'data', 'reports')
```

### Phase 6: Set Up Data Directories (5 minutes)

```bash
# 1. Set ownership
sudo chown -R ubec:ubec /var/lib/ubec
sudo chown -R ubec:ubec /var/log/ubec

# 2. Set permissions
sudo chmod 750 /var/lib/ubec
sudo chmod 750 /var/log/ubec
sudo chmod 750 /etc/ubec

# 3. Ensure ubec user can write to these directories
sudo -u ubec touch /var/log/ubec/test.log
sudo -u ubec touch /var/lib/ubec/test.data

# 4. Clean up test files
sudo rm /var/log/ubec/test.log
sudo rm /var/lib/ubec/test.data

# 5. Copy any existing reports to new location
if [ -d /home/triag/UBEC/projects/UBEC/reports ]; then
    sudo cp -r /home/triag/UBEC/projects/UBEC/reports/* /var/lib/ubec/data/reports/
    sudo chown -R ubec:ubec /var/lib/ubec/data/reports/
fi

# 6. Copy any existing visualizations
if [ -d /home/triag/UBEC/projects/UBEC/visualization ]; then
    sudo find /home/triag/UBEC/projects/UBEC/visualization -type f -name "*.png" -o -name "*.jpg" -o -name "*.svg" | \
    while read file; do
        sudo cp "$file" /var/lib/ubec/data/visualizations/
    done
    sudo chown -R ubec:ubec /var/lib/ubec/data/visualizations/
fi
```

### Phase 7: Configure Log Rotation (10 minutes)

```bash
# 1. Create logrotate configuration
sudo nano /etc/logrotate.d/ubec
```

Add the following content:

```
/var/log/ubec/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 0640 ubec ubec
    sharedscripts
    postrotate
        # Reload service to reopen log files
        /bin/systemctl reload ubec-protocol.service > /dev/null 2>&1 || true
    endscript
}

/var/log/ubec/*/*.log {
    daily
    rotate 14
    compress
    delaycompress
    missingok
    notifempty
    create 0640 ubec ubec
}
```

```bash
# 2. Set permissions
sudo chmod 644 /etc/logrotate.d/ubec

# 3. Test logrotate configuration
sudo logrotate -d /etc/logrotate.d/ubec

# Expected: No errors, shows what would happen

# 4. Force a test rotation (optional)
sudo logrotate -f /etc/logrotate.d/ubec
```

---

## Service Configuration

### Create Systemd Service File

```bash
# 1. Create service file
sudo nano /etc/systemd/system/ubec-protocol.service
```

Add the following content:

```ini
[Unit]
Description=UBEC Protocol Suite - Ubuntu Bioregional Economic Commons
Documentation=https://github.com/yourusername/ubec-protocol
After=network.target postgresql.service
Requires=postgresql.service
StartLimitIntervalSec=0

[Service]
Type=simple
User=ubec
Group=ubec
WorkingDirectory=/opt/ubec

# Environment
Environment="PATH=/opt/ubec/venv/bin:/usr/local/bin:/usr/bin:/bin"
Environment="PYTHONUNBUFFERED=1"
EnvironmentFile=/etc/ubec/environment

# Main command
ExecStart=/opt/ubec/venv/bin/python main.py serve --host 0.0.0.0 --port 8000

# Graceful shutdown for async operations
ExecStop=/bin/kill -SIGTERM $MAINPID
TimeoutStopSec=30

# Restart policy
Restart=always
RestartSec=10

# Resource limits
LimitNOFILE=65536
MemoryMax=2G

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=ubec-protocol

# Security hardening
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/var/log/ubec /var/lib/ubec

[Install]
WantedBy=multi-user.target
```

```bash
# 2. Set permissions
sudo chmod 644 /etc/systemd/system/ubec-protocol.service

# 3. Reload systemd
sudo systemctl daemon-reload

# 4. Enable service (don't start yet)
sudo systemctl enable ubec-protocol.service

# 5. Verify service configuration
systemctl cat ubec-protocol.service

# Expected: Shows the service file content
```

### Create Health Check Timer (Optional but Recommended)

```bash
# 1. Create health check service
sudo nano /etc/systemd/system/ubec-health-check.service
```

```ini
[Unit]
Description=UBEC Protocol Health Check
After=ubec-protocol.service

[Service]
Type=oneshot
User=ubec
Group=ubec
WorkingDirectory=/opt/ubec
Environment="PATH=/opt/ubec/venv/bin:/usr/local/bin:/usr/bin:/bin"
EnvironmentFile=/etc/ubec/environment
ExecStart=/opt/ubec/venv/bin/python main.py health --output /var/lib/ubec/state/health.json
StandardOutput=journal
StandardError=journal
SyslogIdentifier=ubec-health-check
```

```bash
# 2. Create timer
sudo nano /etc/systemd/system/ubec-health-check.timer
```

```ini
[Unit]
Description=Run UBEC health check every 5 minutes
Requires=ubec-health-check.service

[Timer]
OnBootSec=5min
OnUnitActiveSec=5min
AccuracySec=1s

[Install]
WantedBy=timers.target
```

```bash
# 3. Enable and start timer
sudo systemctl enable ubec-health-check.timer
sudo systemctl start ubec-health-check.timer

# 4. Verify timer is active
systemctl list-timers ubec-health-check.timer

# Expected: Shows next execution time
```

---

## Testing & Verification

### Pre-Start Verification (10 minutes)

```bash
# 1. Verify all files are owned by ubec
ls -la /opt/ubec/ | head -20

# Expected: All files owned by ubec:ubec

# 2. Verify environment file is accessible
sudo -u ubec cat /etc/ubec/environment | grep "DB_HOST"

# Expected: Should show DB_HOST value

# 3. Test database connection as ubec user
sudo -u ubec /opt/ubec/venv/bin/python -c "
import os
from dotenv import load_dotenv
load_dotenv('/etc/ubec/environment')
print(f'DB Host: {os.getenv(\"DB_HOST\")}')
print(f'DB Name: {os.getenv(\"DB_NAME\")}')
print(f'Log Dir: {os.getenv(\"UBEC_LOG_DIR\")}')
"

# Expected: Shows configuration values

# 4. Test Python imports
sudo -u ubec /opt/ubec/venv/bin/python -c "
import sys
sys.path.insert(0, '/opt/ubec')
from core.service_registry import ServiceRegistry
print('✓ Imports successful')
"

# Expected: ✓ Imports successful

# 5. Verify write permissions to log directory
sudo -u ubec touch /var/log/ubec/test-write.log && sudo rm /var/log/ubec/test-write.log

# Expected: No errors
```

### Start Service (5 minutes)

```bash
# 1. Start the service
sudo systemctl start ubec-protocol.service

# 2. Check immediate status
sudo systemctl status ubec-protocol.service

# Expected: active (running)

# 3. Watch logs for startup
sudo journalctl -u ubec-protocol -f

# Watch for:
# - "REGISTERING SERVICES WITH SERVICE REGISTRY"
# - "✓ Configuration service initialized"
# - "✓ Database connection pool created"
# - "✅ Scheduler started - background jobs active"
# - API server startup messages

# Press Ctrl+C to stop watching

# 4. Check for errors
sudo journalctl -u ubec-protocol --since "5 minutes ago" | grep -i error

# Expected: No critical errors (some warnings may be normal)

# 5. Verify process is running
ps aux | grep "python main.py serve"

# Expected: Shows process running as 'ubec' user
```

### Functional Testing (15 minutes)

```bash
# 1. Wait 60 seconds for full initialization
sleep 60

# 2. Test health endpoint
curl http://localhost:8000/api/v1/health | jq '.'

# Expected: JSON response with healthy services

# 3. Test tokens endpoint
curl http://localhost:8000/api/v1/tokens | jq '.'

# Expected: JSON array with 4 tokens (UBEC, UBECrc, UBECgpi, UBECtt)

# 4. Check service health via CLI
cd /opt/ubec
sudo -u ubec /opt/ubec/venv/bin/python main.py health

# Expected: All services showing healthy status

# 5. Verify log files are being written
ls -lh /var/log/ubec/

# Expected: ubec.log exists and is growing

# 6. Check log content
sudo tail -50 /var/log/ubec/ubec.log

# Expected: Recent log entries

# 7. Verify scheduler is running
sudo journalctl -u ubec-protocol --since "5 minutes ago" | grep -i "scheduler"

# Expected: "✅ Scheduler started" message

# 8. Test database connectivity
sudo -u ubec /opt/ubec/venv/bin/python -c "
import asyncio
import sys
sys.path.insert(0, '/opt/ubec')
from core.db.database_manager import AsyncDatabaseManager

async def test():
    from dotenv import load_dotenv
    load_dotenv('/etc/ubec/environment')
    db = AsyncDatabaseManager()
    await db.initialize()
    result = await db.execute_query(
        'SELECT COUNT(*) as count FROM ubec_main.account_balances',
        schema='ubec_main'
    )
    print(f'Balance records: {result[0][\"count\"]}')
    await db.cleanup()

asyncio.run(test())
"

# Expected: Shows record count (87,567+)

# 9. Verify API rate limiting works
for i in {1..5}; do
  curl -s http://localhost:8000/api/v1/tokens > /dev/null
  echo "Request $i completed"
done

# Expected: All requests succeed (rate limit is 100/min by default)

# 10. Check service registry health
curl http://localhost:8000/api/v1/health | jq '.services'

# Expected: All services showing "healthy" status
```

### Performance Verification (10 minutes)

```bash
# 1. Check memory usage
ps aux | grep "python main.py serve" | awk '{print $4, $6, $11}'

# Expected: <10% memory usage, <500MB RSS

# 2. Check file descriptors
sudo lsof -u ubec | wc -l

# Expected: <1000 open files

# 3. Test API response time
time curl -s http://localhost:8000/api/v1/tokens > /dev/null

# Expected: <100ms

# 4. Check database connection pool
sudo -u ubec /opt/ubec/venv/bin/python -c "
import asyncio
import sys
sys.path.insert(0, '/opt/ubec')

async def check_pool():
    from core.service_registry import ServiceRegistry
    from dotenv import load_dotenv
    load_dotenv('/etc/ubec/environment')
    
    registry = ServiceRegistry()
    await registry.initialize()
    db = await registry.get('database')
    health = await db.health_check()
    print(f'Pool status: {health[\"status\"]}')
    print(f'Active connections: {health[\"details\"].get(\"active_connections\", \"N/A\")}')
    await registry.cleanup()

asyncio.run(check_pool())
"

# Expected: healthy status, reasonable connection count

# 5. Monitor for 5 minutes and check stability
echo "Monitoring for 5 minutes..."
for i in {1..10}; do
  sleep 30
  curl -s http://localhost:8000/api/v1/health | jq -r '.status'
done

# Expected: All checks return "healthy"
```

---

## Rollback Plan

### If Migration Fails

```bash
# 1. Stop production service
sudo systemctl stop ubec-protocol.service
sudo systemctl disable ubec-protocol.service

# 2. Restore from backup
BACKUP_DIR="<your-backup-directory>"
cd /home/triag/UBEC/projects
tar -xzf "$BACKUP_DIR/ubec_project_complete.tar.gz"

# 3. Restore database if needed
pg_restore -U ubec_admin -d ubec -c "$BACKUP_DIR/ubec_database_*.dump"

# 4. Restart development environment
cd /home/triag/UBEC/projects/UBEC
python main.py serve

# 5. Remove production directories (optional)
sudo rm -rf /opt/ubec
sudo rm -rf /etc/ubec/environment
sudo rm /etc/systemd/system/ubec-protocol.service
sudo systemctl daemon-reload
```

### Partial Rollback (Keep Production, Fix Issues)

```bash
# 1. Stop service
sudo systemctl stop ubec-protocol.service

# 2. Fix specific issue (example: wrong permissions)
sudo chown -R ubec:ubec /opt/ubec
sudo chmod -R 755 /opt/ubec

# 3. Restart service
sudo systemctl start ubec-protocol.service

# 4. Check logs
sudo journalctl -u ubec-protocol -f
```

---

## Post-Migration Tasks

### Day 1: Immediate Monitoring (First 24 Hours)

```bash
# 1. Create monitoring script
cat > /home/triag/monitor_ubec.sh << 'EOF'
#!/bin/bash
# UBEC Production Monitoring Script

echo "=== UBEC Production Health Check ==="
echo "Time: $(date)"
echo ""

# Service status
echo "1. Service Status:"
systemctl is-active ubec-protocol.service
echo ""

# API health
echo "2. API Health:"
curl -s http://localhost:8000/api/v1/health | jq -r '.status'
echo ""

# Log errors (last hour)
echo "3. Recent Errors:"
sudo journalctl -u ubec-protocol --since "1 hour ago" | grep -i error | tail -5
echo ""

# Memory usage
echo "4. Memory Usage:"
ps aux | grep "python main.py serve" | grep -v grep | awk '{print "  Memory: " $4 "% (" $6 " KB)"}'
echo ""

# Disk space
echo "5. Disk Space:"
df -h /opt /var | grep -E "Filesystem|/opt|/var"
echo ""

# Database connectivity
echo "6. Database Status:"
psql -U ubec_admin -d ubec -c "SELECT COUNT(*) FROM ubec_main.account_balances;" | tail -3
echo ""

echo "=== End Health Check ==="
EOF

chmod +x /home/triag/monitor_ubec.sh

# 2. Run monitoring every 15 minutes for first 24 hours
crontab -e
# Add: */15 * * * * /home/triag/monitor_ubec.sh >> /home/triag/ubec_monitoring.log 2>&1

# 3. Watch logs continuously (in separate terminal)
sudo journalctl -u ubec-protocol -f

# 4. Check health status regularly
watch -n 60 'curl -s http://localhost:8000/api/v1/health | jq .'
```

### Week 1: Stabilization Tasks

```bash
# 1. Review logs daily
sudo journalctl -u ubec-protocol --since "24 hours ago" | grep -E "ERROR|WARNING" > /home/triag/daily_issues_$(date +%Y%m%d).log

# 2. Monitor disk usage
df -h /var/log/ubec /var/lib/ubec

# 3. Check database growth
psql -U ubec_admin -d ubec -c "
SELECT 
    pg_size_pretty(pg_database_size('ubec')) as db_size,
    (SELECT COUNT(*) FROM ubec_main.account_balances) as balance_count,
    (SELECT COUNT(*) FROM ubec_main.holonic_scores) as score_count;
"

# 4. Verify backups are running
ls -lh /home/triag/backups/

# 5. Test service restart
sudo systemctl restart ubec-protocol.service
sleep 30
curl -s http://localhost:8000/api/v1/health | jq '.status'
```

### Ongoing Maintenance Setup

```bash
# 1. Set up automated backups
cat > /usr/local/bin/backup-ubec.sh << 'EOF'
#!/bin/bash
# UBEC Automated Backup Script

BACKUP_DIR="/home/triag/backups/production"
DATE=$(date +%Y%m%d)
mkdir -p "$BACKUP_DIR"

# Backup database
pg_dump -U ubec_admin -d ubec -F c -f "$BACKUP_DIR/ubec_db_$DATE.dump"

# Backup configuration
tar -czf "$BACKUP_DIR/ubec_config_$DATE.tar.gz" /etc/ubec

# Backup application state
tar -czf "$BACKUP_DIR/ubec_state_$DATE.tar.gz" /var/lib/ubec

# Remove backups older than 30 days
find "$BACKUP_DIR" -name "*.dump" -mtime +30 -delete
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +30 -delete

echo "Backup completed: $DATE"
EOF

sudo chmod +x /usr/local/bin/backup-ubec.sh

# 2. Schedule daily backups
sudo crontab -e
# Add: 0 2 * * * /usr/local/bin/backup-ubec.sh >> /var/log/ubec/backup.log 2>&1

# 3. Set up monitoring alerts (using email)
cat > /usr/local/bin/ubec-health-alert.sh << 'EOF'
#!/bin/bash
# UBEC Health Alert Script

HEALTH=$(curl -s http://localhost:8000/api/v1/health | jq -r '.status')

if [ "$HEALTH" != "healthy" ]; then
    echo "ALERT: UBEC Protocol health check failed" | mail -s "UBEC Alert" admin@example.com
fi
EOF

sudo chmod +x /usr/local/bin/ubec-health-alert.sh

# Schedule health checks
sudo crontab -e
# Add: */10 * * * * /usr/local/bin/ubec-health-alert.sh

# 4. Document the production setup
cat > /home/triag/PRODUCTION_SETUP_DOCS.md << 'EOF'
# UBEC Production Setup Documentation

## Migration Date
$(date)

## Directory Structure
- Application: /opt/ubec
- Data: /var/lib/ubec
- Logs: /var/log/ubec
- Config: /etc/ubec

## Service Management
- Start: sudo systemctl start ubec-protocol
- Stop: sudo systemctl stop ubec-protocol
- Restart: sudo systemctl restart ubec-protocol
- Status: sudo systemctl status ubec-protocol
- Logs: sudo journalctl -u ubec-protocol -f

## Backup Locations
- Database: /home/triag/backups/production/
- Automated: Daily at 2:00 AM

## Monitoring
- Health Check: curl http://localhost:8000/api/v1/health
- Monitoring Script: /home/triag/monitor_ubec.sh
- Alert Script: /usr/local/bin/ubec-health-alert.sh

## Emergency Contacts
- Database Admin: ubec_admin
- Service User: ubec
- System Admin: triag

## Common Issues
1. Service won't start: Check logs with journalctl
2. Permission errors: Verify ownership with ls -la
3. Database connection: Test with psql -U ubec_admin -d ubec

EOF
```

### Update Development Environment

```bash
# 1. Keep development environment at current location
cd /home/triag/UBEC/projects/UBEC

# 2. Create deployment script for future updates
cat > deploy_to_production.sh << 'EOF'
#!/bin/bash
# Deploy Development Changes to Production

set -e

echo "=== UBEC Production Deployment Script ==="
echo "This will deploy current code to /opt/ubec"
read -p "Continue? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Deployment cancelled"
    exit 0
fi

# Stop production service
echo "Stopping production service..."
sudo systemctl stop ubec-protocol.service

# Backup current production
echo "Backing up current production..."
BACKUP_DIR="/home/triag/backups/production_updates"
mkdir -p "$BACKUP_DIR"
sudo tar -czf "$BACKUP_DIR/ubec_pre_update_$(date +%Y%m%d_%H%M%S).tar.gz" /opt/ubec

# Copy new code
echo "Copying new code..."
sudo cp -r /home/triag/UBEC/projects/UBEC/* /opt/ubec/

# Exclude directories
sudo rm -rf /opt/ubec/logs
sudo rm -rf /opt/ubec/reports
sudo rm -rf /opt/ubec/backups
sudo rm -rf /opt/ubec/.git

# Fix ownership
echo "Setting ownership..."
sudo chown -R ubec:ubec /opt/ubec

# Update dependencies
echo "Updating Python dependencies..."
sudo -u ubec /opt/ubec/venv/bin/pip install -r /opt/ubec/requirements.txt

# Start service
echo "Starting production service..."
sudo systemctl start ubec-protocol.service

# Wait for startup
echo "Waiting for service to start..."
sleep 10

# Check health
echo "Checking health..."
curl -s http://localhost:8000/api/v1/health | jq '.status'

echo "=== Deployment Complete ==="
echo "Monitor logs: sudo journalctl -u ubec-protocol -f"
EOF

chmod +x deploy_to_production.sh

# 3. Create git workflow for tracking changes
git init
git add .
git commit -m "Production baseline - $(date +%Y-%m-%d)"

# 4. Add .gitignore
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
ENV/

# UBEC specific
.env
logs/
reports/
backups/
*.log

# Database
*.dump
*.sql.backup

# IDE
.vscode/
.idea/
*.swp
*.swo
EOF
```

---

## Migration Completion Checklist

### Final Verification

- [ ] All services running: `systemctl status ubec-protocol.service`
- [ ] Health check passing: `curl http://localhost:8000/api/v1/health`
- [ ] Database connectivity verified
- [ ] Logs being written to /var/log/ubec/
- [ ] Scheduler running and executing jobs
- [ ] API responding on port 8000
- [ ] All 15 services showing healthy status
- [ ] No errors in journalctl logs
- [ ] Memory usage < 10%
- [ ] Backups configured and tested
- [ ] Log rotation configured
- [ ] Monitoring scripts in place
- [ ] Development environment remains functional
- [ ] Deployment script created and tested
- [ ] Documentation updated

### Sign-Off

```bash
# Generate migration report
cat > /home/triag/UBEC_MIGRATION_REPORT_$(date +%Y%m%d).txt << EOF
UBEC Protocol Suite - Production Migration Report
==================================================
Migration Date: $(date)
Migrated By: triag

Status: [ ] SUCCESS [ ] FAILED

Production Locations:
- Application: /opt/ubec
- Data: /var/lib/ubec  
- Logs: /var/log/ubec
- Config: /etc/ubec

Service Status:
$(systemctl status ubec-protocol.service | head -10)

Health Check:
$(curl -s http://localhost:8000/api/v1/health | jq '.')

Database Records:
$(psql -U ubec_admin -d ubec -t -c "SELECT COUNT(*) FROM ubec_main.account_balances;")

Notes:
- Development environment retained at /home/triag/UBEC/projects/UBEC/
- Backups located at /home/triag/backups/
- Next steps: Monitor for 24 hours, then proceed with December 15 launch prep

Signature: ________________  Date: __________
EOF

cat /home/triag/UBEC_MIGRATION_REPORT_$(date +%Y%m%d).txt
```

---

## Support and Troubleshooting

### Common Issues and Solutions

**Issue 1: Permission Denied Errors**

```bash
# Solution: Fix ownership
sudo chown -R ubec:ubec /opt/ubec /var/lib/ubec /var/log/ubec
sudo chmod 750 /opt/ubec /var/lib/ubec /var/log/ubec
```

**Issue 2: Service Won't Start**

```bash
# Check logs
sudo journalctl -u ubec-protocol -n 100 --no-pager

# Check file syntax
sudo -u ubec /opt/ubec/venv/bin/python -m py_compile /opt/ubec/main.py

# Test manually
sudo -u ubec /opt/ubec/venv/bin/python /opt/ubec/main.py health
```

**Issue 3: Database Connection Failed**

```bash
# Test connection
psql -U ubec_admin -d ubec -c "SELECT 1;"

# Check environment file
sudo cat /etc/ubec/environment | grep DB_

# Test Python connection
sudo -u ubec /opt/ubec/venv/bin/python -c "
from dotenv import load_dotenv
import os
load_dotenv('/etc/ubec/environment')
print(f'Host: {os.getenv(\"DB_HOST\")}')
print(f'DB: {os.getenv(\"DB_NAME\")}')
"
```

**Issue 4: API Not Responding**

```bash
# Check if port is listening
sudo netstat -tlnp | grep 8000

# Check firewall
sudo ufw status | grep 8000

# Test local connection
curl -v http://localhost:8000/api/v1/health
```

**Issue 5: High Memory Usage**

```bash
# Check current usage
ps aux | grep "python main.py" | grep -v grep

# Restart service
sudo systemctl restart ubec-protocol.service

# Monitor memory over time
watch -n 5 'ps aux | grep "python main.py" | grep -v grep'
```

---

## Attribution

This project uses the services of Claude and Anthropic PBC to inform our decisions and recommendations. This project was made possible with the assistance of Claude and Anthropic PBC.

---

**End of Migration Plan**
