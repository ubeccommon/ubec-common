# UBEC Protocol - Web Interface & Dashboard

**Ubuntu Bioregional Economic Commons**

[![Status](https://img.shields.io/badge/status-development-yellow)]()
[![Completion](https://img.shields.io/badge/completion-65--70%25-orange)]()
[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green)](https://fastapi.tiangolo.com)

> *"I am because we are"* - Ubuntu Philosophy

Public-facing web interface and dashboard for the UBEC Protocol Suite, showcasing the four-element token ecosystem and Ubuntu principles through an intuitive, responsive web application.

> **⚠️ IMPORTANT**: This is the **frontend web interface only**. The backend API service resides in the main UBEC Protocol repository. Both must be installed and running for the system to function.

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Features](#features)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Development](#development)
- [Current Status](#current-status)
- [Contributing](#contributing)
- [Attribution](#attribution)

---

## Overview

The UBEC Web Interface is a modern, asynchronous web application that provides:

- **Public Dashboard**: Real-time visualization of the four-element token ecosystem
- **Token Information**: Detailed information about UBEC, UBECrc, UBECgpi, and UBECtt tokens
- **Network Statistics**: Live metrics from the Stellar blockchain
- **Holonic Evaluations**: Ubuntu principle assessments and scores
- **Documentation Portal**: Comprehensive guides for users and developers
- **API Endpoints**: RESTful API for external integrations

### Four Elements

- 🜁 **Air (UBEC)** - Gateway & Universal Access (Diversity)
- 🜄 **Water (UBECrc)** - Flow & Exchange (Reciprocity)
- 🜃 **Earth (UBECgpi)** - Stability & Value (Mutualism)
- 🜂 **Fire (UBECtt)** - Transformation & Action (Regeneration)

---

## Architecture

### Two-Tier Design with Separate Deployments

The interface uses a clean two-tier architecture with **TWO separate server deployments**:

```
┌─────────────────────────────────────┐
│          PUBLIC INTERNET             │
└──────────────┬──────────────────────┘
               │ HTTPS
               ▼
┌─────────────────────────────────────┐
│   Frontend Server (ubec_interface/)  │
│          Port 8001                   │
│   - Page rendering (Jinja2)         │
│   - Static assets                   │
│   - Client-side routing             │
│   - BackendAPIClient                │
└──────────────┬──────────────────────┘
               │ HTTP (Internal Network)
               ▼
┌─────────────────────────────────────┐
│   Backend Server (UBEC_Protocol/)   │
│          Port 8000                   │
│   - REST API endpoints              │
│   - Data aggregation                │
│   - Database queries                │
│   - Service integration             │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│      PostgreSQL Database             │
└─────────────────────────────────────┘
```

**IMPORTANT**: 
- The **backend API service** (`api_service.py`) is NOT part of this repository
- It resides in the main UBEC Protocol repository (`UBEC_Protocol/services/api/api_service.py`)
- The backend must be running separately for the frontend to function
- Backend should NOT be exposed to public internet - internal access only

### Technology Stack

**Frontend Server**:
- FastAPI - Modern web framework
- Jinja2 - Template engine
- aiohttp - Async HTTP client
- Pydantic - Settings validation
- Uvicorn - ASGI server

**Backend API**:
- FastAPI - REST API framework
- asyncio - Async operations
- PostgreSQL - Database
- Service Registry - Dependency management

**Development**:
- Python 3.11+
- pytest - Testing framework
- black - Code formatting
- mypy - Type checking

---

## Features

### Implemented ✅

1. **Frontend Web Server**
   - FastAPI application with routing
   - Jinja2 template rendering
   - Static file serving
   - CORS middleware
   - GZip compression
   - Error handling
   - Health checks

2. **Backend API Service**
   - RESTful API endpoints
   - OpenAPI documentation
   - Service registry integration
   - Database connectivity
   - Real-time data access
   - Comprehensive health monitoring

3. **HTTP Client**
   - Async communication
   - Response caching (30s TTL)
   - Session management
   - Error handling
   - Connection pooling

4. **Configuration System**
   - Environment variables
   - Pydantic validation
   - Security checks
   - Feature flags
   - Multi-environment support

5. **Page Routes**
   - Home page (`/`)
   - Token stories (`/stories`)
   - About page (`/about`)
   - Documentation (`/docs`)
   - API routes (`/api/v1`)
   - Health endpoint (`/health`)

### In Development ⚠️

1. **Frontend Templates**
   - Complete HTML/CSS implementation
   - JavaScript interactivity
   - Data visualization
   - Responsive design
   - Ubuntu visual identity

2. **Content**
   - Token narratives
   - Project documentation
   - User guides
   - Community resources

3. **Features**
   - WebSocket real-time updates
   - Rate limiting
   - Metrics collection
   - User analytics

---

## Project Structure

```
ubec_interface/                    # THIS REPOSITORY
├── main_web.py                    # Frontend web server
├── config/
│   └── settings.py                # Configuration management
├── api/
│   ├── routes.py                  # Frontend API route definitions
│   └── backend_api.py             # Legacy backend client (deprecated)
├── utils/
│   └── backend_client.py          # HTTP client utility
├── templates/                     # Jinja2 templates
│   ├── base.html                  # Base template
│   ├── home.html                  # Home page
│   ├── stories.html               # Token stories
│   ├── about.html                 # About page
│   ├── docs.html                  # Documentation
│   └── error.html                 # Error page
├── static/                        # Static assets
│   ├── css/                       # Stylesheets (TO BE CREATED)
│   ├── js/                        # JavaScript
│   │   └── main.js                # Main JS file
│   ├── images/                    # Images/graphics (TO BE CREATED)
│   └── fonts/                     # Custom fonts (TO BE CREATED)
├── tests/                         # Test suite
│   ├── test_web.py                # Web server tests
│   ├── test_api.py                # API tests
│   └── test_client.py             # Client tests
├── .env                           # Environment variables
├── .env.example                   # Environment template
├── requirements.txt               # Python dependencies
└── README.md                      # This file
```

**NOT in this repository** (part of main UBEC Protocol):
```
UBEC_Protocol/                     # SEPARATE REPOSITORY
├── main.py                        # Protocol orchestrator
├── services/
│   └── api/
│       └── api_service.py         # Backend API service ← NOT HERE
├── core/
│   ├── service_registry.py
│   ├── db/
│   │   └── database_manager.py
│   └── protocols/
│       ├── UBEC_protocol.py
│       ├── UBECrc_protocol.py
│       ├── UBECgpi_protocol.py
│       └── UBECtt_protocol.py
└── ... (all core UBEC services)
```

---

## Installation

### Prerequisites

- Python 3.11 or higher
- **UBEC Protocol backend** (separate installation required)
  - Must be running on port 8000 (or configured port)
  - See main UBEC Protocol repository for installation
- Git

**IMPORTANT**: This is only the frontend web interface. You must have the main UBEC Protocol backend installed and running separately. The backend provides the API that this frontend consumes.

### Step 1: Clone Repository

```bash
git clone https://github.com/ubeccommon/ubec_interface.git
cd ubec_interface
```

### Step 2: Create Virtual Environment

```bash
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit configuration
nano .env
```

Required environment variables:
```bash
# Application
APP_ENV=development
APP_HOST=127.0.0.1
APP_PORT=8001
LOG_LEVEL=INFO

# Backend API
BACKEND_API_URL=http://localhost:8000
BACKEND_API_KEY=

# Security
SECRET_KEY=change-this-in-production
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8001

# Features
ENABLE_API_DOCS=true
ENABLE_METRICS=true
ENABLE_WEBSOCKETS=false

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60
```

### Step 5: Verify Backend is Running

**IMPORTANT**: The backend API must be installed and running separately.

**If you haven't installed the UBEC Protocol backend yet**:
1. Clone the main UBEC Protocol repository
2. Follow its installation instructions
3. Start the backend API: `python main.py serve --port 8000`

**Verify backend is accessible**:

```bash
# Check backend health
curl http://localhost:8000/health

# Expected response:
# {"status": "healthy", "version": "2.0.0", ...}
```

If the backend is not running, the frontend will not be able to fetch data.

---

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `APP_ENV` | `production` | Environment: development, staging, production |
| `APP_HOST` | `127.0.0.1` | Host to bind server (use 127.0.0.1 for localhost) |
| `APP_PORT` | `8001` | Port for frontend server |
| `LOG_LEVEL` | `INFO` | Logging level: DEBUG, INFO, WARNING, ERROR |
| `BACKEND_API_URL` | `http://localhost:8000` | Backend API base URL |
| `BACKEND_API_KEY` | `` | API authentication key (if required) |
| `SECRET_KEY` | `change-this-in-production` | Secret for sessions/JWT |
| `ALLOWED_ORIGINS` | `["https://www.ubec.network"]` | CORS allowed origins |
| `ENABLE_API_DOCS` | `false` | Enable OpenAPI documentation |
| `ENABLE_METRICS` | `true` | Enable metrics collection |
| `ENABLE_WEBSOCKETS` | `false` | Enable WebSocket support |
| `RATE_LIMIT_PER_MINUTE` | `60` | API rate limit per IP |

### Security Configuration

**For Production**:
1. Change `SECRET_KEY` to a strong random value
2. Set `APP_ENV=production`
3. Restrict `ALLOWED_ORIGINS` to your domain
4. Use HTTPS with reverse proxy (Nginx)
5. Set `ENABLE_API_DOCS=false`

**For Development**:
1. Set `APP_ENV=development`
2. Use `ENABLE_API_DOCS=true` for API exploration
3. Relaxed CORS for localhost testing

---

## Usage

### Two-Server Startup Process

**IMPORTANT**: Both servers must be running:

1. **Backend Server** (do this first)
2. **Frontend Server** (this repository)

### Start Backend Server (Required First)

The backend API must be started from the main UBEC Protocol repository:

```bash
# Navigate to UBEC Protocol repository
cd /path/to/UBEC_Protocol

# Start backend API server
python main.py serve --host 0.0.0.0 --port 8000
```

**Verify backend is running**:
```bash
curl http://localhost:8000/health
```

### Start Frontend Server (This Repository)

**Development Mode** (with auto-reload):
```bash
uvicorn main_web:app --reload --host 127.0.0.1 --port 8001
```

**Production Mode**:
```bash
uvicorn main_web:app --host 0.0.0.0 --port 8001 --workers 4
```

**Using Gunicorn** (recommended for production):
```bash
gunicorn main_web:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8001
```

### Access Interface

- **Home Page**: http://localhost:8001
- **API Docs**: http://localhost:8001/api/docs (if enabled)
- **Health Check**: http://localhost:8001/health
- **Backend API** (internal): http://localhost:8000

**Note**: The backend API (port 8000) should not be directly accessed from the public internet in production. It's for internal use by the frontend only.

---

## API Documentation

### Frontend API Endpoints

Base URL: `http://localhost:8001/api/v1`

#### Tokens

**GET `/api/v1/tokens`**
- Description: Get all four UBEC tokens
- Response: Array of token objects
- Cache: 30 seconds

**GET `/api/v1/tokens/{token_code}`**
- Description: Get specific token details
- Parameters: `token_code` (UBEC, UBECrc, UBECgpi, UBECtt)
- Response: Token object
- Cache: 30 seconds

#### Network

**GET `/api/v1/network/status`**
- Description: Get network statistics
- Response: Network status object with bioregion count
- Cache: 30 seconds

**GET `/api/v1/transactions/recent`**
- Description: Get recent transactions
- Query Parameters: `limit` (default: 10)
- Response: Array of transaction objects
- Cache: 15 seconds

#### Holonic Evaluation

**GET `/api/v1/holonic/scores`**
- Description: Get Ubuntu principle scores
- Query Parameters: `account_id` (optional)
- Response: Array of holonic score objects
- Cache: 60 seconds

#### Distribution

**GET `/api/v1/distributions/stats`**
- Description: Get distribution statistics
- Response: Distribution stats object
- Cache: 60 seconds

#### System

**GET `/api/v1/system/info`**
- Description: Get system information
- Response: System info object

**GET `/api/v1/system/health`**
- Description: Check system health
- Response: Health status object

### Backend API Endpoints

**Location**: Provided by the main UBEC Protocol backend (separate repository)  
**Base URL**: `http://localhost:8000` (internal access only)

**⚠️ Note**: These endpoints are provided by the backend server, not this repository. They are documented here for reference.

Full documentation available at: `http://localhost:8000/api/docs` (when backend running)

---

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_web.py

# Run with verbose output
pytest -v
```

### Code Quality

```bash
# Format code with black
black .

# Type checking with mypy
mypy .

# Lint with flake8
flake8 .
```

### Development Workflow

**Two-Server Development Setup**:

1. **Start Backend** (in separate terminal from UBEC Protocol repository):
   ```bash
   cd /path/to/UBEC_Protocol
   python main.py serve --port 8000
   ```

2. **Start Frontend** (from this repository, with auto-reload):
   ```bash
   cd /path/to/ubec_interface
   uvicorn main_web:app --reload --port 8001
   ```

3. **Access Application**:
   - Frontend: http://localhost:8001
   - Backend API: http://localhost:8000/api/docs (for reference only)

4. **Make Changes**:
   - Edit templates in `templates/`
   - Edit styles in `static/css/`
   - Edit JavaScript in `static/js/`
   - Frontend server auto-reloads on changes
   - Backend changes require restarting backend server

### Adding New Pages

1. Create template in `templates/`:
   ```html
   {% extends "base.html" %}
   {% block title %}New Page{% endblock %}
   {% block content %}
   <!-- Your content -->
   {% endblock %}
   ```

2. Add route in `main_web.py`:
   ```python
   @app.get("/newpage", response_class=HTMLResponse)
   async def new_page(request: Request):
       return templates.TemplateResponse(
           "newpage.html",
           {"request": request, "page": "newpage"}
       )
   ```

3. Update navigation in `base.html`

### Adding API Endpoints

1. Add endpoint in `api/routes.py`:
   ```python
   @router.get("/custom/endpoint")
   async def custom_endpoint(
       client: BackendAPIClient = Depends(get_backend_client)
   ) -> Dict:
       data = await client._cached_get("/api/custom/data")
       return data
   ```

2. Add client method in `utils/backend_client.py`:
   ```python
   async def get_custom_data(self) -> Dict:
       return await self._cached_get("/api/custom/data", ttl=60)
   ```

---

## Current Status

### Completion: 65-70%

**Note**: This completion percentage refers to the `ubec_interface/` repository only. The backend API service (`api_service.py`) is complete and operational, but it resides in the separate UBEC Protocol repository.

#### ✅ Complete

- Two-tier architecture
- FastAPI web server (frontend)
- Backend API service (in UBEC Protocol repository - operational)
- HTTP client with caching
- Configuration system
- Page routing
- API endpoints
- Service integration
- Health monitoring
- Error handling
- Logging infrastructure

#### ⚠️ In Progress

- HTML template completion
- CSS styling
- JavaScript interactivity
- Data visualization
- Content writing
- Testing suite

#### ❌ Not Started

- Visual design system
- Ubuntu visual identity
- Responsive design
- WebSocket implementation
- Rate limiting configuration
- Metrics dashboard
- User authentication (if needed)
- Deployment automation

### Known Issues

1. **Templates Incomplete**
   - Issue: Templates have structure but no content/styling
   - Impact: Interface not user-facing ready
   - Priority: HIGH
   - Solution: Frontend development required

2. **No Visual Design**
   - Issue: No CSS, colors, or Ubuntu identity
   - Impact: Generic appearance, no brand
   - Priority: HIGH
   - Solution: Design system needed

3. **Untested Integration**
   - Issue: End-to-end testing not performed
   - Impact: Unknown integration issues
   - Priority: MEDIUM
   - Solution: Integration test suite

### Roadmap

**Phase 1: Visual Foundation** (2-3 weeks)
- Design Ubuntu-inspired visual identity
- Implement base template with styling
- Create CSS framework

**Phase 2: Page Implementation** (2-3 weeks)
- Complete all HTML templates
- Write content for all pages
- Add images and graphics

**Phase 3: Data Integration** (1-2 weeks)
- Connect templates to real data
- Add chart/visualization libraries
- JavaScript interactivity

**Phase 4: Testing & Polish** (1-2 weeks)
- Integration testing
- Performance optimization
- Security review

**Phase 5: Deployment** (1 week)
- Documentation
- CI/CD pipeline
- Production deployment

**Total Estimated Time**: 7-11 weeks

---

## Contributing

### Development Guidelines

1. **Follow Design Principles**
   - Respect all 12 UBEC design principles
   - Maintain async patterns
   - No code duplication
   - Comprehensive documentation

2. **Code Style**
   - Use black for formatting
   - Type hints required
   - Docstrings for all functions
   - Meaningful variable names

3. **Testing**
   - Write tests for new features
   - Maintain >80% code coverage
   - Test error scenarios
   - Document test cases

4. **Attribution**
   - Include attribution in all new files
   - Update documentation
   - Credit contributors

### Pull Request Process

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Make changes following guidelines
4. Add tests for new functionality
5. Update documentation
6. Commit changes (`git commit -m 'Add amazing feature'`)
7. Push to branch (`git push origin feature/amazing-feature`)
8. Open Pull Request

---

## Attribution

This project uses the services of Claude and Anthropic PBC to inform our decisions and recommendations. This project was made possible with the assistance of Claude and Anthropic PBC.

### Acknowledgments

- **Ubuntu Philosophy** - Foundation of project design
- **Stellar Network** - Blockchain infrastructure
- **FastAPI** - Web framework
- **UBEC Community** - Inspiration and support

---

## License

This project is part of the UBEC Protocol Suite. See main project for license details.

---

## Contact & Support

- **Website**: (Coming soon)
- **Documentation**: http://localhost:8001/docs
- **API Docs**: http://localhost:8001/api/docs
- **GitHub**: https://github.com/ubeccommon/ubec_interface
- **Issues**: https://github.com/ubeccommon/ubec_interface/issues

---

**Ubuntu**: *"I am because we are"* 🌍

---

**Version**: 1.0.0-beta  
**Last Updated**: November 5, 2025  
**Status**: Development (65-70% complete)
