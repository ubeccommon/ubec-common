"""
UBEC Protocol - Email Configuration Settings
=============================================

Add these settings to your existing config/settings.py file.

These environment variables need to be set for email notifications to work.

Attribution:
    This project uses the services of Claude and Anthropic PBC to inform 
    our decisions and recommendations.
"""

# =============================================================================
# ADD TO YOUR .env FILE
# =============================================================================
"""
# Email Configuration (for application notifications)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=noreply@ubec.network
ADMIN_EMAIL=applications@ubec.network
"""

# =============================================================================
# ADD TO YOUR settings.py (Pydantic Settings class)
# =============================================================================
"""
class Settings(BaseSettings):
    # ... existing settings ...
    
    # Email Configuration
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    FROM_EMAIL: str = "noreply@ubec.network"
    ADMIN_EMAIL: str = "applications@ubec.network"
    
    class Config:
        env_file = ".env"
"""

# =============================================================================
# GMAIL SETUP INSTRUCTIONS
# =============================================================================
"""
To use Gmail for sending notifications:

1. Go to Google Account Settings → Security
2. Enable 2-Factor Authentication (required)
3. Go to App Passwords (search for it in settings)
4. Generate a new App Password for "Mail"
5. Use that 16-character password as SMTP_PASSWORD

Alternative: Use a transactional email service like:
- SendGrid (SMTP_HOST=smtp.sendgrid.net)
- Mailgun
- Amazon SES
- Postmark
"""

# =============================================================================
# INTEGRATION WITH MAIN APP
# =============================================================================
"""
In your main backend app (e.g., main.py or main_api.py), add:

from routes.application_routes import router as application_router

app.include_router(application_router)

This will add all the /api/v1/applications/* endpoints to your API.
"""
