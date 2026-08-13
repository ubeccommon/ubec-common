# UBEC Application System - Deployment Guide

## Overview

This system handles applications from the four core beneficiary types:
- 🌾 **Farmers** - Small-scale regenerative agriculture
- 🏘️ **Communities** - Collective food sovereignty groups
- 🔄 **Activators** - Facilitators and trainers
- 🎓 **Living Labs** - Educational institutions with monitoring

## Architecture

```
User submits form on bioregional.ubec.network
         ↓
POST /api/v1/applications/{type}
         ↓
Backend API (api.ubec.network)
         ↓
    ┌────┴────┐
    ↓         ↓
PostgreSQL   Email
 Storage    Notification
```

## Files to Deploy

### Frontend Server (92.205.28.58)

| File | Destination |
|------|-------------|
| `apply.html` | `templates/apply.html` |
| `apply-farmer.html` | `templates/apply-farmer.html` |
| `apply-community.html` | `templates/apply-community.html` |
| `apply-activator.html` | `templates/apply-activator.html` |
| `apply-livinglab.html` | `templates/apply-livinglab.html` |
| `main_web.py` | Replace existing |

### Backend Server (92.205.230.245)

| File | Destination |
|------|-------------|
| `001_create_applications_table.sql` | Run in PostgreSQL |
| `application_schemas.py` | `schemas/application_schemas.py` |
| `application_routes.py` | `routes/application_routes.py` |

## Step-by-Step Deployment

### 1. Database Setup

Connect to PostgreSQL and run the migration:

```bash
psql -U ubec -d ubec_db -f 001_create_applications_table.sql
```

Or via Python:
```python
import asyncpg
# ... run the SQL file
```

### 2. Backend Setup

**a) Add schema file:**
```bash
cp application_schemas.py /path/to/backend/schemas/
```

**b) Add routes file:**
```bash
cp application_routes.py /path/to/backend/routes/
```

**c) Register routes in your main app:**

Edit your main API file (e.g., `main_api.py`):
```python
from routes.application_routes import router as application_router

# Add after other routers
app.include_router(application_router)
```

**d) Configure email settings:**

Add to your `.env` file:
```env
# Email Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=noreply@ubec.network
ADMIN_EMAIL=applications@ubec.network
```

Add to your `config/settings.py`:
```python
class Settings(BaseSettings):
    # ... existing settings ...
    
    # Email Configuration
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    FROM_EMAIL: str = "noreply@ubec.network"
    ADMIN_EMAIL: str = "applications@ubec.network"
```

**e) Restart backend:**
```bash
sudo systemctl restart ubec-api
```

### 3. Frontend Setup

Copy all template files:
```bash
cp apply*.html /srv/ubec-www/app/templates/
cp main_web.py /srv/ubec-www/app/
sudo systemctl restart ubec-www
```

## API Endpoints Created

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/applications/farmer` | Submit farmer application |
| POST | `/api/v1/applications/community` | Submit community application |
| POST | `/api/v1/applications/activator` | Submit activator application |
| POST | `/api/v1/applications/livinglab` | Submit living lab application |
| GET | `/api/v1/applications` | List all applications (admin) |
| GET | `/api/v1/applications/{ref}` | Get application by reference |
| GET | `/api/v1/applications/stats/summary` | Get statistics |

## Reference Number Format

Applications get unique reference numbers:
- `FRM-2025-0001` - Farmer
- `COM-2025-0001` - Community
- `ACT-2025-0001` - Activator
- `LAB-2025-0001` - Living Lab

## Email Notifications

When an application is submitted:
1. **Admin notification** → sent to `applications@ubec.network`
2. **Applicant confirmation** → sent to their email

Emails include:
- Reference number
- Application summary
- Next steps and timeline

## Gmail Setup for SMTP

1. Enable 2-Factor Authentication on your Google account
2. Go to Google Account → Security → App Passwords
3. Generate a new App Password for "Mail"
4. Use the 16-character password as `SMTP_PASSWORD`

## Testing

Test form submission:
```bash
curl -X POST https://api.ubec.network/api/v1/applications/farmer \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Farmer",
    "contact_email": "test@example.com",
    "location": "Test City, Country",
    "farm_size": "5 hectares",
    "products": "Vegetables, fruits",
    "regenerative_practices": "Cover cropping, composting, no-till",
    "experience": "intermediate",
    "requested_amount": 10000,
    "token_usage": "Seeds and tools",
    "expected_impact": "Feed 50 families",
    "ubuntu_alignment": "Community sharing and mutual aid",
    "community_connections": "Local farmers market",
    "reference1_name": "Jane Doe",
    "reference1_contact": "jane@example.com",
    "agree_terms": true,
    "agree_values": true
  }'
```

## Troubleshooting

**Forms not submitting:**
- Check browser console for errors
- Verify API endpoint is accessible
- Check CORS settings

**Emails not sending:**
- Verify SMTP credentials
- Check if SMTP_USER is set (empty = disabled)
- Check server logs for email errors

**Database errors:**
- Ensure migration was run successfully
- Check database connection settings
- Verify `generate_application_reference` function exists

---

*This project uses the services of Claude and Anthropic PBC.*
