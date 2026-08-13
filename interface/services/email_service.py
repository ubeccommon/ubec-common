"""
UBEC Protocol - Email Service
==============================

Handles all email notifications for the UBEC application system.
Uses SMTP with SSL/TLS for secure email delivery.

Configuration via environment variables:
    SMTP_HOST        - SMTP server hostname
    SMTP_PORT        - SMTP server port (465 for SSL, 587 for TLS)
    SMTP_USERNAME    - SMTP authentication username
    SMTP_PASSWORD    - SMTP authentication password
    SMTP_USE_TLS     - Use TLS/SSL (true/false)
    SMTP_FROM_EMAIL  - Sender email address
    SMTP_FROM_NAME   - Sender display name
    ADMIN_EMAIL      - Admin notification recipient

Usage:
    from services.email_service import send_confirmation_email, send_admin_notification
    
    # Send applicant confirmation
    send_confirmation_email("farmer", "FRM-2025-0001", "John Doe", "john@example.com", submitted_at)
    
    # Send admin notification
    send_admin_notification("farmer", "FRM-2025-0001", "John Doe", "john@example.com", "Berlin", 5000)

Attribution:
    This project uses the services of Claude and Anthropic PBC to inform 
    our decisions and recommendations.
"""

import os
import ssl
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from datetime import datetime

logger = logging.getLogger(__name__)


# =============================================================================
# Configuration
# =============================================================================

SMTP_CONFIG = {
    "host": os.getenv("SMTP_HOST", ""),
    "port": int(os.getenv("SMTP_PORT", "465")),
    "username": os.getenv("SMTP_USERNAME", ""),
    "password": os.getenv("SMTP_PASSWORD", ""),
    "use_ssl": os.getenv("SMTP_USE_TLS", "true").lower() == "true",
    "from_email": os.getenv("SMTP_FROM_EMAIL", ""),
    "from_name": os.getenv("SMTP_FROM_NAME", "UBEC DAO Protocol"),
}

ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "stewardship@ubec.network")


# =============================================================================
# Helper Constants
# =============================================================================

APPLICATION_TYPE_LABELS = {
    "farmer": "Farmer",
    "community": "Community", 
    "activator": "Community Activator",
    "livinglab": "Living Lab"
}

APPLICATION_TYPE_ICONS = {
    "farmer": "🌱",
    "community": "🏘️",
    "activator": "🔄",
    "livinglab": "🔬"
}

REVIEW_TIMELINES = {
    "farmer": "14-30 days",
    "community": "60-90 days",
    "activator": "45-75 days",
    "livinglab": "30-60 days"
}


# =============================================================================
# Core Functions
# =============================================================================

def is_email_configured() -> bool:
    """Check if email is properly configured."""
    return bool(
        SMTP_CONFIG["host"] and 
        SMTP_CONFIG["username"] and 
        SMTP_CONFIG["password"] and
        SMTP_CONFIG["from_email"]
    )


def send_email(
    to_email: str,
    subject: str,
    html_body: str,
    text_body: Optional[str] = None
) -> bool:
    """
    Send an email via SMTP with SSL support.
    
    Handles both:
    - Port 465: SSL from start (SMTP_SSL)
    - Port 587: STARTTLS upgrade
    
    Args:
        to_email: Recipient email address
        subject: Email subject line
        html_body: HTML content of email
        text_body: Plain text fallback (optional)
    
    Returns:
        True if sent successfully, False otherwise
    """
    if not is_email_configured():
        logger.warning("Email not configured - skipping send")
        return False
    
    try:
        # Create message
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{SMTP_CONFIG['from_name']} <{SMTP_CONFIG['from_email']}>"
        msg["To"] = to_email
        
        # Add plain text version
        if text_body:
            msg.attach(MIMEText(text_body, "plain"))
        
        # Add HTML version
        msg.attach(MIMEText(html_body, "html"))
        
        # Connect and send based on port
        port = SMTP_CONFIG["port"]
        
        if port == 465:
            # SSL connection (port 465)
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(
                SMTP_CONFIG["host"], 
                port, 
                context=context
            ) as server:
                server.login(SMTP_CONFIG["username"], SMTP_CONFIG["password"])
                server.send_message(msg)
        else:
            # STARTTLS connection (port 587 or others)
            with smtplib.SMTP(SMTP_CONFIG["host"], port) as server:
                if SMTP_CONFIG["use_ssl"]:
                    server.starttls()
                server.login(SMTP_CONFIG["username"], SMTP_CONFIG["password"])
                server.send_message(msg)
        
        logger.info(f"Email sent successfully to {to_email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {e}")
        return False


# =============================================================================
# Application Email Functions
# =============================================================================

def send_confirmation_email(
    app_type: str,
    reference_number: str,
    contact_name: str,
    contact_email: str,
    submitted_at: datetime
) -> bool:
    """
    Send confirmation email to applicant.
    
    Args:
        app_type: Application type (farmer, community, activator, livinglab)
        reference_number: Application reference number
        contact_name: Applicant's name
        contact_email: Applicant's email
        submitted_at: Submission timestamp
    
    Returns:
        True if sent successfully, False otherwise
    """
    type_label = APPLICATION_TYPE_LABELS.get(app_type, app_type.title())
    type_icon = APPLICATION_TYPE_ICONS.get(app_type, "📋")
    timeline = REVIEW_TIMELINES.get(app_type, "60 days")
    
    subject = f"Application Received - {reference_number}"
    
    html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #2c3e50; margin: 0; padding: 0; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #8BC34A 0%, #689F38 100%); color: white; padding: 30px; text-align: center; border-radius: 12px 12px 0 0; }}
        .header h1 {{ margin: 0; font-size: 24px; color: white; }}
        .content {{ background: #f8f9fa; padding: 30px; border: 1px solid #e2e8f0; }}
        .reference-box {{ background: white; border: 2px solid #8BC34A; border-radius: 8px; padding: 20px; text-align: center; margin: 20px 0; }}
        .reference-number {{ font-size: 28px; font-weight: bold; color: #689F38; letter-spacing: 2px; font-family: monospace; }}
        .details {{ background: white; border-radius: 8px; padding: 15px; margin: 20px 0; }}
        .details p {{ margin: 8px 0; }}
        .footer {{ text-align: center; padding: 20px; color: #718096; font-size: 14px; }}
        .next-steps {{ background: white; border-radius: 8px; padding: 20px; margin: 20px 0; }}
        .next-steps h3 {{ margin-top: 0; color: #2c3e50; }}
        .next-steps ol {{ padding-left: 20px; }}
        .next-steps li {{ margin: 10px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{type_icon} UBEC {type_label} Application</h1>
            <p style="margin: 10px 0 0 0; opacity: 0.9;">Thank you for applying!</p>
        </div>
        <div class="content">
            <p>Dear {contact_name},</p>
            
            <p>Thank you for submitting your <strong>{type_label}</strong> application to the Ubuntu Bioregional Economic Commons (UBEC) Protocol Network.</p>
            
            <div class="reference-box">
                <p style="margin: 0 0 10px 0; color: #718096; font-size: 14px;">Your Reference Number</p>
                <div class="reference-number">{reference_number}</div>
            </div>
            
            <p><strong>Please save this reference number.</strong> You will need it for any correspondence about your application.</p>
            
            <div class="details">
                <p><strong>Application Type:</strong> {type_label}</p>
                <p><strong>Submitted:</strong> {submitted_at.strftime('%B %d, %Y at %H:%M UTC')}</p>
                <p><strong>Status:</strong> Pending Review</p>
            </div>
            
            <div class="next-steps">
                <h3>What Happens Next?</h3>
                <ol>
                    <li><strong>Review:</strong> Our stewardship team will review your application within <strong>{timeline}</strong>.</li>
                    <li><strong>Validation:</strong> We may contact your references for verification.</li>
                    <li><strong>Decision:</strong> You'll receive an email with our decision and next steps.</li>
                </ol>
            </div>
            
            <p>If you have any questions, please contact us at <a href="mailto:stewardship@ubec.network">stewardship@ubec.network</a>.</p>
            
            <p style="margin-top: 30px;">
                With gratitude,<br>
                <strong>The UBEC Stewardship Team</strong>
            </p>
        </div>
        <div class="footer">
            <p><em>"I am because we are"</em> — Ubuntu Philosophy</p>
            <p>Ubuntu Bioregional Economic Commons<br>
            <a href="https://bioregional.ubec.network">bioregional.ubec.network</a></p>
        </div>
    </div>
</body>
</html>
"""
    
    text_body = f"""
UBEC {type_label} Application Received

Dear {contact_name},

Thank you for submitting your {type_label} application to the Ubuntu Bioregional Economic Commons (UBEC) Protocol Network.

YOUR REFERENCE NUMBER: {reference_number}

Please save this reference number for any correspondence.

Application Details:
- Type: {type_label}
- Submitted: {submitted_at.strftime('%B %d, %Y at %H:%M UTC')}
- Status: Pending Review

What Happens Next?
1. Review: Our stewardship team will review your application within {timeline}.
2. Validation: We may contact your references.
3. Decision: You'll receive an email with our decision.

Questions? Contact us at stewardship@ubec.network

With gratitude,
The UBEC Stewardship Team

---
"I am because we are" — Ubuntu Philosophy
Ubuntu Bioregional Economic Commons
https://bioregional.ubec.network
"""
    
    return send_email(contact_email, subject, html_body, text_body)


def send_admin_notification(
    app_type: str,
    reference_number: str,
    contact_name: str,
    contact_email: str,
    location: str,
    requested_amount: int,
    organization_name: Optional[str] = None
) -> bool:
    """
    Send notification email to admin about new application.
    
    Args:
        app_type: Application type
        reference_number: Application reference number
        contact_name: Applicant's name
        contact_email: Applicant's email
        location: Applicant's location
        requested_amount: Requested token amount
        organization_name: Organization name (optional)
    
    Returns:
        True if sent successfully, False otherwise
    """
    type_label = f"{APPLICATION_TYPE_ICONS.get(app_type, '📋')} {APPLICATION_TYPE_LABELS.get(app_type, app_type.title())}"
    
    subject = f"New {APPLICATION_TYPE_LABELS.get(app_type, app_type.title())} Application - {reference_number}"
    
    html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #2c3e50; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: #2c3e50; color: white; padding: 20px; border-radius: 8px 8px 0 0; }}
        .header h2 {{ margin: 0; }}
        .content {{ background: #f8f9fa; padding: 20px; border: 1px solid #e2e8f0; }}
        .badge {{ display: inline-block; background: #8BC34A; color: white; padding: 4px 12px; border-radius: 20px; font-size: 14px; }}
        .details {{ background: white; border-radius: 8px; padding: 15px; margin: 15px 0; }}
        .details p {{ margin: 8px 0; }}
        .amount {{ font-size: 24px; font-weight: bold; color: #689F38; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h2>{type_label} Application</h2>
        </div>
        <div class="content">
            <p>A new application has been submitted to the UBEC Protocol Network.</p>
            
            <div class="details">
                <p><strong>📋 Reference:</strong> {reference_number}</p>
                <p><strong>👤 Applicant:</strong> {contact_name}</p>
                <p><strong>📧 Email:</strong> <a href="mailto:{contact_email}">{contact_email}</a></p>
                <p><strong>📍 Location:</strong> {location}</p>
                {f'<p><strong>🏢 Organization:</strong> {organization_name}</p>' if organization_name else ''}
                <p><strong>💰 Request:</strong> <span class="amount">{requested_amount:,} UBEC</span></p>
                <p><strong>🕐 Submitted:</strong> {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}</p>
            </div>
            
            <p>Log in to the admin panel to review this application.</p>
        </div>
    </div>
</body>
</html>
"""
    
    text_body = f"""
New {APPLICATION_TYPE_LABELS.get(app_type, app_type.title())} Application - {reference_number}

A new application has been submitted:

Reference: {reference_number}
Applicant: {contact_name}
Email: {contact_email}
Location: {location}
{f'Organization: {organization_name}' if organization_name else ''}
Request: {requested_amount:,} UBEC
Submitted: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}
"""
    
    return send_email(ADMIN_EMAIL, subject, html_body, text_body)


def send_status_update_email(
    app_type: str,
    reference_number: str,
    contact_name: str,
    contact_email: str,
    new_status: str,
    message: Optional[str] = None
) -> bool:
    """
    Send status update email to applicant.
    
    Args:
        app_type: Application type
        reference_number: Application reference number
        contact_name: Applicant's name
        contact_email: Applicant's email
        new_status: New application status
        message: Optional custom message
    
    Returns:
        True if sent successfully, False otherwise
    """
    type_label = APPLICATION_TYPE_LABELS.get(app_type, app_type.title())
    
    status_colors = {
        "approved": "#689F38",
        "rejected": "#c53030",
        "under_review": "#3182ce",
        "pending": "#718096"
    }
    status_color = status_colors.get(new_status, "#718096")
    
    subject = f"Application Update - {reference_number}"
    
    html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #2c3e50; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #8BC34A 0%, #689F38 100%); color: white; padding: 30px; text-align: center; border-radius: 12px 12px 0 0; }}
        .content {{ background: #f8f9fa; padding: 30px; border: 1px solid #e2e8f0; }}
        .status-badge {{ display: inline-block; background: {status_color}; color: white; padding: 8px 20px; border-radius: 20px; font-weight: bold; text-transform: uppercase; }}
        .footer {{ text-align: center; padding: 20px; color: #718096; font-size: 14px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Application Status Update</h1>
        </div>
        <div class="content">
            <p>Dear {contact_name},</p>
            
            <p>There has been an update to your <strong>{type_label}</strong> application.</p>
            
            <p><strong>Reference:</strong> {reference_number}</p>
            <p><strong>New Status:</strong> <span class="status-badge">{new_status.replace('_', ' ').title()}</span></p>
            
            {f'<p><strong>Message:</strong></p><p>{message}</p>' if message else ''}
            
            <p>If you have questions, contact <a href="mailto:stewardship@ubec.network">stewardship@ubec.network</a>.</p>
            
            <p style="margin-top: 30px;">
                With gratitude,<br>
                <strong>The UBEC Stewardship Team</strong>
            </p>
        </div>
        <div class="footer">
            <p><em>"I am because we are"</em> — Ubuntu Philosophy</p>
        </div>
    </div>
</body>
</html>
"""
    
    text_body = f"""
Application Status Update - {reference_number}

Dear {contact_name},

There has been an update to your {type_label} application.

Reference: {reference_number}
New Status: {new_status.replace('_', ' ').title()}

{f'Message: {message}' if message else ''}

Questions? Contact stewardship@ubec.network

With gratitude,
The UBEC Stewardship Team
"""
    
    return send_email(contact_email, subject, html_body, text_body)
