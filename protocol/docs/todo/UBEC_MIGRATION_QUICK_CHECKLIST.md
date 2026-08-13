# UBEC Production Migration - Quick Reference Checklist

**Target**: Move from `/home/triag/UBEC/projects/UBEC/` to production structure  
**Time**: 2-3 hours  
**Risk**: MEDIUM (with rollback available)

---

## 📋 PRE-MIGRATION (30 minutes)

### Backup Everything
```bash
BACKUP_DIR="/home/triag/backups/ubec_migration_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
cd /home/triag/UBEC/projects
tar -czf "$BACKUP_DIR/ubec_project_complete.tar.gz" UBEC/
pg_dump -U ubec_admin -d ubec -F c -f "$BACKUP_DIR/ubec_database_$(date +%Y%m%d).dump"
cp /home/triag/UBEC/projects/UBEC/.env "$BACKUP_DIR/.env.backup"
ls -lh "$BACKUP_DIR"
```

### System Checks
```bash
□ df -h /opt /var                    # Check disk space (need 5GB)
□ systemctl status postgresql        # Verify PostgreSQL running
□ python main.py health              # Current system health
```

---

## 🏗️ CREATE STRUCTURE (15 minutes)

### Directories
```bash
sudo mkdir -p /opt/ubec
sudo mkdir -p /var/lib/ubec/{state,data}
sudo mkdir -p /var/log/ubec/{archive,services,analytics,protocols}
sudo mkdir -p /etc/ubec
```

### System User
```bash
sudo useradd -r -s /bin/false -d /opt/ubec -c "UBEC Protocol Service" ubec
sudo usermod -a -G ubec triag
id ubec
```

---

## 📦 COPY APPLICATION (20 minutes)

### Stop Current Service
```bash
cd /home/triag/UBEC/projects/UBEC
pkill -f "python main.py"
ps aux | grep "main.py"  # Verify stopped
```

### Copy Files
```bash
sudo cp -r /home/triag/UBEC/projects/UBEC/* /opt/ubec/
sudo rm -rf /opt/ubec/{logs,reports,backups,.git}
sudo chown -R ubec:ubec /opt/ubec
sudo chmod 750 /opt/ubec
sudo chmod 755 /opt/ubec/main.py
```

### Python Environment
```bash
sudo -u ubec python3 -m venv /opt/ubec/venv
sudo -u ubec /opt/ubec/venv/bin/pip install --upgrade pip
sudo -u ubec /opt/ubec/venv/bin/pip install -r /opt/ubec/requirements.txt
sudo -u ubec /opt/ubec/venv/bin/pip install stellar-sdk --break-system-packages
```

---

## ⚙️ CONFIGURE (25 minutes)

### Environment File
```bash
sudo cp /home/triag/UBEC/projects/UBEC/.env /etc/ubec/environment
sudo nano /etc/ubec/environment
```

Add these lines:
```bash
UBEC_BASE_DIR=/opt/ubec
UBEC_DATA_DIR=/var/lib/ubec
UBEC_LOG_DIR=/var/log/ubec
UBEC_CONFIG_DIR=/etc/ubec
UBEC_ENV=production
LOG_FILE=/var/log/ubec/ubec.log
```

```bash
sudo chown root:ubec /etc/ubec/environment
sudo chmod 640 /etc/ubec/environment
sudo ln -s /etc/ubec/environment /opt/ubec/.env
```

### Update Code Paths
```bash
sudo nano /opt/ubec/config/logging.py
```

Ensure:
```python
log_dir = os.getenv('UBEC_LOG_DIR', '/var/log/ubec')
default_log_file = os.path.join(log_dir, 'ubec.log')
os.makedirs(os.path.dirname(actual_log_file), exist_ok=True)
```

### Set Permissions
```bash
sudo chown -R ubec:ubec /var/lib/ubec /var/log/ubec
sudo chmod 750 /var/lib/ubec /var/log/ubec /etc/ubec
```

---

## 🔧 SYSTEMD SERVICE (15 minutes)

### Service File
```bash
sudo nano /etc/systemd/system/ubec-protocol.service
```

Paste:
```ini
[Unit]
Description=UBEC Protocol Suite
After=network.target postgresql.service
Requires=postgresql.service

[Service]
Type=simple
User=ubec
Group=ubec
WorkingDirectory=/opt/ubec
Environment="PATH=/opt/ubec/venv/bin:/usr/local/bin:/usr/bin:/bin"
Environment="PYTHONUNBUFFERED=1"
EnvironmentFile=/etc/ubec/environment
ExecStart=/opt/ubec/venv/bin/python main.py serve --host 0.0.0.0 --port 8000
ExecStop=/bin/kill -SIGTERM $MAINPID
TimeoutStopSec=30
Restart=always
RestartSec=10
LimitNOFILE=65536
MemoryMax=2G
StandardOutput=journal
StandardError=journal
SyslogIdentifier=ubec-protocol
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/var/log/ubec /var/lib/ubec

[Install]
WantedBy=multi-user.target
```

### Enable Service
```bash
sudo systemctl daemon-reload
sudo systemctl enable ubec-protocol.service
```

---

## 🚀 START & TEST (30 minutes)

### Pre-Start Tests
```bash
□ sudo -u ubec cat /etc/ubec/environment | head -5
□ sudo -u ubec /opt/ubec/venv/bin/python -c "from core.service_registry import ServiceRegistry; print('OK')"
□ sudo -u ubec touch /var/log/ubec/test.log && sudo rm /var/log/ubec/test.log
```

### Start Service
```bash
sudo systemctl start ubec-protocol.service
sudo systemctl status ubec-protocol.service
sudo journalctl -u ubec-protocol -f  # Watch startup
```

### Verify Health (Wait 60 seconds first)
```bash
□ curl http://localhost:8000/api/v1/health | jq '.status'           # Should be "healthy"
□ curl http://localhost:8000/api/v1/tokens | jq '.'                 # Should return 4 tokens
□ sudo -u ubec /opt/ubec/venv/bin/python /opt/ubec/main.py health  # All services healthy
□ sudo tail -50 /var/log/ubec/ubec.log                              # Check logs
□ ps aux | grep "python main.py serve"                              # Running as ubec
```

### Performance Check
```bash
□ ps aux | grep "python main.py serve" | awk '{print $4, $6}'      # Memory <10%, <500MB
□ time curl -s http://localhost:8000/api/v1/tokens > /dev/null     # Response <100ms
□ sudo lsof -u ubec | wc -l                                         # Files <1000
```

---

## 📊 POST-MIGRATION (Ongoing)

### Day 1 Monitoring Script
```bash
cat > /home/triag/monitor_ubec.sh << 'EOF'
#!/bin/bash
echo "=== UBEC Health $(date) ==="
echo "Service: $(systemctl is-active ubec-protocol.service)"
echo "API: $(curl -s http://localhost:8000/api/v1/health | jq -r '.status')"
echo "Errors: $(sudo journalctl -u ubec-protocol --since "1 hour ago" | grep -i error | wc -l)"
echo "Memory: $(ps aux | grep 'python main.py serve' | grep -v grep | awk '{print $4"%"}')"
df -h /opt /var | grep -E "Filesystem|/opt|/var"
EOF
chmod +x /home/triag/monitor_ubec.sh

# Run every 15 minutes
crontab -e
# Add: */15 * * * * /home/triag/monitor_ubec.sh >> /home/triag/ubec_monitoring.log 2>&1
```

### Daily Backup Script
```bash
cat > /usr/local/bin/backup-ubec.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/home/triag/backups/production"
DATE=$(date +%Y%m%d)
mkdir -p "$BACKUP_DIR"
pg_dump -U ubec_admin -d ubec -F c -f "$BACKUP_DIR/ubec_db_$DATE.dump"
tar -czf "$BACKUP_DIR/ubec_config_$DATE.tar.gz" /etc/ubec
tar -czf "$BACKUP_DIR/ubec_state_$DATE.tar.gz" /var/lib/ubec
find "$BACKUP_DIR" -name "*.dump" -mtime +30 -delete
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +30 -delete
EOF
sudo chmod +x /usr/local/bin/backup-ubec.sh

# Schedule daily at 2 AM
sudo crontab -e
# Add: 0 2 * * * /usr/local/bin/backup-ubec.sh >> /var/log/ubec/backup.log 2>&1
```

### Deployment Script (Development to Production)
```bash
cat > /home/triag/UBEC/projects/UBEC/deploy_to_production.sh << 'EOF'
#!/bin/bash
set -e
read -p "Deploy to production? (yes/no): " confirm
[ "$confirm" != "yes" ] && exit 0

sudo systemctl stop ubec-protocol.service
BACKUP_DIR="/home/triag/backups/production_updates"
mkdir -p "$BACKUP_DIR"
sudo tar -czf "$BACKUP_DIR/ubec_pre_update_$(date +%Y%m%d_%H%M%S).tar.gz" /opt/ubec
sudo cp -r /home/triag/UBEC/projects/UBEC/* /opt/ubec/
sudo rm -rf /opt/ubec/{logs,reports,backups,.git}
sudo chown -R ubec:ubec /opt/ubec
sudo -u ubec /opt/ubec/venv/bin/pip install -r /opt/ubec/requirements.txt
sudo systemctl start ubec-protocol.service
sleep 10
curl -s http://localhost:8000/api/v1/health | jq '.status'
echo "Deployment complete. Monitor: sudo journalctl -u ubec-protocol -f"
EOF
chmod +x /home/triag/UBEC/projects/UBEC/deploy_to_production.sh
```

---

## 🔄 ROLLBACK (If Needed)

```bash
# Stop production
sudo systemctl stop ubec-protocol.service
sudo systemctl disable ubec-protocol.service

# Restore from backup
BACKUP_DIR="<your-backup-directory>"
cd /home/triag/UBEC/projects
tar -xzf "$BACKUP_DIR/ubec_project_complete.tar.gz"

# Restart development
cd /home/triag/UBEC/projects/UBEC
python main.py serve
```

---

## ✅ FINAL CHECKLIST

### Must Pass Before Production Launch
- [ ] Service running: `systemctl status ubec-protocol.service`
- [ ] Health check: `curl http://localhost:8000/api/v1/health | jq '.status'` = "healthy"
- [ ] All 15 services healthy
- [ ] API responding on port 8000
- [ ] Scheduler executing jobs
- [ ] Logs written to /var/log/ubec/
- [ ] No errors in journal: `sudo journalctl -u ubec-protocol --since "1 hour ago" | grep -i error`
- [ ] Memory < 10%, < 500MB
- [ ] Backups configured and tested
- [ ] Log rotation working
- [ ] Monitoring scripts active
- [ ] Development environment functional
- [ ] Deployment script tested
- [ ] Documentation updated

---

## 📞 QUICK COMMANDS

```bash
# Service Management
sudo systemctl {start|stop|restart|status} ubec-protocol.service
sudo journalctl -u ubec-protocol -f

# Health Checks
curl http://localhost:8000/api/v1/health | jq '.'
sudo -u ubec /opt/ubec/venv/bin/python /opt/ubec/main.py health

# Logs
sudo tail -f /var/log/ubec/ubec.log
sudo journalctl -u ubec-protocol --since "1 hour ago"

# Database
psql -U ubec_admin -d ubec -c "SELECT COUNT(*) FROM ubec_main.account_balances;"

# Deployment
/home/triag/UBEC/projects/UBEC/deploy_to_production.sh

# Monitoring
/home/triag/monitor_ubec.sh
tail -f /home/triag/ubec_monitoring.log
```

---

## 📚 DOCUMENTATION LOCATIONS

- Full Migration Plan: `/home/claude/UBEC_PRODUCTION_MIGRATION_PLAN.md`
- This Checklist: `/home/claude/UBEC_MIGRATION_QUICK_CHECKLIST.md`
- Production Setup: `/home/triag/PRODUCTION_SETUP_DOCS.md` (created post-migration)
- Migration Report: `/home/triag/UBEC_MIGRATION_REPORT_*.txt` (created post-migration)

---

**Attribution**: This project uses the services of Claude and Anthropic PBC to inform our decisions and recommendations. This project was made possible with the assistance of Claude and Anthropic PBC.
