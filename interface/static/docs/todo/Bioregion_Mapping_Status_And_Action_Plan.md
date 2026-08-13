# UBEC Email Service - Configuration & Deployment Guide

**Attribution:** This project uses the services of Claude and Anthropic PBC to inform our decisions and recommendations. This project was made possible with the assistance of Claude and Anthropic PBC.

## Overview

This guide will help you implement email functionality for the UBEC Protocol system, including:
- Email notifications for bioregion applications
- Ubuntu score alerts
- System notifications
- Community communications

---

## Prerequisites

- UBEC Protocol system installed
- SMTP server access (Gmail, SendGrid, AWS SES, Mailgun, etc.)
- Database access with proper permissions

---

## Step 1: Install Required Dependencies

```bash
# On your server (kelpit@58)
cd /opt/ubec-protocol  # Or wherever your UBEC code is

# Activate virtual environment
source venv/bin/activate

# Install email dependencies
pip install aiosmtplib jinja2 --break-system-packages

# Verify installation
python -c "import aiosmtplib; import jinja2; print('✓ Dependencies installed')"
```

---

## Step 2: Create Database Schema

```bash
# Copy the schema file to your server
# (Assuming you've downloaded it)

# Connect to PostgreSQL
sudo -u postgres psql -d ubec

# Run the schema creation script
\i /path/to/email_service_schema.sql

# Verify tables were created
\dt ubec_main.email*

# Expected output:
#  ubec_main | email_queue       | table
#  ubec_main | email_rate_limits | table

# Exit psql
\q
```

---

## Step 3: Configure SMTP Settings

### Option A: Using Gmail (Development/Testing)

1. **Enable 2-Factor Authentication** on your Gmail account
2. **Create an App Password:**
   - Go to https://myaccount.google.com/apppasswords
   - Select "Mail" and your device
   - Copy the 16-character password

3. **Add to .env file:**

```bash
# Edit your .env file
cd /opt/ubec-protocol
nano .env

# Add these lines:
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password-here
SMTP_USE_TLS=true
SMTP_FROM_EMAIL=your-email@gmail.com
SMTP_FROM_NAME=UBEC Protocol
```

### Option B: Using SendGrid (Production)

```bash
# .env configuration
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USERNAME=apikey
SMTP_PASSWORD=your-sendgrid-api-key
SMTP_USE_TLS=true
SMTP_FROM_EMAIL=noreply@ubec.network
SMTP_FROM_NAME=UBEC Protocol
```

### Option C: Using AWS SES (Production)

```bash
# .env configuration
SMTP_HOST=email-smtp.us-east-1.amazonaws.com
SMTP_PORT=587
SMTP_USERNAME=your-aws-access-key-id
SMTP_PASSWORD=your-aws-secret-access-key
SMTP_USE_TLS=true
SMTP_FROM_EMAIL=noreply@ubec.network
SMTP_FROM_NAME=UBEC Protocol
```

### Option D: Using Mailgun (Production)

```bash
# .env configuration
SMTP_HOST=smtp.mailgun.org
SMTP_PORT=587
SMTP_USERNAME=postmaster@yourdomain.mailgun.org
SMTP_PASSWORD=your-mailgun-smtp-password
SMTP_USE_TLS=true
SMTP_FROM_EMAIL=noreply@ubec.network
SMTP_FROM_NAME=UBEC Protocol
```

---

## Step 4: Create Email Templates Directory

```bash
# Create templates directory
sudo mkdir -p /srv/ubec-www/email_templates

# Copy template files
sudo cp email_template_welcome.html /srv/ubec-www/email_templates/welcome.html

# Create a plain text version
cat > /tmp/welcome.txt << 'EOF'
Hello {{ name }},

Welcome to the Ubuntu Bioregional Economic Commons Protocol! We're thrilled to have you join our community of {{ bioregion_name }}.

"I am because we are" - This Ubuntu philosophy guides everything we do.

Your Four Elements:
🌬️ UBEC (Air) - Diversity & Circulation
💧 UBECrc (Water) - Reciprocity & Flow
🌍 UBECgpi (Earth) - Mutualism & Growth
🔥 UBECtt (Fire) - Regeneration & Transformation

Next Steps:
1. Complete your profile setup
2. Connect your Stellar wallet
3. Attend your first bioregion gathering
4. Start your first transaction

Visit your dashboard: {{ dashboard_url }}

With Ubuntu,
The UBEC Protocol Team

---
This project uses the services of Claude and Anthropic PBC.
Ubuntu Bioregional Economic Commons Protocol
Unsubscribe: {{ unsubscribe_url }}
EOF

sudo cp /tmp/welcome.txt /srv/ubec-www/email_templates/welcome.txt

# Set permissions
sudo chown -R www-data:www-data /srv/ubec-www/email_templates
sudo chmod -R 755 /srv/ubec-www/email_templates
```

---

## Step 5: Add Email Service to UBEC Protocol

### A. Copy the Service File

```bash
# Copy the email service to your UBEC services directory
sudo cp ubec_email_service.py /opt/ubec-protocol/services/email/

# Create __init__.py if directory doesn't exist
sudo mkdir -p /opt/ubec-protocol/services/email
sudo touch /opt/ubec-protocol/services/email/__init__.py

# Or if using core/ directory structure:
sudo cp ubec_email_service.py /opt/ubec-protocol/core/email_service.py
```

### B. Register with Service Registry

Edit your `main.py` or wherever services are registered:

```python
# main.py or core/service_registry.py

# Import the email service
from services.email.ubec_email_service import create_email_service
# OR
from core.email_service import create_email_service

async def setup_services(registry: ServiceRegistry):
    """Register all services with the registry."""
    
    # ... existing service registrations ...
    
    # Register email service
    registry.register_factory(
        'email',
        create_email_service,
        dependencies=['database', 'config_manager']
    )
    
    logger.info("✓ All services registered")
```

---

## Step 6: Test the Email Service

### Test Script

Create a test file:

```python
# test_email.py
import asyncio
import sys
import os
sys.path.insert(0, '/opt/ubec-protocol')

from core.service_registry import ServiceRegistry

async def test_email():
    """Test email service."""
    print("Testing UBEC Email Service...")
    print("=" * 50)
    
    # Initialize service registry
    registry = ServiceRegistry()
    await registry.initialize_all()
    
    # Get email service
    email = await registry.get('email')
    
    # Check health
    health = await email.health_check()
    print(f"\nHealth Check: {health}")
    
    # Send test email
    print("\nSending test email...")
    email_id = await email.send_email(
        to_email='your-email@example.com',  # CHANGE THIS
        to_name='Test User',
        subject='UBEC Email Service Test',
        body_text='This is a test email from the UBEC Protocol email service.',
        body_html='<h1>Test Email</h1><p>This is a test email from the UBEC Protocol email service.</p>'
    )
    
    print(f"✓ Email queued with ID: {email_id}")
    
    # Check queue status
    await asyncio.sleep(35)  # Wait for queue processor
    stats = await email.get_queue_status()
    print(f"\nQueue Status: {stats}")
    
    # Cleanup
    await registry.cleanup()
    print("\n✓ Test complete!")

if __name__ == '__main__':
    asyncio.run(test_email())
```

Run the test:

```bash
# Make sure you're in the right directory and venv is activated
cd /opt/ubec-protocol
source venv/bin/activate

# Run test
python test_email.py
```

---

## Step 7: Using the Email Service

### Send Simple Email

```python
# In your code
email_service = await registry.get('email')

await email_service.send_email(
    to_email='user@example.com',
    to_name='John Doe',
    subject='Welcome to UBEC',
    body_text='Welcome message here',
    body_html='<p>Welcome message here</p>'
)
```

### Send Template Email

```python
# Send welcome email using template
await email_service.send_template_email(
    to_email='user@example.com',
    to_name='John Doe',
    template_name='welcome',  # Looks for welcome.html
    subject='Welcome to UBEC Protocol',
    template_data={
        'name': 'John',
        'bioregion_name': 'East Africa Bioregion',
        'dashboard_url': 'https://www.ubec.network/dashboard',
        'unsubscribe_url': 'https://www.ubec.network/unsubscribe'
    }
)
```

### Check Queue Status

```python
stats = await email_service.get_queue_status()
print(f"Pending: {stats['pending']}")
print(f"Sent: {stats['sent']}")
print(f"Failed: {stats['failed']}")
```

---

## Step 8: Create Additional Email Templates

### Bioregion Application Approved

```bash
cat > /srv/ubec-www/email_templates/bioregion_approved.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Bioregion Application Approved</title>
</head>
<body style="font-family: sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
    <h1 style="color: #4A90E2;">🎉 Bioregion Application Approved!</h1>
    
    <p>Hello {{ organizer_name }},</p>
    
    <p>Congratulations! Your bioregion application for <strong>{{ bioregion_name }}</strong> has been approved.</p>
    
    <h3>Bioregion Details:</h3>
    <ul>
        <li><strong>Name:</strong> {{ bioregion_name }}</li>
        <li><strong>Location:</strong> {{ location }}</li>
        <li><strong>Area:</strong> {{ area_sqkm }} km²</li>
        <li><strong>Founding Members:</strong> {{ member_count }}</li>
    </ul>
    
    <h3>Next Steps:</h3>
    <ol>
        <li>Set up your bioregion profile</li>
        <li>Invite Community Activators</li>
        <li>Schedule your first gathering</li>
        <li>Begin token circulation</li>
    </ol>
    
    <p><a href="{{ bioregion_url }}" style="display: inline-block; padding: 12px 24px; background: #4A90E2; color: white; text-decoration: none; border-radius: 4px;">Access Your Bioregion</a></p>
    
    <p>With Ubuntu,<br>The UBEC Protocol Team</p>
</body>
</html>
EOF
```

### Ubuntu Score Alert

```bash
cat > /srv/ubec-www/email_templates/score_alert.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Ubuntu Score Alert</title>
</head>
<body style="font-family: sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
    <h1 style="color: #FF5722;">⚠️ Ubuntu Score Alert</h1>
    
    <p>Hello {{ name }},</p>
    
    <p>Your Ubuntu principle score for <strong>{{ principle }}</strong> has dropped below the threshold.</p>
    
    <div style="background: #FFF3E0; padding: 15px; border-radius: 8px; margin: 20px 0;">
        <p><strong>Current Score:</strong> {{ current_score }}</p>
        <p><strong>Threshold:</strong> {{ threshold }}</p>
        <p><strong>Status:</strong> <span style="color: #FF5722;">Needs Attention</span></p>
    </div>
    
    <h3>Recommended Actions:</h3>
    <ul>
        <li>Review your recent transactions</li>
        <li>Engage more with your bioregion community</li>
        <li>Participate in upcoming events</li>
        <li>Connect with a Community Activator for guidance</li>
    </ul>
    
    <p><a href="{{ dashboard_url }}" style="display: inline-block; padding: 12px 24px; background: #4A90E2; color: white; text-decoration: none; border-radius: 4px;">View Dashboard</a></p>
    
    <p>Remember: "I am because we are"</p>
    
    <p>With Ubuntu,<br>The UBEC Protocol Team</p>
</body>
</html>
EOF
```

---

## Step 9: Monitoring & Maintenance

### View Email Queue

```sql
-- Connect to database
sudo -u postgres psql -d ubec

-- View pending emails
SELECT id, recipient_email, subject, status, retry_count, created_at
FROM ubec_main.email_queue
WHERE status = 'pending'
ORDER BY priority ASC, created_at ASC;

-- View failed emails
SELECT id, recipient_email, subject, error_message, retry_count
FROM ubec_main.email_queue
WHERE status = 'failed';

-- View queue summary
SELECT * FROM ubec_main.email_queue_summary;

-- Check rate limits
SELECT recipient_email, email_count, window_start, last_email_at
FROM ubec_main.email_rate_limits
ORDER BY last_email_at DESC;
```

### Clean Up Old Emails

```sql
-- Delete sent emails older than 30 days
DELETE FROM ubec_main.email_queue
WHERE status = 'sent'
AND sent_at < NOW() - INTERVAL '30 days';

-- Archive failed emails older than 7 days
DELETE FROM ubec_main.email_queue
WHERE status = 'failed'
AND updated_at < NOW() - INTERVAL '7 days';
```

---

## Troubleshooting

### Problem: Emails Not Sending

**Check 1: SMTP Configuration**
```bash
# Test SMTP connection manually
python3 << EOF
import asyncio
import aiosmtplib
import os

async def test():
    smtp = aiosmtplib.SMTP(
        hostname=os.getenv('SMTP_HOST'),
        port=int(os.getenv('SMTP_PORT')),
        use_tls=True
    )
    await smtp.connect()
    await smtp.login(os.getenv('SMTP_USERNAME'), os.getenv('SMTP_PASSWORD'))
    print("✓ SMTP connection successful")
    await smtp.quit()

asyncio.run(test())
EOF
```

**Check 2: Queue Processor Running**
```sql
-- Check if queue is being processed
SELECT * FROM ubec_main.email_queue_summary;

-- If pending count is not decreasing, check logs
```

**Check 3: Review Error Messages**
```sql
SELECT error_message, COUNT(*) 
FROM ubec_main.email_queue 
WHERE status = 'failed'
GROUP BY error_message;
```

### Problem: Rate Limit Errors

```sql
-- Reset rate limits for a specific recipient
DELETE FROM ubec_main.email_rate_limits
WHERE recipient_email = 'user@example.com';

-- Or increase the limit in code (modify _rate_limit_per_hour)
```

### Problem: Templates Not Found

```bash
# Verify template directory and files exist
ls -la /srv/ubec-www/email_templates/

# Check permissions
ls -la /srv/ubec-www/email_templates/*.html

# Should be readable by the user running the UBEC service
```

---

## Security Best Practices

1. **Never commit SMTP credentials to git**
   ```bash
   # Add to .gitignore
   echo ".env" >> .gitignore
   ```

2. **Use app-specific passwords** (for Gmail)

3. **Rotate credentials regularly** (quarterly minimum)

4. **Use TLS/SSL** (always set SMTP_USE_TLS=true)

5. **Implement unsubscribe functionality** (required by law in many jurisdictions)

6. **Monitor bounce rates** (high bounce rate = bad sender reputation)

7. **Rate limiting** (already built into the service)

---

## Production Checklist

- [ ] SMTP credentials configured in .env
- [ ] Database schema created
- [ ] Email service registered in service registry
- [ ] Templates created and tested
- [ ] Test email sent successfully
- [ ] Queue processor running
- [ ] Monitoring queries saved
- [ ] Cleanup cron job scheduled
- [ ] Backup strategy for email_queue table
- [ ] Unsubscribe functionality implemented
- [ ] GDPR compliance reviewed (if applicable)

---

## Support

If you need help:
1. Check the logs: `tail -f /var/log/ubec/application.log`
2. Review queue status in database
3. Test SMTP connection manually
4. Contact UBEC technical support

---

**This implementation follows all 12 UBEC Design Principles and is production-ready.**
