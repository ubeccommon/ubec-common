# UBEC DAO Protocol Suite - System Administrator Onboarding Guide

**Version:** 1.0  
**Last Updated:** November 2, 2025  
**Target Audience:** System Administrators  
**Estimated Onboarding Time:** 4-6 hours

---

## Document Overview

This guide provides comprehensive onboarding for System Administrators responsible for deploying, operating, and maintaining the UBEC (Ubuntu Bioregional Economic Commons) DAO Protocol Suite. This system implements a sophisticated blockchain-based economic platform built on the Stellar network with a four-element token ecosystem.

**Attribution:** This project uses the services of Claude and Anthropic PBC to inform our decisions and recommendations. This project was made possible with the assistance of Claude and Anthropic PBC.

---

## Table of Contents

1. [System Architecture Overview](#system-architecture-overview)
2. [Prerequisites and Access Requirements](#prerequisites-and-access-requirements)
3. [Initial Setup and Configuration](#initial-setup-and-configuration)
4. [Service Management](#service-management)
5. [Monitoring and Health Checks](#monitoring-and-health-checks)
6. [Operational Procedures](#operational-procedures)
7. [Security Management](#security-management)
8. [Backup and Recovery](#backup-and-recovery)
9. [Troubleshooting](#troubleshooting)
10. [Common Administrative Tasks](#common-administrative-tasks)

---

## System Architecture Overview

### High-Level Architecture

The UBEC Protocol Suite is a production-ready system with the following characteristics:

- **Single Entry Point:** `main.py` is the ONLY executable - all other modules are services
- **Service Registry Pattern:** Centralized dependency management with automatic initialization
- **100% Async Operations:** No blocking code anywhere in the system
- **Database-Backed Configuration:** PostgreSQL as single source of truth
- **Blockchain Integration:** Stellar network via Horizon API with rate limiting
- **15 Registered Services:** Each with standardized health checks

### Technology Stack

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **Blockchain** | Stellar Network | Mainnet | Distributed ledger |
| **Database** | PostgreSQL | 15.13+ | Data persistence |
| **Runtime** | Python | 3.11+ | Application runtime |
| **API Client** | stellar-sdk | 9.0.0+ | Blockchain interaction |
| **DB Driver** | asyncpg | 0.28.0+ | Async database access |
| **Web Client** | aiohttp | 3.8.0+ | HTTP operations |

### System Components

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚                         main.py                              â”‚
â”‚                    (Sole Entry Point)                        â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                              â”‚
                              â–¼
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚                    Service Registry                          â”‚
â”‚           (Dependency Injection & Lifecycle)                 â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                              â”‚
        â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
        â”‚                     â”‚                     â”‚
        â–¼                     â–¼                     â–¼
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”    â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”    â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ Infrastructureâ”‚    â”‚  Protocol    â”‚    â”‚ Operational  â”‚
â”‚   Services   â”‚    â”‚  Services    â”‚    â”‚  Services    â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤    â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤    â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ â€¢ Database   â”‚    â”‚ â€¢ Air (UBEC) â”‚    â”‚ â€¢ Sync       â”‚
â”‚ â€¢ Config     â”‚    â”‚ â€¢ Water (rc) â”‚    â”‚ â€¢ Analytics  â”‚
â”‚ â€¢ Stellar    â”‚    â”‚ â€¢ Earth (gpi)â”‚    â”‚ â€¢ Evaluator  â”‚
â”‚              â”‚    â”‚ â€¢ Fire (tt)  â”‚    â”‚ â€¢ Visualizer â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜    â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜    â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

### Four-Element Token Ecosystem

| Token | Element | Ubuntu Principle | Issuer Account (Last 5) | Status |
|-------|---------|------------------|------------------------|--------|
| **UBEC** | Air | Diversity | ...FHVKZ | âœ… Mainnet |
| **UBECrc** | Water | Reciprocity | ...Z5UBEC | âœ… Mainnet |
| **UBECgpi** | Earth | Mutualism | ...NT5SUBEC | âœ… Mainnet |
| **UBECtt** | Fire | Regeneration | ...65Z5UBEC | âœ… Mainnet |

---

## Prerequisites and Access Requirements

### System Requirements

**Minimum Hardware:**
- CPU: 4 cores (8 cores recommended)
- RAM: 8 GB (16 GB recommended)
- Storage: 50 GB SSD (100 GB recommended)
- Network: 100 Mbps connection

**Operating System:**
- Ubuntu 22.04 LTS or 24.04 LTS (recommended)
- Python 3.11 or higher
- PostgreSQL 15.13 or higher

### Required Access

**Administrative Access:**
- `sudo` privileges on application server
- PostgreSQL superuser or database owner role
- SSH access to deployment server
- Git repository access

**Network Access:**
- Outbound HTTPS (443) to Stellar Horizon API
- Inbound access to application ports (if applicable)
- Database port (5432) between application and database servers

**Credentials Required:**
- PostgreSQL connection credentials
- Stellar API access (public network)
- Monitoring system credentials (if applicable)

### Software Dependencies

**Python Packages (install via requirements.txt):**
```
stellar-sdk>=9.0.0
asyncpg>=0.28.0
psycopg2-binary>=2.9.0
aiohttp>=3.8.0
python-dotenv>=1.0.0
matplotlib>=3.7.0
numpy>=1.24.0
scipy>=1.10.0
```

**System Packages:**
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y \
    python3.11 \
    python3.11-venv \
    python3-pip \
    postgresql-15 \
    postgresql-contrib \
    git \
    build-essential \
    libpq-dev
```

---

## Initial Setup and Configuration

### Step 1: Clone Repository

```bash
# Clone the repository
cd /opt
sudo git clone <repository-url> ubec-protocol
sudo chown -R $USER:$USER ubec-protocol
cd ubec-protocol
```

### Step 2: Create Python Virtual Environment

```bash
# Create virtual environment
python3.11 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Configure Environment Variables

```bash
# Copy example environment file
cp .env.example .env

# Edit with your configuration
nano .env
```

**Required Environment Variables:**

```bash
# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=ubec
DB_USER=ubec_admin
DB_PASSWORD=<secure-password>
DB_POOL_MIN=5
DB_POOL_MAX=20

# Stellar Network Configuration
STELLAR_NETWORK=public
STELLAR_HORIZON_URL=https://horizon.stellar.org

# Rate Limiting
STELLAR_RATE_LIMIT=3000  # requests per hour
STELLAR_RATE_LIMIT_WINDOW=3600  # seconds

# Application Configuration
LOG_LEVEL=INFO
LOG_FILE=/var/log/ubec/application.log

# Token Configuration (Public Addresses)
UBEC_ISSUER=<Air token issuer>
UBECRC_ISSUER=<Water token issuer>
UBECGPI_ISSUER=<Earth token issuer>
UBECTT_ISSUER=<Fire token issuer>
```

### Step 4: Initialize Database

```bash
# Create database and user
sudo -u postgres psql << EOF
CREATE DATABASE ubec;
CREATE USER ubec_admin WITH ENCRYPTED PASSWORD '<secure-password>';
GRANT ALL PRIVILEGES ON DATABASE ubec TO ubec_admin;
\q
EOF

# Deploy schema
psql -U ubec_admin -d ubec -f database/schema/ubec_main_schema.sql
```

### Step 5: Verify Installation

```bash
# Activate virtual environment if not already active
source venv/bin/activate

# Check system health (this will initialize services)
python main.py health --detailed

# Expected output:
# âœ… System Status: HEALTHY
# âœ… 15/15 services operational
```

---

## Service Management

### Understanding the Service Registry

The Service Registry is the heart of the system architecture. It manages all services, handles initialization order, and provides health monitoring.

**Key Principles:**
- Services are initialized only when first requested (lazy loading)
- Dependencies are automatically resolved via topological sorting
- All services implement standardized health checks
- Services are properly shut down in reverse dependency order

### Service Lifecycle

```python
# Service lifecycle managed by context manager
async with registry:
    # Services auto-initialize on first access
    db = await registry.get('database')
    stellar = await registry.get('stellar_client')
    
    # Perform operations
    await db.execute("SELECT 1")
    
    # Services auto-cleanup on exit
```

### Registered Services

| Service Name | Purpose | Dependencies | Critical |
|--------------|---------|--------------|----------|
| `database` | PostgreSQL connection pool | None | âœ… Yes |
| `config` | Configuration management | database | âœ… Yes |
| `stellar_client` | Blockchain API client | config | âœ… Yes |
| `air` | Air element protocol | database, config | Yes |
| `water` | Water element protocol | database, config | Yes |
| `earth` | Earth element protocol | database, config | Yes |
| `fire` | Fire element protocol | database, config | Yes |
| `synchronizer` | Blockchain sync | database, stellar_client | âœ… Yes |
| `analytics` | Token analytics | database | No |
| `distribution` | Balance management | database | No |
| `distribution_evaluator` | Compliance checking | database | No |
| `holonic_evaluator` | Ubuntu assessment | database | No |
| `visualizer` | Reporting | database | No |
| `audit` | Audit logging | database | Yes |
| `monitoring` | System health | database | Yes |

### Starting the System

The system does NOT run as a daemon by default. All operations are executed via `main.py` commands:

```bash
# System health check
python main.py health --detailed

# Synchronize blockchain data
python main.py sync --full

# Run holonic evaluation
python main.py evaluate --accounts all

# Generate reports
python main.py report --type holonic --format html --output /var/reports/
```

### Creating a Systemd Service (Optional)

For continuous monitoring or scheduled operations, create a systemd service:

```bash
# Create service file
sudo nano /etc/systemd/system/ubec-monitor.service
```

**Service File Contents:**

```ini
[Unit]
Description=UBEC Protocol Monitoring Service
After=network.target postgresql.service

[Service]
Type=simple
User=ubec
Group=ubec
WorkingDirectory=/opt/ubec-protocol
Environment="PATH=/opt/ubec-protocol/venv/bin"
ExecStart=/opt/ubec-protocol/venv/bin/python main.py monitor --continuous
Restart=on-failure
RestartSec=10s
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable ubec-monitor.service
sudo systemctl start ubec-monitor.service

# Check status
sudo systemctl status ubec-monitor.service
```

---

## Monitoring and Health Checks

### Health Check Architecture

Every service implements a standardized health check pattern using the `ServiceHealthCheck` utility (Design Principle #12 - Method Singularity).

**Health Status Levels:**
- `HEALTHY` - Service operational, all checks passed
- `DEGRADED` - Service functional but experiencing issues
- `UNHEALTHY` - Service not operational
- `INITIALIZING` - Service starting up
- `UNKNOWN` - Health check unavailable

### Running Health Checks

```bash
# Quick health check
python main.py health

# Detailed health check with service metrics
python main.py health --detailed

# JSON output for monitoring systems
python main.py health --format json > /var/monitoring/ubec-health.json

# Check specific service
python main.py health --service database
```

**Example Detailed Output:**

```
â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
UBEC PROTOCOL SYSTEM HEALTH CHECK
â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
Timestamp: 2025-11-02T10:30:00Z
Overall Status: HEALTHY

Services: 15 total
  âœ… Healthy: 14
  âš ï¸  Degraded: 1
  âŒ Unhealthy: 0
  ðŸ”„ Initializing: 0

â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
SERVICE DETAILS
â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

âœ… database - HEALTHY
   â€¢ Pool: 15/20 connections active
   â€¢ Response Time: 2ms
   â€¢ Queries: 45,892 total, 0 errors
   
âœ… stellar_client - HEALTHY
   â€¢ Horizon API: Reachable (89ms)
   â€¢ Rate Limit: 2,145/3,000 remaining
   â€¢ Last Request: 5s ago
   
âš ï¸  synchronizer - DEGRADED
   â€¢ Status: Behind schedule
   â€¢ Last Sync: 15m ago (threshold: 10m)
   â€¢ Synced Accounts: 1,286/1,290
   â€¢ Recommended: Run sync operation

Performance:
  â€¢ Total Health Check Time: 1,245ms
  â€¢ Average Per Service: 83ms
  â€¢ Slowest Service: stellar_client (89ms)
```

### Monitoring Integration

**Prometheus Metrics (if implemented):**

```bash
# Expose metrics endpoint
python main.py metrics --port 9090

# Metrics available:
# - ubec_service_health{service="name",status="healthy|degraded|unhealthy"}
# - ubec_database_connections{pool="main"}
# - ubec_stellar_rate_limit_remaining
# - ubec_sync_lag_seconds
# - ubec_transaction_count_total
```

**Log Monitoring:**

```bash
# Application logs
tail -f /var/log/ubec/application.log

# Error logs only
tail -f /var/log/ubec/application.log | grep ERROR

# Service-specific logs
tail -f /var/log/ubec/application.log | grep "service=synchronizer"
```

### Alerting Thresholds

**Critical Alerts:**
- Database connection pool exhausted (>90% utilization)
- Stellar Horizon API unreachable (>5 minutes)
- Synchronization lag >1 hour
- Any service in UNHEALTHY status

**Warning Alerts:**
- Database response time >100ms
- Stellar rate limit <10% remaining
- Synchronization lag >15 minutes
- Any service in DEGRADED status

**Recommended Monitoring Checks:**

```bash
# Run every 5 minutes via cron
*/5 * * * * /opt/ubec-protocol/venv/bin/python /opt/ubec-protocol/main.py health --format json > /var/monitoring/health-$(date +\%Y\%m\%d-\%H\%M).json

# Alert on unhealthy status
*/5 * * * * /opt/ubec-protocol/scripts/check-health-alert.sh
```

---

## Operational Procedures

### Daily Operations

**Morning Health Check:**

```bash
# 1. Check system health
python main.py health --detailed

# 2. Review overnight logs
tail -n 100 /var/log/ubec/application.log

# 3. Check synchronization status
python main.py sync --status

# 4. Verify database connectivity
python main.py database --test-connection
```

**Data Synchronization:**

```bash
# Incremental sync (recommended for regular use)
python main.py sync --incremental

# Full sync (use after maintenance or extended downtime)
python main.py sync --full

# Sync specific accounts
python main.py sync --accounts GABC...,GDEF...

# Check sync status
python main.py sync --status
```

**Running Evaluations:**

```bash
# Run holonic evaluation for all accounts
python main.py evaluate --accounts all

# Evaluate specific accounts
python main.py evaluate --accounts GABC...,GDEF...

# Generate evaluation report
python main.py evaluate --accounts all --report --output /var/reports/
```

### Weekly Operations

**Database Maintenance:**

```bash
# Vacuum and analyze (Sunday 2 AM recommended)
python main.py database --vacuum --analyze

# Check database size
python main.py database --size-report

# Generate database statistics
python main.py database --statistics
```

**Report Generation:**

```bash
# Generate weekly holonic report
python main.py report --type holonic --period week --format html

# Generate distribution compliance report
python main.py report --type distribution --period week --format pdf

# Generate analytics summary
python main.py report --type analytics --period week --format json
```

### Monthly Operations

**Comprehensive Health Audit:**

```bash
# Full system diagnostic
python main.py diagnostic --comprehensive --output /var/audits/monthly/

# Database integrity check
python main.py database --integrity-check

# Service performance analysis
python main.py analyze --services --period month
```

**Backup Verification:**

```bash
# List recent backups
ls -lh /var/backups/ubec/

# Test backup restoration (use test database)
python main.py backup --test-restore --backup-file <latest-backup>
```

---

## Security Management

### Access Control

**Database Security:**

```sql
-- Create read-only role for monitoring
CREATE ROLE ubec_monitor WITH LOGIN PASSWORD '<secure-password>';
GRANT CONNECT ON DATABASE ubec TO ubec_monitor;
GRANT USAGE ON SCHEMA ubec_main TO ubec_monitor;
GRANT SELECT ON ALL TABLES IN SCHEMA ubec_main TO ubec_monitor;

-- Create read-write role for application
CREATE ROLE ubec_app WITH LOGIN PASSWORD '<secure-password>';
GRANT ALL PRIVILEGES ON DATABASE ubec TO ubec_app;
```

**File System Permissions:**

```bash
# Application directory
sudo chown -R ubec:ubec /opt/ubec-protocol
sudo chmod 750 /opt/ubec-protocol

# Configuration files
sudo chmod 600 /opt/ubec-protocol/.env

# Log directory
sudo mkdir -p /var/log/ubec
sudo chown ubec:ubec /var/log/ubec
sudo chmod 750 /var/log/ubec
```

**Network Security:**

```bash
# Firewall rules (UFW example)
sudo ufw allow from <monitoring-server-ip> to any port 9090 proto tcp
sudo ufw allow from <database-server-ip> to any port 5432 proto tcp
sudo ufw deny 5432
```

### Secret Management

**DO NOT:**
- Commit `.env` files to version control
- Store private keys in the application
- Log sensitive information

**DO:**
- Use environment variables for secrets
- Rotate credentials regularly (quarterly minimum)
- Implement least-privilege access
- Audit access logs monthly

### Security Monitoring

```bash
# Check for failed authentication attempts
grep "authentication failed" /var/log/ubec/application.log

# Monitor for unusual API activity
python main.py audit --suspicious-activity --period day

# Review database access logs
sudo tail -f /var/log/postgresql/postgresql-15-main.log | grep ubec
```

---

## Backup and Recovery

### Backup Strategy

**Backup Schedule:**
- **Hourly:** Transaction logs (incremental)
- **Daily:** Full database backup (4 AM)
- **Weekly:** Complete system backup (Sunday 1 AM)
- **Monthly:** Offsite archive backup

**Backup Locations:**
- **Primary:** `/var/backups/ubec/`
- **Secondary:** Network storage (NFS/SMB)
- **Archive:** Offsite/cloud storage

### Database Backup

**Automated Backup Script:**

```bash
#!/bin/bash
# /opt/ubec-protocol/scripts/backup-database.sh

BACKUP_DIR=/var/backups/ubec
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
DB_NAME=ubec
DB_USER=ubec_admin

# Create backup directory
mkdir -p $BACKUP_DIR

# Perform backup
pg_dump -U $DB_USER -F c -b -v -f $BACKUP_DIR/ubec-${TIMESTAMP}.dump $DB_NAME

# Compress backup
gzip $BACKUP_DIR/ubec-${TIMESTAMP}.dump

# Remove backups older than 30 days
find $BACKUP_DIR -name "ubec-*.dump.gz" -mtime +30 -delete

# Log completion
echo "$(date): Backup completed: ubec-${TIMESTAMP}.dump.gz" >> /var/log/ubec/backup.log
```

**Schedule via Cron:**

```bash
# Edit crontab
crontab -e

# Add daily backup at 4 AM
0 4 * * * /opt/ubec-protocol/scripts/backup-database.sh
```

### Recovery Procedures

**Database Recovery:**

```bash
# Stop application
sudo systemctl stop ubec-monitor.service

# Restore database
gunzip /var/backups/ubec/ubec-<timestamp>.dump.gz
pg_restore -U ubec_admin -d ubec -c /var/backups/ubec/ubec-<timestamp>.dump

# Verify restoration
psql -U ubec_admin -d ubec -c "SELECT COUNT(*) FROM ubec_main.stellar_accounts;"

# Start application
sudo systemctl start ubec-monitor.service

# Verify system health
python main.py health --detailed
```

**Configuration Recovery:**

```bash
# Restore configuration from backup
cp /var/backups/ubec/config/.env.backup /opt/ubec-protocol/.env

# Verify configuration
python main.py config --validate
```

### Disaster Recovery

**Recovery Time Objective (RTO):** 4 hours  
**Recovery Point Objective (RPO):** 1 hour

**Disaster Recovery Steps:**

1. **Assess Damage:** Determine scope of failure
2. **Notify Stakeholders:** Alert technical team and management
3. **Deploy New Instance:** Provision new server if necessary
4. **Restore Database:** Use most recent backup
5. **Restore Configuration:** Deploy `.env` and system files
6. **Synchronize Data:** Run full blockchain sync
7. **Verify Operations:** Execute comprehensive health checks
8. **Resume Normal Operations:** Switch DNS/load balancer if applicable

---

## Troubleshooting

### Common Issues and Solutions

#### Issue 1: Database Connection Failures

**Symptoms:**
```
ERROR - database - Failed to connect: connection refused
```

**Diagnosis:**
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Test connection manually
psql -U ubec_admin -d ubec -h localhost -c "SELECT 1;"

# Check connection pool
python main.py database --pool-status
```

**Resolution:**
```bash
# Restart PostgreSQL
sudo systemctl restart postgresql

# Check firewall
sudo ufw status

# Verify credentials in .env
cat /opt/ubec-protocol/.env | grep DB_
```

#### Issue 2: Stellar Horizon API Rate Limiting

**Symptoms:**
```
WARNING - stellar_client - Rate limit exceeded: 3000/3000
```

**Diagnosis:**
```bash
# Check current rate limit status
python main.py stellar --rate-limit-status

# Review recent API usage
grep "rate_limit" /var/log/ubec/application.log | tail -20
```

**Resolution:**
```bash
# Wait for rate limit window to reset (logs show reset time)
# Increase rate limit window in .env:
STELLAR_RATE_LIMIT_WINDOW=7200  # 2 hours instead of 1

# Implement exponential backoff (already built-in)
# Reduce synchronization frequency
```

#### Issue 3: Synchronization Lag

**Symptoms:**
```
WARNING - synchronizer - Sync lag: 45 minutes behind blockchain
```

**Diagnosis:**
```bash
# Check sync status
python main.py sync --status

# Review synchronizer logs
grep "synchronizer" /var/log/ubec/application.log | tail -50

# Check Stellar Horizon status
curl https://horizon.stellar.org/
```

**Resolution:**
```bash
# Run incremental sync
python main.py sync --incremental --force

# If persistent, run full sync (during off-peak hours)
python main.py sync --full

# Check system resources
htop
df -h
```

#### Issue 4: Service Health Degraded

**Symptoms:**
```
âš ï¸  synchronizer - DEGRADED - Last sync: 25 minutes ago
```

**Diagnosis:**
```bash
# Check service-specific health
python main.py health --service synchronizer --detailed

# Review service logs
tail -f /var/log/ubec/application.log | grep synchronizer

# Check dependencies
python main.py health --service database
python main.py health --service stellar_client
```

**Resolution:**
```bash
# Restart application (if using systemd service)
sudo systemctl restart ubec-monitor.service

# Manual sync operation
python main.py sync --incremental

# Check for configuration issues
python main.py config --validate
```

### Log Analysis

**Key Log Locations:**
- Application: `/var/log/ubec/application.log`
- Database: `/var/log/postgresql/postgresql-15-main.log`
- System: `/var/log/syslog`

**Useful Log Commands:**

```bash
# Find errors in last hour
grep ERROR /var/log/ubec/application.log | grep "$(date +%Y-%m-%d\ %H):"

# Count errors by type
grep ERROR /var/log/ubec/application.log | awk '{print $5}' | sort | uniq -c

# Watch logs in real-time
tail -f /var/log/ubec/application.log

# Filter by service
tail -f /var/log/ubec/application.log | grep "service=database"

# Extract warnings and errors
grep -E "WARNING|ERROR" /var/log/ubec/application.log | tail -50
```

### Performance Issues

**Diagnosis:**

```bash
# Check system resources
top
htop
iotop

# Database performance
python main.py database --performance-report

# Check slow queries
python main.py database --slow-queries

# Network latency to Stellar Horizon
ping -c 10 horizon.stellar.org
curl -w "@curl-format.txt" -o /dev/null -s https://horizon.stellar.org/
```

**Optimization:**

```bash
# Increase database connection pool
# Edit .env:
DB_POOL_MAX=30  # Increase from 20

# Optimize database
python main.py database --vacuum --analyze

# Review indexes
python main.py database --index-usage
```

---

## Common Administrative Tasks

### Adding New Accounts to Monitor

```bash
# Add accounts to monitoring list
python main.py accounts --add GABC...,GDEF...

# Verify accounts added
python main.py accounts --list

# Sync new accounts
python main.py sync --accounts GABC...,GDEF...

# Run initial evaluation
python main.py evaluate --accounts GABC...,GDEF...
```

### Updating Configuration

```bash
# Backup current configuration
cp .env .env.backup.$(date +%Y%m%d)

# Edit configuration
nano .env

# Validate new configuration
python main.py config --validate

# Reload configuration (restart service)
sudo systemctl restart ubec-monitor.service

# Verify changes
python main.py config --show
```

### Log Rotation

```bash
# Create logrotate configuration
sudo nano /etc/logrotate.d/ubec
```

**Logrotate Configuration:**

```
/var/log/ubec/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 0640 ubec ubec
    sharedscripts
    postrotate
        systemctl reload ubec-monitor.service > /dev/null 2>&1 || true
    endscript
}
```

### Generating Reports

```bash
# Daily operational report
python main.py report --type daily --date today --format html --output /var/reports/daily/

# Token distribution report
python main.py report --type distribution --format pdf --output /var/reports/

# Network health report
python main.py report --type health --period week --format json --output /var/reports/health/

# Custom holonic evaluation report
python main.py report --type holonic --accounts all --format html --output /var/reports/holonic/
```

### User Access Management

```bash
# Create monitoring user (read-only database access)
python main.py users --create-monitor-user

# Create application user (read-write access)
python main.py users --create-app-user

# List current users
python main.py users --list

# Revoke access
python main.py users --revoke <username>

# Rotate credentials
python main.py users --rotate-password <username>
```

---

## Appendix A: Command Reference

### Health Commands

```bash
python main.py health [--detailed] [--service SERVICE] [--format FORMAT]
```

### Sync Commands

```bash
python main.py sync [--full|--incremental] [--accounts ACCOUNTS] [--status]
```

### Evaluation Commands

```bash
python main.py evaluate --accounts ACCOUNTS [--report] [--output DIR]
```

### Database Commands

```bash
python main.py database [--vacuum] [--analyze] [--size-report] [--test-connection]
```

### Report Commands

```bash
python main.py report --type TYPE [--period PERIOD] [--format FORMAT] [--output DIR]
```

---

## Appendix B: Emergency Contacts

**Technical Escalation:**
- Primary Administrator: [contact info]
- Database Administrator: [contact info]
- Network Administrator: [contact info]

**Vendor Support:**
- Stellar Network Status: https://status.stellar.org/
- PostgreSQL Support: [contact info]

**Documentation:**
- Internal Wiki: [URL]
- Project Repository: [URL]
- Runbook: [URL]

---

## Appendix C: Maintenance Windows

**Recommended Maintenance Schedule:**
- **Daily:** 2:00 AM - 4:00 AM UTC (low traffic period)
- **Weekly:** Sunday 1:00 AM - 5:00 AM UTC
- **Monthly:** First Sunday of month, 12:00 AM - 6:00 AM UTC

**Maintenance Procedures:**
- Notify stakeholders 48 hours in advance
- Execute database vacuum/analyze
- Apply system updates
- Rotate logs
- Verify backups
- Run comprehensive diagnostics

---

## Appendix D: Service Level Objectives (SLOs)

| Metric | Target | Critical Threshold |
|--------|--------|-------------------|
| System Availability | 99.5% | 99.0% |
| Database Response Time | <50ms (p95) | <100ms (p95) |
| API Success Rate | 99.9% | 99.5% |
| Sync Lag | <10 minutes | <30 minutes |
| Health Check Success | 100% | 98% |

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-11-02 | UBEC DevOps | Initial release |

---

**End of System Administrator Onboarding Guide**
