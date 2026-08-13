# UBEC Backend API Service

**Version:** 2.1.2  
**Status:** Production Ready  
**Last Updated:** November 9, 2025

## Attribution

This project uses the services of Claude and Anthropic PBC to inform our decisions and recommendations. This project was made possible with the assistance of Claude and Anthropic PBC.

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [API Endpoints](#api-endpoints)
- [Rate Limiting](#rate-limiting)
- [Development](#development)
- [Testing](#testing)
- [Deployment](#deployment)
- [Monitoring](#monitoring)
- [Troubleshooting](#troubleshooting)
- [Design Principles](#design-principles)

---

## Overview

The UBEC Backend API Service provides a RESTful API for accessing real-time UBEC Protocol data. Built with FastAPI, it exposes blockchain data, token metrics, holonic evaluations, and bioregional information for consumption by frontend applications and external services.

### Key Features

- **Real-time Data**: Live blockchain synchronization with Stellar network
- **IP-Based Rate Limiting**: Prevents abuse without requiring authentication
- **Holonic Evaluation**: Ubuntu principle-based account assessments
- **Geographic Data**: Ecoregions and watersheds from phenomenal schema
- **Bioregional Integration**: Community organization tracking
- **CORS Configured**: Ready for multi-domain deployment
- **Health Monitoring**: Comprehensive service health checks
- **Auto-Documentation**: Swagger UI and ReDoc included
- **16 Operational Endpoints**: Complete API coverage across all data types
- **17 Total Routes**: Including automatic documentation routes (/docs, /redoc, /openapi.json)

### Purpose

This API serves as the data layer for:
- Public website (www.ubec.network)
- Bioregional dashboard (bioregional.ubec.network)
- Analytics and reporting tools
- Third-party integrations
- Mobile applications

---

## Architecture

### Technology Stack

- **Framework**: FastAPI 0.104+
- **Python**: 3.11+
- **Database**: PostgreSQL 15.13+ with asyncpg driver
- **Rate Limiting**: SlowAPI (in-memory storage)
- **Web Server**: Uvicorn (ASGI server)
- **Architecture**: Service-oriented with dependency injection

### System Components

```
┌─────────────────────────────────────────────────────────┐
│                   UBEC Backend API                      │
│                    (FastAPI App)                        │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐  │
│  │   Health     │  │    Token     │  │   Network   │  │
│  │  Endpoints   │  │  Endpoints   │  │  Endpoints  │  │
│  └──────────────┘  └──────────────┘  └─────────────┘  │
│                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐  │
│  │   Holonic    │  │ Transaction  │  │ Bioregion   │  │
│  │  Endpoints   │  │  Endpoints   │  │  Endpoints  │  │
│  └──────────────┘  └──────────────┘  └─────────────┘  │
│                                                         │
├─────────────────────────────────────────────────────────┤
│            Rate Limiter (IP-based)                      │
│         100/min | 1000/hour per IP                      │
├─────────────────────────────────────────────────────────┤
│           CORS Middleware                               │
│    (Configured for UBEC domains)                        │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│              Service Registry                           │
│    (Dependency Management & Health Monitoring)          │
└─────────────────────────────────────────────────────────┘
                          │
          ┌───────────────┼───────────────┐
          ▼               ▼               ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   Database   │  │  Bioregion   │  │    Config    │
│   Manager    │  │   Manager    │  │   Service    │
└──────────────┘  └──────────────┘  └──────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────┐
│           PostgreSQL Database                           │
│    ubec_main | phenomenal | topology | public           │
│         87,567+ records | 68 tables                      │
└─────────────────────────────────────────────────────────┘
```

### Service Integration

The API service integrates with:

1. **Database Manager**: Async connection pool for PostgreSQL
2. **Bioregion Manager**: Geographic and community data
3. **Configuration Service**: Database-backed settings
4. **Service Registry**: Dependency injection and lifecycle management

---

## Prerequisites

### System Requirements

- **Operating System**: Linux (Ubuntu 24.04 LTS recommended), macOS, or Windows
- **Python**: 3.11 or higher
- **PostgreSQL**: 15.13 or higher
- **Memory**: 4GB RAM minimum, 8GB recommended
- **Network**: Internet connectivity for Stellar Horizon API

### Required Software

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install python3.11 python3.11-venv postgresql-15

# macOS (via Homebrew)
brew install python@3.11 postgresql@15

# Verify installations
python3.11 --version  # Should show 3.11.x
psql --version        # Should show 15.13+
```

### Dependencies

```
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
slowapi>=0.1.9
asyncpg>=0.28.0
stellar-sdk>=9.0.0
python-dotenv>=1.0.0
```

---

## Installation

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/ubec-protocol.git
cd ubec-protocol
```

### 2. Create Virtual Environment

```bash
python3.11 -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate     # Windows
```

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure Database

#### Create Database and User

```bash
# Access PostgreSQL as superuser
sudo -u postgres psql

# Create user and database
CREATE USER ubec_app WITH PASSWORD 'your_secure_password';
CREATE DATABASE ubec OWNER ubec_app;
GRANT ALL PRIVILEGES ON DATABASE ubec TO ubec_app;

# Enable PostGIS extension
\c ubec
CREATE EXTENSION IF NOT EXISTS postgis;

# Exit
\q
```

#### Initialize Schema

```bash
# Deploy main schema
psql -U ubec_app -d ubec -f database/schema/ubec_main_schema.sql

# Verify schema
psql -U ubec_app -d ubec -c "\dt ubec_main.*"
```

### 5. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit configuration
nano .env
```

**Required Environment Variables:**

```bash
# Database Configuration
UBEC_DB_HOST=localhost
UBEC_DB_PORT=5432
UBEC_DB_NAME=ubec
UBEC_DB_USER=ubec_app
UBEC_DB_PASSWORD=your_secure_password
UBEC_DB_SCHEMA=ubec_main
DB_SEARCH_PATH=ubec_main,phenomenal,topology,public

# Database Connection Pool
DB_MIN_POOL=2
DB_MAX_POOL=10
DB_POOL_TIMEOUT=30
DB_COMMAND_TIMEOUT=60

# Stellar Network
STELLAR_NETWORK=PUBLIC
STELLAR_HORIZON_URL=https://horizon.stellar.org

# Token Issuers (Mainnet Addresses)
UBEC_ISSUER=GDPNB7S3IOM2J6C3NA2QG4TQAUCRZXPJJ4HSCCSIKELEH7ORUCX5UB2VN
UBECRC_ISSUER=GBYOTGM27KLFNQQU3G6QWVEK7LQB36N6OX2YLYMN4WU3AFM4VRFZUBEC
UBECGPI_ISSUER=GCPU3LUGRIYLWMPOQEEGIL2HI5Z637PQVK42Z5PYRRQMPFDTNT5SUBEC
UBECTT_ISSUER=GBWYGECRQ7R5E6QQKWBTVNYSCFVTIYZLF6MGDHJQBHP2KU2U65Z5UBEC

# Application Configuration
LOG_LEVEL=INFO
LOG_FILE=logs/ubec.log
```

### 6. Verify Installation

```bash
# Check system health
python main.py health

# Expected output:
# ✅ System Status: HEALTHY
# ✅ 15/15 services operational
```

---

## Configuration

### Environment Variables Reference

#### Database Configuration

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `UBEC_DB_HOST` | Yes | localhost | PostgreSQL host address |
| `UBEC_DB_PORT` | Yes | 5432 | PostgreSQL port |
| `UBEC_DB_NAME` | Yes | ubec | Database name |
| `UBEC_DB_USER` | Yes | - | Database user |
| `UBEC_DB_PASSWORD` | Yes | - | Database password |
| `UBEC_DB_SCHEMA` | Yes | ubec_main | Primary schema |
| `DB_SEARCH_PATH` | Yes | ubec_main,public | Schema search path |
| `DB_MIN_POOL` | No | 2 | Minimum pool size |
| `DB_MAX_POOL` | No | 10 | Maximum pool size |
| `DB_POOL_TIMEOUT` | No | 30 | Connection timeout (seconds) |
| `DB_COMMAND_TIMEOUT` | No | 60 | Query timeout (seconds) |

#### Stellar Network Configuration

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `STELLAR_NETWORK` | Yes | PUBLIC | Network: PUBLIC or TESTNET |
| `STELLAR_HORIZON_URL` | Yes | https://horizon.stellar.org | Horizon API URL |
| `STELLAR_RATE_LIMIT` | No | 3000 | API calls per hour |
| `STELLAR_RATE_LIMIT_WINDOW` | No | 3600 | Rate limit window (seconds) |

#### Token Configuration

| Variable | Required | Description |
|----------|----------|-------------|
| `UBEC_ISSUER` | Yes | Air token issuer address |
| `UBECRC_ISSUER` | Yes | Water token issuer address |
| `UBECGPI_ISSUER` | Yes | Earth token issuer address |
| `UBECTT_ISSUER` | Yes | Fire token issuer address |

#### Application Configuration

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `LOG_LEVEL` | No | INFO | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `LOG_FILE` | No | logs/ubec.log | Log file path |

### CORS Configuration

CORS is pre-configured for UBEC domains. To modify, edit `services/api/api_service.py`:

```python
allow_origins=[
    "https://www.ubec.network",
    "https://bioregional.ubec.network",
    "http://localhost:3000",  # Development
]
```

## API Discovery

Users can discover available API endpoints through multiple methods:

### Interactive Documentation

**Swagger UI**: `http://localhost:8000/api/docs`
- Interactive interface to test endpoints in browser
- View all parameters and request/response schemas
- Execute live API calls

**ReDoc**: `http://localhost:8000/api/redoc`
- Clean, readable documentation
- Organized by endpoint categories
- Detailed request/response examples

### Health Check

```bash
curl http://localhost:8000/health
```

**Response:**
```json
{
  "service": "BackendAPIService",
  "version": "2.1.2",
  "status": "healthy",
  "initialized": true,
  "endpoints_count": 17,
  "rate_limiting": "active",
  "rate_limit_config": {
    "default": "100/minute, 1000/hour",
    "scope": "per IP address",
    "storage": "in-memory"
  },
  "dependencies": {
    "database": "healthy",
    "bioregion_manager": "healthy"
  },
  "timestamp": "2025-11-09T15:00:00Z"
}
```

**Note**: `endpoints_count: 17` includes:
- 16 operational API endpoints
- 1 additional FastAPI route (e.g., root redirect)

### Programmatic Discovery

```bash
# Get OpenAPI specification (JSON)
curl http://localhost:8000/openapi.json

# Returns full API schema with all endpoints, parameters, and responses
```

### Endpoint Organization

Endpoints are organized by tags in the documentation:

| Tag | Endpoints | Description |
|-----|-----------|-------------|
| **default** | 2 | Health checks (/health, /api/v1/health) |
| **tokens** | 1 | Token information and metrics |
| **network** | 1 | Network status and health |
| **distribution** | 1 | Distribution statistics |
| **holonic** | 1 | Ubuntu principle evaluations |
| **transactions** | 1 | Recent blockchain operations |
| **bioregions** | 5 | Bioregion data (count, summary, list, detail, health) |
| **ecoregions** | 2 | Ecoregion geographic data |
| **watersheds** | 2 | Watershed data from FEOW |

**Total: 16 operational endpoints**

---

## API Endpoints

### Base URL

**Production**: `https://api.ubec.network`  
**Development**: `http://localhost:8000`

### Documentation

- **Swagger UI**: `http://localhost:8000/api/docs`
- **ReDoc**: `http://localhost:8000/api/redoc`

### Endpoint Categories

#### 1. Health Check Endpoints

##### GET /health

Health check for monitoring and load balancers.

**Rate Limit**: 300 requests/minute

**Response:**
```json
{
  "service": "BackendAPIService",
  "version": "2.1.2",
  "status": "healthy",
  "initialized": true,
  "endpoints_count": 15,
  "rate_limiting": "active",
  "rate_limit_config": {
    "default": "100/minute, 1000/hour",
    "scope": "per IP address",
    "storage": "in-memory"
  },
  "dependencies": {
    "database": "healthy",
    "bioregion_manager": "healthy"
  },
  "timestamp": "2025-11-09T10:30:00Z"
}
```

##### GET /api/v1/health

Alternative health check under /api/v1 path.

**Rate Limit**: 300 requests/minute

**Response**: Same as `/health`

---

#### 2. Token Information Endpoints

##### GET /api/v1/tokens

Get comprehensive token information for all four UBEC tokens.

**Rate Limit**: 100 requests/minute

**Response:**
```json
{
  "tokens": [
    {
      "code": "UBEC",
      "issuer": "GDPNB7S3...",
      "element": "air",
      "ubuntu_principle": "diversity",
      "description": "Gateway Token - Universal Access",
      "total_supply": 1000000.00,
      "holders": 651,
      "active_accounts": 325,
      "median_balance": 500.00
    },
    {
      "code": "UBECrc",
      "issuer": "GBYOTGM2...",
      "element": "water",
      "ubuntu_principle": "reciprocity",
      "description": "Reciprocity Credits - Flow and Exchange",
      "total_supply": 750000.00,
      "holders": 487,
      "active_accounts": 243,
      "median_balance": 350.00
    },
    {
      "code": "UBECgpi",
      "issuer": "GCPU3LUG...",
      "element": "earth",
      "ubuntu_principle": "mutualism",
      "description": "Stability Token - Value Storage",
      "total_supply": 500000.00,
      "holders": 312,
      "active_accounts": 156,
      "median_balance": 800.00
    },
    {
      "code": "UBECtt",
      "issuer": "GBWYGECC...",
      "element": "fire",
      "ubuntu_principle": "regeneration",
      "description": "Transform Token - Community Sovereignty",
      "total_supply": 250000.00,
      "holders": 178,
      "active_accounts": 89,
      "median_balance": 1200.00
    }
  ],
  "timestamp": "2025-11-09T10:30:00Z"
}
```

---

#### 3. Network Status Endpoints

##### GET /api/v1/network-status

Get real-time network health and metrics.

**Rate Limit**: 100 requests/minute

**Response:**
```json
{
  "network_health": {
    "overall_health": 0.78,
    "active_account_rate": 0.45,
    "transaction_volume_24h": 1247,
    "unique_participants_24h": 342,
    "network_growth_rate": 0.12,
    "bioregion_count": 8
  },
  "element_metrics": {
    "air": {
      "holders": 651,
      "active_rate": 0.50,
      "volume_24h": 412
    },
    "water": {
      "holders": 487,
      "active_rate": 0.48,
      "volume_24h": 356
    },
    "earth": {
      "holders": 312,
      "active_rate": 0.42,
      "volume_24h": 289
    },
    "fire": {
      "holders": 178,
      "active_rate": 0.38,
      "volume_24h": 190
    }
  },
  "ubuntu_alignment": {
    "diversity_score": 0.82,
    "reciprocity_score": 0.75,
    "mutualism_score": 0.71,
    "regeneration_score": 0.69
  },
  "timestamp": "2025-11-09T10:30:00Z"
}
```

---

#### 4. Distribution Statistics Endpoints

##### GET /api/v1/distribution

Get token distribution statistics and compliance metrics.

**Rate Limit**: 100 requests/minute

**Response:**
```json
{
  "distributions": [
    {
      "token": "UBEC",
      "element": "air",
      "total_supply": 1000000.00,
      "circulating_supply": 850000.00,
      "allocation_model": {
        "beneficiaries": 0.65,
        "liquidity": 0.30,
        "operations": 0.05
      },
      "current_distribution": {
        "beneficiaries": 0.63,
        "liquidity": 0.32,
        "operations": 0.05
      },
      "compliance_score": 0.95,
      "gini_coefficient": 0.42
    }
  ],
  "compliance_status": "compliant",
  "timestamp": "2025-11-09T10:30:00Z"
}
```

---

#### 5. Holonic Evaluation Endpoints

##### GET /api/v1/holonic-scores

Get holonic evaluation scores for accounts (Ubuntu principle assessments).

**Rate Limit**: 100 requests/minute

**Query Parameters:**
- `category` (optional): Filter by holonic category (observer, contributor, activator, integrator, exemplar)
- `limit` (optional, default=50): Maximum number of results
- `min_score` (optional, default=0.0): Minimum holonic score threshold

**Response:**
```json
{
  "accounts": [
    {
      "account_id": "GABC123...",
      "holonic_category": "activator",
      "holonic_score": 0.82,
      "dimension_scores": {
        "autonomy": 0.85,
        "multi_scale": 0.78,
        "regenerative": 0.81,
        "network_contribution": 0.84,
        "ubuntu_alignment": 0.83
      },
      "metrics": {
        "transaction_count": 145,
        "unique_partners": 28,
        "balance": 1250.00,
        "account_age_days": 287,
        "reciprocity_score": 0.76
      },
      "evaluated_at": "2025-11-09T08:15:00Z"
    }
  ],
  "summary": {
    "total_evaluated": 1286,
    "category_distribution": {
      "observer": 342,
      "contributor": 458,
      "activator": 312,
      "integrator": 134,
      "exemplar": 40
    },
    "average_score": 0.64,
    "median_score": 0.62
  },
  "timestamp": "2025-11-09T10:30:00Z"
}
```

**Holonic Categories:**
- **Observer** (0.0-0.4): New participants, learning the system
- **Contributor** (0.4-0.6): Regular participants with basic engagement
- **Activator** (0.6-0.8): Active community members driving local change
- **Integrator** (0.8-0.95): System leaders connecting multiple initiatives
- **Exemplar** (0.95-1.0): Network elders embodying Ubuntu principles

---

#### 6. Transaction Endpoints

##### GET /api/v1/transactions

Get recent UBEC protocol transactions.

**Rate Limit**: 60 requests/minute (lower due to query complexity)

**Query Parameters:**
- `limit` (optional, default=25, max=100): Number of transactions to return

**Response:**
```json
{
  "transactions": [
    {
      "operation_id": 123456789,
      "hash": "abc123...",
      "ledger": 45678901,
      "asset_code": "UBEC",
      "element": "air",
      "ubuntu_principle": "diversity",
      "operation_type": "payment",
      "from_account": "GABC123...",
      "to_account": "GDEF456...",
      "source_account": "GABC123...",
      "amount": 50.00,
      "timestamp": "2025-11-09T10:28:45Z"
    }
  ],
  "count": 25,
  "timestamp": "2025-11-09T10:30:00Z"
}
```

---

#### 7. Bioregion Endpoints

##### GET /api/v1/bioregions/count

Get total count of active bioregions.

**Rate Limit**: 100 requests/minute

**Response:**
```json
{
  "count": 8,
  "timestamp": "2025-11-09T10:30:00Z"
}
```

##### GET /api/v1/bioregions/summary

Get summary statistics for all bioregions.

**Rate Limit**: 100 requests/minute

**Response:**
```json
{
  "total_bioregions": 8,
  "total_accounts": 1286,
  "total_transactions": 74495,
  "average_health": 0.78,
  "timestamp": "2025-11-09T10:30:00Z"
}
```

##### GET /api/v1/bioregions/count

Get total count of active bioregions.

**Rate Limit**: 100 requests/minute

**Response:**
```json
{
  "count": 8,
  "timestamp": "2025-11-09T10:30:00Z"
}
```

##### GET /api/v1/bioregions/summary

Get summary statistics for all bioregions.

**Rate Limit**: 100 requests/minute

**Response:**
```json
{
  "total_bioregions": 8,
  "total_accounts": 1286,
  "total_transactions": 74495,
  "average_health": 0.78,
  "average_autonomy_score": 0.72,
  "average_integration_score": 0.81,
  "timestamp": "2025-11-09T10:30:00Z"
}
```

##### GET /api/v1/bioregions

Get list of all bioregions with detailed information.

**Rate Limit**: 100 requests/minute

**Query Parameters:**
- `limit` (optional, default=50, max=100): Maximum results
- `offset` (optional, default=0): Pagination offset
- `status` (optional): Filter by status ('active', 'forming', 'dissolved')
- `include_dissolved` (optional, default=false): Include dissolved bioregions
- `min_members` (optional, default=1): Minimum member count

**Response:**
```json
{
  "bioregions": [
    {
      "bioregion_id": 1,
      "name": "Pacific Northwest Bioregion",
      "account_count": 187,
      "transaction_count": 9234,
      "health_score": 0.82,
      "autonomy_score": 0.75,
      "integration_score": 0.88,
      "status": "active",
      "created_at": "2024-06-15T00:00:00Z"
    }
  ],
  "count": 8,
  "total": 8,
  "limit": 50,
  "offset": 0,
  "timestamp": "2025-11-09T10:30:00Z"
}
```

##### GET /api/v1/bioregions/{bioregion_id}

Get detailed information for a specific bioregion.

**Rate Limit**: 100 requests/minute

**Path Parameters:**
- `bioregion_id`: Integer ID of the bioregion

**Response:**
```json
{
  "bioregion_id": 1,
  "name": "Pacific Northwest Bioregion",
  "description": "Spanning from Northern California to British Columbia",
  "account_count": 187,
  "transaction_count": 9234,
  "active_accounts": 94,
  "health_score": 0.82,
  "token_distribution": {
    "UBEC": 23450.00,
    "UBECrc": 17230.00,
    "UBECgpi": 12800.00,
    "UBECtt": 8750.00
  },
  "ubuntu_scores": {
    "diversity": 0.85,
    "reciprocity": 0.78,
    "mutualism": 0.81,
    "regeneration": 0.79
  },
  "created_at": "2024-06-15T00:00:00Z",
  "updated_at": "2025-11-09T08:00:00Z",
  "timestamp": "2025-11-09T10:30:00Z"
}
```

##### GET /api/v1/bioregions/{bioregion_id}/health

Get health metrics for a specific bioregion.

**Rate Limit**: 100 requests/minute

**Path Parameters:**
- `bioregion_id`: Integer ID of the bioregion

**Response:**
```json
{
  "bioregion_id": 1,
  "health_score": 0.82,
  "metrics": {
    "activity_rate": 0.50,
    "transaction_velocity": 0.78,
    "network_connectivity": 0.85,
    "ubuntu_alignment": 0.83,
    "growth_rate": 0.12
  },
  "status": "healthy",
  "recommendations": [
    "Maintain current transaction patterns",
    "Continue fostering network connections",
    "Monitor growth sustainability"
  ],
  "timestamp": "2025-11-09T10:30:00Z"
}
```

##### GET /api/v1/bioregions/{bioregion_id}/health

Get health assessment for a specific bioregion.

**Rate Limit**: 100 requests/minute

**Path Parameters:**
- `bioregion_id`: Integer ID of the bioregion

**Response:**
```json
{
  "bioregion_id": 1,
  "bioregion_name": "Pacific Northwest Bioregion",
  "health_rating": "excellent",
  "autonomy_score": 0.75,
  "integration_score": 0.88,
  "member_count": 187,
  "status": "active",
  "timestamp": "2025-11-09T10:30:00Z"
}
```

**Health Ratings:**
- `excellent`: Composite score ≥ 0.8
- `good`: Composite score ≥ 0.6
- `fair`: Composite score ≥ 0.4
- `poor`: Composite score < 0.4

**Errors:**
- `404 Not Found`: Bioregion with specified ID doesn't exist

---

#### 8. Ecoregion Endpoints (Phenomenal Schema)

These endpoints provide access to the Ecoregions2017 dataset for geographic and ecological bioregion data.

##### GET /api/v1/ecoregions

Get ecoregion data with filtering options.

**Rate Limit**: 100 requests/minute

**Query Parameters:**
- `limit` (optional, default=50, max=200): Number of results to return
- `biome` (optional): Filter by biome name (partial match, case-insensitive)
- `realm` (optional): Filter by realm (partial match, case-insensitive)

**Response:**
```json
{
  "count": 50,
  "summary": {
    "total_ecoregions": 847,
    "total_biomes": 14,
    "total_realms": 8
  },
  "ecoregions": [
    {
      "id": 1,
      "objectid": 12345,
      "eco_name": "Pacific Northwest Temperate Rainforest",
      "eco_id": 123,
      "biome_num": 1,
      "biome_name": "Temperate Broadleaf & Mixed Forests",
      "realm": "Nearctic",
      "eco_biome_": "NA0513",
      "nnh": 1,
      "nnh_name": "Nature Could Reach Half Protected",
      "shape_leng": 45.678,
      "shape_area": 123.456,
      "color": "#2E8B57",
      "color_bio": "#228B22",
      "color_nnh": "#32CD32"
    }
  ],
  "filters": {
    "biome": "forest",
    "realm": null,
    "limit": 50
  },
  "timestamp": "2025-11-09T10:30:00Z"
}
```

##### GET /api/v1/ecoregions/{eco_id}

Get detailed information about a specific ecoregion by ID.

**Rate Limit**: 100 requests/minute

**Path Parameters:**
- `eco_id`: Ecoregion ID (integer)

**Response:**
```json
{
  "id": 1,
  "objectid": 12345,
  "eco_name": "Pacific Northwest Temperate Rainforest",
  "eco_id": 123,
  "biome_num": 1,
  "biome_name": "Temperate Broadleaf & Mixed Forests",
  "realm": "Nearctic",
  "eco_biome_": "NA0513",
  "nnh": 1,
  "nnh_name": "Nature Could Reach Half Protected",
  "shape_leng": 45.678,
  "shape_area": 123.456,
  "color": "#2E8B57",
  "color_bio": "#228B22",
  "color_nnh": "#32CD32",
  "license": "CC BY 4.0"
}
```

**Errors:**
- `404 Not Found`: Ecoregion with specified eco_id doesn't exist

---

#### 9. Watershed Endpoints (Phenomenal Schema)

These endpoints provide access to the FEOW (Freshwater Ecoregions of the World) HydroSHEDS dataset.

##### GET /api/v1/watersheds

Get watershed data with optional area filtering.

**Rate Limit**: 100 requests/minute

**Query Parameters:**
- `limit` (optional, default=50, max=200): Number of results to return
- `min_area` (optional): Minimum watershed area in square kilometers

**Response:**
```json
{
  "count": 50,
  "summary": {
    "total_watersheds": 426,
    "total_area_km2": 148940000.0,
    "avg_area_km2": 349624.82,
    "max_area_km2": 7050000.0
  },
  "watersheds": [
    {
      "id": 1,
      "feow_id": 101,
      "area_skm": 7050000.0
    },
    {
      "id": 2,
      "feow_id": 102,
      "area_skm": 3200000.0
    }
  ],
  "filters": {
    "min_area": 1000000.0,
    "limit": 50
  },
  "timestamp": "2025-11-09T10:30:00Z"
}
```

**Note**: Results are ordered by area descending (largest watersheds first).

##### GET /api/v1/watersheds/{feow_id}

Get specific watershed by FEOW ID.

**Rate Limit**: 100 requests/minute

**Path Parameters:**
- `feow_id`: FEOW watershed ID (integer)

**Response:**
```json
{
  "id": 1,
  "feow_id": 101,
  "area_skm": 7050000.0
}
```

**Errors:**
- `404 Not Found`: Watershed with specified feow_id doesn't exist

---

## Rate Limiting

### Overview

The API implements IP-based rate limiting using SlowAPI. No authentication or API keys are required - rate limits prevent abuse while maintaining open access.

### Default Limits

- **Default**: 100 requests/minute, 1000 requests/hour per IP
- **Health Endpoints**: 300 requests/minute (higher for monitoring tools)
- **Transaction Queries**: 60 requests/minute (expensive queries)

### Rate Limit Headers

All responses include rate limit headers:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1699535460
```

### Rate Limit Exceeded Response

When rate limit is exceeded, you'll receive:

```json
{
  "error": "Rate limit exceeded",
  "message": "You have exceeded the rate limit for this API. Please try again later.",
  "detail": {
    "limit": "100 requests per minute, 1000 requests per hour",
    "scope": "Per IP address",
    "guidance": "This is an open API for public blockchain data. Rate limits prevent abuse while maintaining access for all."
  },
  "timestamp": "2025-11-09T10:30:00Z"
}
```

**Status Code**: 429 Too Many Requests  
**Retry-After Header**: 60 seconds

### Best Practices

1. **Respect Rate Limits**: Monitor rate limit headers and adjust request frequency
2. **Cache Responses**: Cache frequently accessed data locally
3. **Batch Requests**: Use query parameters to get multiple items in single request
4. **Handle 429 Errors**: Implement exponential backoff for retry logic
5. **Use Webhooks**: For real-time updates, consider webhook integration (future feature)

### Rate Limit Configuration

To modify rate limits for production deployment, edit `services/api/api_service.py`:

```python
limiter = Limiter(
    key_func=get_real_ip,
    default_limits=["100/minute", "1000/hour"],
    storage_uri="memory://",
)
```

For distributed deployments, use Redis for shared rate limit storage:

```python
storage_uri="redis://localhost:6379"
```

---

## Development

### Running Locally

#### Start API Server

```bash
# Activate virtual environment
source venv/bin/activate

# Start server with main orchestrator
python main.py serve --host 0.0.0.0 --port 8000

# Or with hot-reload for development
python main.py serve --host 0.0.0.0 --port 8000 --reload
```

**Server will start on**: `http://localhost:8000`  
**API Documentation**: `http://localhost:8000/api/docs`

#### Alternative: Direct Uvicorn

```bash
# For API development only (bypasses service orchestration)
uvicorn services.api.api_service:app --host 0.0.0.0 --port 8000 --reload
```

**Note**: This bypasses the service registry and may not have all dependencies initialized. Use `main.py serve` for complete system.

### Development Mode Features

- **Auto-Reload**: Code changes automatically restart server
- **Debug Mode**: Enhanced error messages and stack traces
- **Swagger UI**: Interactive API testing at `/api/docs`
- **ReDoc**: Alternative documentation at `/api/redoc`
- **Health Checks**: Real-time service status at `/health`

### Code Structure

```
services/api/
├── api_service.py           # Main FastAPI application
├── bioregion_endpoints.py   # Bioregion router (modular endpoints)
└── __init__.py

Key Components:
- BackendAPIService: Main service class
- create_backend_api_service(): Factory function
- Rate limiter configuration
- CORS middleware
- Health check system
```

### Adding New Endpoints

1. **Add endpoint to `api_service.py`**:

```python
@self.app.get("/api/v1/new-endpoint", response_model=Dict)
@limiter.limit("100/minute")
async def new_endpoint(request: Request) -> Dict:
    """
    Endpoint description.
    
    Rate limit: 100 requests/minute
    """
    try:
        # Implementation
        return {"result": "data"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

2. **Follow patterns**:
   - Always include `request: Request` parameter for rate limiting
   - Apply `@limiter.limit()` decorator AFTER `@self.app.get()`
   - Use try-except for error handling
   - Return consistent response format with `timestamp`
   - Document rate limits in docstring

3. **Test endpoint**:

```bash
curl http://localhost:8000/api/v1/new-endpoint
```

### Database Queries

Access database through service registry:

```python
async def get_data(self):
    # Get database service
    db = await self.registry.get('database')
    
    # Execute async query
    query = """
        SELECT * FROM ubec_main.my_table
        WHERE condition = $1
    """
    
    results = await db.fetch(query, 'value')
    return results
```

**Best Practices**:
- Use parameterized queries (`$1`, `$2`) to prevent SQL injection
- Always use async operations (`await`)
- Handle exceptions appropriately
- Close connections properly (handled by service registry)

---

## Testing

### Manual Testing

#### Test All Endpoints

```bash
# Run comprehensive endpoint test script
bash test_all_endpoints.sh
```

This script tests all 13 operational endpoints:
- Health endpoints (2)
- Token information (1)
- Network status (1)
- Distribution statistics (1)
- Holonic scores (3 with different filters)
- Transaction queries (2 with different limits)
- Bioregion endpoints (2)
- Ecoregion endpoints (4 with filters and specific IDs)
- Watershed endpoints (not in current test script, but available)

#### Test Individual Endpoints

```bash
# Health check
curl http://localhost:8000/health

# Token information
curl http://localhost:8000/api/v1/tokens

# Network status
curl http://localhost:8000/api/v1/network-status

# Holonic scores (with filters)
curl "http://localhost:8000/api/v1/holonic-scores?category=activator&limit=5"

# Recent transactions
curl "http://localhost:8000/api/v1/transactions?limit=10"

# Bioregions
curl http://localhost:8000/api/v1/bioregions
curl http://localhost:8000/api/v1/bioregions/1

# Ecoregions
curl http://localhost:8000/api/v1/ecoregions
curl "http://localhost:8000/api/v1/ecoregions?biome=forest&limit=5"
curl http://localhost:8000/api/v1/ecoregions/123

# Watersheds
curl http://localhost:8000/api/v1/watersheds
curl "http://localhost:8000/api/v1/watersheds?min_area=1000000&limit=10"
curl http://localhost:8000/api/v1/watersheds/101
```

### Rate Limit Testing

```bash
# Test rate limiting (should fail after 100 requests)
for i in {1..105}; do
  curl -s http://localhost:8000/api/v1/tokens > /dev/null
  echo "Request $i"
done

# Expected: First 100 succeed, next 5 return 429
```

### Automated Testing

```bash
# Run pytest suite (if implemented)
pytest tests/api/

# Run with coverage
pytest --cov=services/api tests/api/
```

### Load Testing

```bash
# Using Apache Bench (ab)
ab -n 1000 -c 10 http://localhost:8000/api/v1/tokens

# Using wrk
wrk -t12 -c400 -d30s http://localhost:8000/api/v1/tokens
```

**Expected Performance**:
- Response time: <100ms for simple queries
- Response time: <500ms for complex queries
- Throughput: >1000 requests/second
- Error rate: <0.1%

---

## Deployment

### Production Deployment Options

#### Option 1: Systemd Service (Recommended)

Create systemd service file:

```bash
# Create service file
sudo nano /etc/systemd/system/ubec-api.service
```

```ini
[Unit]
Description=UBEC Backend API Service
After=network.target postgresql.service

[Service]
Type=simple
User=ubec
Group=ubec
WorkingDirectory=/opt/ubec-protocol
Environment="PATH=/opt/ubec-protocol/venv/bin"
ExecStart=/opt/ubec-protocol/venv/bin/python main.py serve --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl enable ubec-api
sudo systemctl start ubec-api

# Check status
sudo systemctl status ubec-api

# View logs
sudo journalctl -u ubec-api -f
```

#### Option 2: Supervisor

```bash
# Install supervisor
sudo apt-get install supervisor

# Create config
sudo nano /etc/supervisor/conf.d/ubec-api.conf
```

```ini
[program:ubec-api]
command=/opt/ubec-protocol/venv/bin/python main.py serve --host 0.0.0.0 --port 8000
directory=/opt/ubec-protocol
user=ubec
autostart=true
autorestart=true
stdout_logfile=/var/log/ubec/api.log
stderr_logfile=/var/log/ubec/api-error.log
```

```bash
# Update supervisor
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start ubec-api
```

#### Option 3: Docker (Future)

```dockerfile
# Dockerfile (example)
FROM python:3.11-slim

WORKDIR /app
COPY . .

RUN pip install -r requirements.txt

EXPOSE 8000

CMD ["python", "main.py", "serve", "--host", "0.0.0.0", "--port", "8000"]
```

### Reverse Proxy Configuration

#### Nginx

```nginx
# /etc/nginx/sites-available/ubec-api
server {
    listen 80;
    server_name api.ubec.network;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Increase timeouts for long-running queries
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
```

```bash
# Enable site and restart nginx
sudo ln -s /etc/nginx/sites-available/ubec-api /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### Traefik (Alternative)

```yaml
# docker-compose.yml with Traefik labels
version: '3.8'
services:
  ubec-api:
    image: ubec-api:latest
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.ubec-api.rule=Host(`api.ubec.network`)"
      - "traefik.http.services.ubec-api.loadbalancer.server.port=8000"
```

### SSL/TLS Configuration

```bash
# Using Certbot (Let's Encrypt)
sudo apt-get install certbot python3-certbot-nginx
sudo certbot --nginx -d api.ubec.network

# Auto-renewal
sudo systemctl enable certbot.timer
```

### Environment-Specific Configuration

#### Production

```bash
# .env.production
LOG_LEVEL=WARNING
DB_MAX_POOL=20
STELLAR_RATE_LIMIT=5000
```

#### Staging

```bash
# .env.staging
LOG_LEVEL=INFO
DB_MAX_POOL=10
STELLAR_RATE_LIMIT=3000
```

#### Development

```bash
# .env.development
LOG_LEVEL=DEBUG
DB_MAX_POOL=5
STELLAR_RATE_LIMIT=1000
```

### Deployment Checklist

- [ ] Database schema deployed and verified
- [ ] Environment variables configured
- [ ] SSL certificates installed
- [ ] Reverse proxy configured
- [ ] Systemd/Supervisor service configured
- [ ] Health check endpoint accessible
- [ ] Rate limiting tested
- [ ] CORS origins updated for production domains
- [ ] Monitoring configured (see next section)
- [ ] Backup procedures in place
- [ ] Documentation updated

---

## Monitoring

### Health Monitoring

#### Automated Health Checks

```bash
# Add to crontab for periodic health checks
*/5 * * * * curl -f http://localhost:8000/health || mail -s "API Health Check Failed" admin@ubec.network
```

#### External Monitoring Services

Integrate with:
- **UptimeRobot**: Free tier available
- **Pingdom**: Comprehensive monitoring
- **DataDog**: Full observability platform
- **New Relic**: Application performance monitoring

### Logging

#### Log Locations

```bash
# Application logs
/var/log/ubec/api.log

# System service logs
sudo journalctl -u ubec-api -f

# Nginx access logs
/var/log/nginx/access.log

# Nginx error logs
/var/log/nginx/error.log
```

#### Log Rotation

```bash
# /etc/logrotate.d/ubec-api
/var/log/ubec/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 ubec ubec
    sharedscripts
    postrotate
        systemctl reload ubec-api > /dev/null 2>&1 || true
    endscript
}
```

### Performance Monitoring

#### Key Metrics to Track

1. **Response Times**:
   - Average: <100ms
   - P95: <500ms
   - P99: <1000ms

2. **Error Rates**:
   - Target: <0.1%
   - Alert threshold: >1%

3. **Rate Limit Hits**:
   - Monitor 429 responses
   - Adjust limits if legitimate users affected

4. **Database Performance**:
   - Query times
   - Connection pool utilization
   - Active connections

5. **System Resources**:
   - CPU usage
   - Memory usage
   - Disk I/O

#### Prometheus Integration (Future)

```python
# Add prometheus metrics
from prometheus_client import Counter, Histogram

request_count = Counter('api_requests_total', 'Total API requests')
request_duration = Histogram('api_request_duration_seconds', 'Request duration')

@app.middleware("http")
async def track_metrics(request: Request, call_next):
    request_count.inc()
    with request_duration.time():
        response = await call_next(request)
    return response
```

---

## Troubleshooting

### Common Issues

#### 1. API Service Won't Start

**Symptom**: Service fails to initialize

**Check**:
```bash
# Verify database connection
python main.py health

# Check logs
sudo journalctl -u ubec-api -n 50

# Verify environment variables
env | grep UBEC
```

**Common Causes**:
- Database not running or inaccessible
- Invalid database credentials
- Missing environment variables
- Port 8000 already in use

**Solutions**:
```bash
# Check if port is in use
sudo lsof -i :8000

# Verify database is running
sudo systemctl status postgresql

# Test database connection
psql -U ubec_app -d ubec -c "SELECT 1;"
```

#### 2. High Response Times

**Symptom**: API responses taking >1 second

**Check**:
```bash
# Check database query performance
psql -U ubec_app -d ubec

# Enable query logging
SET log_min_duration_statement = 100;

# Check slow queries
SELECT * FROM pg_stat_statements 
WHERE mean_exec_time > 100 
ORDER BY mean_exec_time DESC 
LIMIT 10;
```

**Common Causes**:
- Missing database indexes
- Large result sets without pagination
- Connection pool exhaustion
- Slow Stellar Horizon API responses

**Solutions**:
- Add appropriate database indexes
- Implement pagination for large queries
- Increase database connection pool size
- Implement caching for frequently accessed data

#### 3. Rate Limit Issues

**Symptom**: Legitimate users hitting rate limits

**Check**:
```bash
# Monitor rate limit hits
grep "Rate limit exceeded" /var/log/ubec/api.log | wc -l

# Check which IPs are affected
grep "Rate limit exceeded" /var/log/ubec/api.log | grep -oP 'IP: \K[^ ]+'
```

**Solutions**:
- Increase rate limits in `api_service.py`
- Implement IP whitelisting for known services
- Use Redis for distributed rate limiting
- Add authenticated endpoints with higher limits

#### 4. CORS Errors

**Symptom**: Browser console shows CORS policy errors

**Check**: Verify origin is in allowed list:
```python
# In api_service.py
allow_origins=[
    "https://www.ubec.network",
    "https://bioregional.ubec.network",
    "http://localhost:3000",
]
```

**Solutions**:
- Add your origin to `allow_origins` list
- Verify protocol (http vs https) matches
- Check for trailing slashes in URLs

#### 5. Database Connection Errors

**Symptom**: "could not connect to database" errors

**Check**:
```bash
# Verify PostgreSQL is running
sudo systemctl status postgresql

# Check database logs
sudo tail -f /var/log/postgresql/postgresql-15-main.log

# Test direct connection
psql -U ubec_app -h localhost -d ubec
```

**Solutions**:
- Restart PostgreSQL: `sudo systemctl restart postgresql`
- Check pg_hba.conf for access permissions
- Verify network connectivity
- Check connection pool settings

### Debug Mode

Enable debug mode for detailed error information:

```bash
# In .env
LOG_LEVEL=DEBUG

# Restart service
sudo systemctl restart ubec-api
```

**Warning**: Don't use DEBUG level in production - it exposes sensitive information.

### Getting Help

1. **Check Logs First**: Most issues are visible in logs
2. **Consult Documentation**: Review this README and API docs
3. **Test Endpoints**: Use Swagger UI at `/api/docs` for testing
4. **Run Health Checks**: `python main.py health` shows system status
5. **Community Support**: Post issues to GitHub repository

### Emergency Procedures

#### Emergency Shutdown

```bash
# Stop API service
sudo systemctl stop ubec-api

# Or kill process
pkill -f "python main.py serve"
```

#### Emergency Rollback

```bash
# Revert to previous version
cd /opt/ubec-protocol
git checkout <previous-commit>

# Restart service
sudo systemctl restart ubec-api
```

#### Database Recovery

```bash
# Restore from backup
psql -U ubec_app -d ubec < backup.sql

# Verify data integrity
python main.py health
```

---

## Design Principles

The UBEC API Service adheres to the [12 Project Design Principles](docs/COMPREHENSIVE_PROJECT_DESIGN_PRINCIPLES.md):

### 1. Modular Design and Architecture
- API service operates as self-contained module
- Clear boundaries with other services
- Well-defined interfaces for integration

### 2. Service Pattern with Centralized Execution
- No standalone execution - called via `main.py serve`
- Exposes functionality through standardized FastAPI interface
- Orchestrated by main.py entry point

### 3. Service Registry for Dependencies
- All dependencies injected via service registry
- No direct imports of other service modules
- Dynamic service discovery through registry

### 4. Single Source of Truth
- Database is authoritative data source
- No data duplication across services
- Configuration stored in database, not files

### 5. Strict Async Operations
- 100% async/await throughout codebase
- No blocking operations in any endpoint
- Concurrent request handling via asyncio

### 6. No Sync Fallbacks or Backward Compatibility
- Pure async implementation
- No legacy code or compatibility layers
- Forward-looking architecture only

### 7. Per-Asset Monitoring with Execution Minimums
- Individual endpoint rate limits
- Per-IP tracking and limiting
- Query result limits to prevent resource exhaustion

### 8. No Duplicate Configuration
- Environment variables for connection only
- Operational config from database
- Single definition of all settings

### 9. Integrated Rate Limiting
- Built-in SlowAPI rate limiting
- Per-endpoint limit configuration
- Prevents abuse without authentication

### 10. Clear Separation of Concerns
- API layer separate from business logic
- Data access via service registry
- Presentation logic in API responses only

### 11. Comprehensive Documentation
- Docstrings in all modules
- Auto-generated Swagger/ReDoc docs
- This comprehensive README

### 12. Method Singularity (No Redundancy)
- Each endpoint implemented once
- Shared functionality via service registry
- Zero code duplication

---

## API Versioning

### Current Version

**Version**: v1  
**Path Prefix**: `/api/v1/`

### Version Policy

- **Backwards Compatibility**: v1 endpoints remain stable
- **Breaking Changes**: Require new version (v2, v3, etc.)
- **Deprecation**: 6-month notice before removal
- **Documentation**: All versions documented

### Future Versions

When v2 is needed:
- v1 endpoints continue at `/api/v1/`
- v2 endpoints added at `/api/v2/`
- Both versions run simultaneously during transition

---

## Performance Optimization

### Current Performance

- **Response Time**: <100ms average for simple queries
- **Throughput**: >1000 requests/second
- **Concurrency**: Handles 100+ concurrent connections
- **Resource Usage**: <500MB RAM, <10% CPU at 100 req/s

### Optimization Techniques

1. **Database Indexing**:
   - All foreign keys indexed
   - Query-specific indexes on frequently filtered columns
   - 308 indexes across 68 tables

2. **Connection Pooling**:
   - Min 2 connections, Max 10 connections
   - Automatic connection recycling
   - Connection timeout: 30 seconds

3. **Query Optimization**:
   - Parameterized queries prevent injection
   - Result limits prevent memory exhaustion
   - Efficient JOIN strategies

4. **Async Operations**:
   - Non-blocking I/O throughout
   - Concurrent request handling
   - Efficient resource utilization

5. **Response Caching** (Future):
   - Redis cache for frequently accessed data
   - TTL-based invalidation
   - Cache warming for popular endpoints

---

## Security Considerations

### Current Security Measures

1. **No Authentication Required**:
   - Public blockchain data
   - Open access model
   - Rate limiting prevents abuse

2. **SQL Injection Prevention**:
   - Parameterized queries throughout
   - asyncpg automatic escaping
   - No string concatenation in SQL

3. **CORS Protection**:
   - Restricted to known domains
   - No wildcard origins in production
   - Credentials handling disabled

4. **Rate Limiting**:
   - IP-based tracking
   - Per-endpoint limits
   - Prevents DDoS and abuse

5. **Input Validation**:
   - Pydantic models for request validation
   - Type checking on all parameters
   - Range limits on numeric inputs

### Future Security Enhancements

1. **API Key Authentication**:
   - Optional authentication for higher limits
   - Per-user quota management
   - Usage analytics per API key

2. **HTTPS Only**:
   - Force TLS in production
   - HSTS headers
   - Certificate pinning

3. **Request Signing**:
   - HMAC signatures for authenticated requests
   - Timestamp validation
   - Replay attack prevention

4. **Advanced Rate Limiting**:
   - Per-user limits with authentication
   - Dynamic limits based on system load
   - Exponential backoff enforcement

---

## Contributing

### Development Workflow

1. **Fork Repository**: Create personal fork on GitHub
2. **Create Branch**: `git checkout -b feature/your-feature-name`
3. **Make Changes**: Implement feature or fix
4. **Test**: Run tests and verify functionality
5. **Commit**: Clear commit messages following conventions
6. **Push**: Push to your fork
7. **Pull Request**: Submit PR with description

### Code Standards

- **Python Style**: PEP 8 compliant
- **Type Hints**: Use type annotations throughout
- **Docstrings**: All functions documented
- **Async/Await**: All I/O operations must be async
- **Error Handling**: Comprehensive try-except blocks
- **Testing**: Unit tests for new features

### Testing Requirements

- All new endpoints must have tests
- Maintain >80% code coverage
- Integration tests for complex workflows
- Load tests for performance-critical endpoints

### Documentation Requirements

- Update README for new endpoints
- Add docstrings to all functions
- Include examples in API docs
- Update CHANGELOG.md

---

## Changelog

### Version 2.1.2 (2025-11-08)
- Added `/api/v1/holonic-scores` endpoint
- Fixed rate limit middleware tuple handling
- Improved token endpoint configuration service usage

### Version 2.1.1 (2025-11-07)
- Fixed rate limit response headers
- Improved error handling for database queries
- Enhanced health check dependency status

### Version 2.1.0 (2025-11-05)
- Added bioregion endpoints module
- Implemented IP-based rate limiting
- Added comprehensive health checks
- CORS configuration for production domains

### Version 2.0.0 (2025-10-15)
- Complete rewrite with FastAPI
- Service registry integration
- Async/await throughout
- Database-backed configuration

---

## License

[Add your license information here]

---

## Contact and Support

- **Website**: https://www.ubec.network
- **Email**: support@ubec.network
- **GitHub**: [Repository URL]
- **Documentation**: https://docs.ubec.network

---

## Additional Resources

- [Main Project README](../README.md)
- [Database Schema Documentation](../docs/database/)
- [Holonic Evaluation Guide](../docs/holonic_metrics_explained.md)
- [UBEC Protocol White Paper](../docs/UBEC_Protocol_White_Paper.md)
- [System Administrator Guide](../docs/User_Guides/SYSTEM_ADMINISTRATOR_ONBOARDING_GUIDE.md)
- [Developer Onboarding Guide](../docs/User_Guides/UBEC_Developer_Onboarding_Guide.md)

---

**Last Updated**: November 9, 2025  
**Document Version**: 1.0  
**API Version**: 2.1.2  
**Status**: Production Ready
