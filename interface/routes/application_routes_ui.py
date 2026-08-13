"""
UBEC Protocol - Application API Routes (UI Database Version)
=============================================================

API endpoints for receiving and managing beneficiary applications.
Stores applications in PostgreSQL (ubec_ui schema) and sends email notifications.

Database: ubec_ui_interface
Schema: ubec_ui

Endpoints:
    POST /api/v1/applications/farmer     - Submit farmer application
    POST /api/v1/applications/community  - Submit community application
    POST /api/v1/applications/activator  - Submit activator application
    POST /api/v1/applications/livinglab  - Submit living lab application
    GET  /api/v1/applications            - List all applications (admin)
    GET  /api/v1/applications/{ref}      - Get application by reference

Attribution:
    This project uses the services of Claude and Anthropic PBC to inform 
    our decisions and recommendations.
"""

import logging
import json
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Optional, List

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, EmailStr, Field, validator

# Import from our UI database module
from database.ui_db_connection import get_db_connection, get_db_transaction

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/applications", tags=["applications"])


# =============================================================================
# Configuration
# =============================================================================

EMAIL_CONFIG = {
    "smtp_host": os.getenv('SMTP_HOST', 'smtp.gmail.com'),
    "smtp_port": int(os.getenv('SMTP_PORT', '587')),
    "smtp_user": os.getenv('SMTP_USER', ''),
    "smtp_password": os.getenv('SMTP_PASSWORD', ''),
    "from_email": os.getenv('FROM_EMAIL', 'noreply@ubec.network'),
    "admin_email": os.getenv('ADMIN_EMAIL', 'applications@ubec.network'),
}


# =============================================================================
# Pydantic Models
# =============================================================================

class ApplicationBase(BaseModel):
    """Base fields common to all applications."""
    contact_email: EmailStr
    contact_phone: Optional[str] = None
    location: str = Field(..., min_length=2, max_length=255)
    requested_amount: int = Field(..., gt=0)
    ubuntu_alignment: str = Field(..., min_length=20)
    agree_terms: bool
    agree_values: bool
    reference1_name: str = Field(..., min_length=2)
    reference1_contact: str = Field(..., min_length=5)
    reference2_name: Optional[str] = None
    reference2_contact: Optional[str] = None


class FarmerApplicationCreate(ApplicationBase):
    """Schema for farmer application."""
    name: str = Field(..., min_length=2, max_length=255)
    farm_name: Optional[str] = None
    farm_size: str = Field(..., min_length=1)
    products: str = Field(..., min_length=10)
    regenerative_practices: str = Field(..., min_length=20)
    experience: str
    token_usage: str = Field(..., min_length=20)
    expected_impact: str = Field(..., min_length=20)
    community_connections: str = Field(..., min_length=10)
    
    @validator('requested_amount')
    def validate_amount(cls, v):
        if v < 1000 or v > 50000:
            raise ValueError('Amount must be between 1,000 and 50,000 UBEC')
        return v


class CommunityApplicationCreate(ApplicationBase):
    """Schema for community application."""
    contact_name: str = Field(..., min_length=2, max_length=255)
    contact_role: str = Field(..., min_length=2)
    organization_name: str = Field(..., min_length=2, max_length=255)
    organization_type: str
    member_count: int = Field(..., ge=3)
    mission: str = Field(..., min_length=20)
    current_activities: str = Field(..., min_length=20)
    governance_structure: str = Field(..., min_length=10)
    token_usage: str = Field(..., min_length=20)
    expected_impact: str = Field(..., min_length=20)
    regenerative_practices: str = Field(..., min_length=10)
    
    @validator('requested_amount')
    def validate_amount(cls, v):
        if v < 10000 or v > 200000:
            raise ValueError('Amount must be between 10,000 and 200,000 UBEC')
        return v


class ActivatorApplicationCreate(ApplicationBase):
    """Schema for activator application."""
    name: str = Field(..., min_length=2, max_length=255)
    affiliation: Optional[str] = None
    background: str = Field(..., min_length=20)
    skills: str = Field(..., min_length=20)
    track_record: str = Field(..., min_length=20)
    networks: str = Field(..., min_length=10)
    proposed_services: str = Field(..., min_length=20)
    geographic_scope: str = Field(..., min_length=5)
    time_commitment: str
    year1_plan: str = Field(..., min_length=50)
    budget_breakdown: str = Field(..., min_length=20)
    facilitation_philosophy: str = Field(..., min_length=20)
    
    @validator('requested_amount')
    def validate_amount(cls, v):
        if v < 20000 or v > 100000:
            raise ValueError('Amount must be between 20,000 and 100,000 UBEC')
        return v


class LivingLabApplicationCreate(ApplicationBase):
    """Schema for living lab application."""
    contact_name: str = Field(..., min_length=2, max_length=255)
    contact_role: str = Field(..., min_length=2)
    institution_name: str = Field(..., min_length=2, max_length=255)
    institution_type: str
    student_count: int = Field(..., ge=10)
    land_area: str = Field(..., min_length=1)
    ecosystem_types: str = Field(..., min_length=3)
    site_description: str = Field(..., min_length=20)
    infrastructure: str = Field(..., min_length=10)
    current_curriculum: str = Field(..., min_length=20)
    integration_plan: str = Field(..., min_length=20)
    citizen_science: str = Field(..., min_length=10)
    technical_support: str = Field(..., min_length=10)
    sensors: List[str] = Field(..., min_items=1)
    budget_breakdown: str = Field(..., min_length=20)
    community_access: str = Field(..., min_length=10)
    
    @validator('requested_amount')
    def validate_amount(cls, v):
        if v < 5000 or v > 25000:
            raise ValueError('Amount must be between 5,000 and 25,000 UBEC')
        return v


class ApplicationResponse(BaseModel):
    """Response after submission."""
    success: bool
    message: str
    reference_number: str
    application_type: str
    submitted_at: datetime


class ApplicationListItem(BaseModel):
    """Summary for listing."""
    id: int
    reference_number: str
    application_type: str
    status: str
    contact_name: str
    contact_email: str
    location: str
    requested_amount: int
    submitted_at: datetime


# =============================================================================
# Helper Functions
# =============================================================================

async def store_application(
    app_type: str,
    data: dict,
    contact_name: str,
    contact_email: str,
    contact_phone: Optional[str],
    location: str,
    requested_amount: int,
    organization_name: Optional[str] = None,
    organization_type: Optional[str] = None
) -> dict:
    """Store application in database."""
    
    async with get_db_transaction() as conn:
        # Generate reference number
        reference_number = await conn.fetchval(
            "SELECT ubec_ui.generate_application_reference($1)",
            app_type
        )
        
        # Prepare references
        references = []
        if data.get('reference1_name'):
            references.append({
                "name": data.get('reference1_name'),
                "contact": data.get('reference1_contact')
            })
        if data.get('reference2_name'):
            references.append({
                "name": data.get('reference2_name'),
                "contact": data.get('reference2_contact')
            })
        
        # Filter out non-data fields
        exclude_fields = {
            'contact_name', 'contact_email', 'contact_phone', 'location',
            'requested_amount', 'organization_name', 'organization_type',
            'agree_terms', 'agree_values', 'application_type', 'name',
            'email', 'phone', 'reference1_name', 'reference1_contact',
            'reference2_name', 'reference2_contact', 'contact_role',
            'institution_name', 'institution_type'
        }
        app_data = {k: v for k, v in data.items() if k not in exclude_fields}
        
        # Insert application
        result = await conn.fetchrow("""
            INSERT INTO ubec_ui.applications (
                application_type, reference_number, contact_name, contact_email,
                contact_phone, location, organization_name, organization_type,
                application_data, requested_amount, applicant_references,
                agreed_terms, agreed_values
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
            RETURNING id, reference_number, submitted_at
        """,
            app_type, reference_number, contact_name, contact_email,
            contact_phone, location, organization_name, organization_type,
            json.dumps(app_data), requested_amount, json.dumps(references),
            data.get('agree_terms', False), data.get('agree_values', False)
        )
        
        # Log activity
        await conn.execute("""
            INSERT INTO ubec_ui.activity_log (action, entity_type, entity_id, details)
            VALUES ($1, $2, $3, $4)
        """, 'application_submitted', 'application', result['id'],
            json.dumps({'type': app_type, 'email': contact_email}))
        
        return {
            "id": result['id'],
            "reference_number": result['reference_number'],
            "submitted_at": result['submitted_at']
        }


def send_notification_email(
    app_type: str,
    reference_number: str,
    contact_name: str,
    contact_email: str,
    location: str,
    requested_amount: int,
    organization_name: Optional[str] = None
) -> bool:
    """Send email notification to admin."""
    
    if not EMAIL_CONFIG['smtp_user']:
        logger.warning("SMTP not configured - skipping notification email")
        return False
    
    try:
        type_labels = {
            'farmer': '🌾 Farmer',
            'community': '🏘️ Community',
            'activator': '🔄 Community Activator',
            'livinglab': '🎓 Living Lab'
        }
        type_label = type_labels.get(app_type, app_type.title())
        
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"New UBEC Application: {reference_number} ({type_label})"
        msg['From'] = EMAIL_CONFIG['from_email']
        msg['To'] = EMAIL_CONFIG['admin_email']
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #8BC34A 0%, #87CEEB 100%); padding: 20px; border-radius: 8px 8px 0 0; }}
        .header h1 {{ color: #2c3e50; margin: 0; }}
        .content {{ background: #f9f9f9; padding: 20px; border-radius: 0 0 8px 8px; }}
        .badge {{ background: #667eea; color: white; padding: 4px 12px; border-radius: 20px; font-size: 14px; }}
        .details {{ background: white; padding: 15px; border-radius: 8px; margin: 15px 0; }}
        .amount {{ font-size: 24px; font-weight: bold; color: #2e7d32; }}
        .button {{ display: inline-block; background: #667eea; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header"><h1>New UBEC Application</h1></div>
        <div class="content">
            <p><span class="badge">{type_label}</span></p>
            <p><strong>Reference:</strong> {reference_number}</p>
            <p><strong>Submitted:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}</p>
            <div class="details">
                <p><strong>👤 Applicant:</strong> {contact_name}</p>
                <p><strong>📧 Email:</strong> <a href="mailto:{contact_email}">{contact_email}</a></p>
                <p><strong>📍 Location:</strong> {location}</p>
                {f'<p><strong>🏢 Organization:</strong> {organization_name}</p>' if organization_name else ''}
            </div>
            <p><strong>Token Request:</strong></p>
            <p class="amount">{requested_amount:,} UBEC</p>
            <a href="https://bioregional.ubec.network/admin/applications/{reference_number}" class="button">Review Application →</a>
        </div>
    </div>
</body>
</html>
        """
        
        msg.attach(MIMEText(html_content, 'html'))
        
        with smtplib.SMTP(EMAIL_CONFIG['smtp_host'], EMAIL_CONFIG['smtp_port']) as server:
            server.starttls()
            server.login(EMAIL_CONFIG['smtp_user'], EMAIL_CONFIG['smtp_password'])
            server.send_message(msg)
        
        logger.info(f"Admin notification sent for {reference_number}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send admin notification: {e}")
        return False


def send_confirmation_email(
    app_type: str,
    reference_number: str,
    contact_name: str,
    contact_email: str,
    requested_amount: int
) -> bool:
    """Send confirmation email to applicant."""
    
    if not EMAIL_CONFIG['smtp_user']:
        logger.warning("SMTP not configured - skipping confirmation email")
        return False
    
    try:
        type_labels = {
            'farmer': 'Farmer', 'community': 'Community',
            'activator': 'Community Activator', 'livinglab': 'Living Lab'
        }
        timelines = {
            'farmer': '30-60 days', 'community': '60-90 days',
            'activator': '45-75 days', 'livinglab': '45-60 days'
        }
        
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"UBEC Application Received: {reference_number}"
        msg['From'] = EMAIL_CONFIG['from_email']
        msg['To'] = contact_email
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #8BC34A 0%, #87CEEB 100%); padding: 30px 20px; border-radius: 8px 8px 0 0; text-align: center; }}
        .header h1 {{ color: #2c3e50; margin: 0 0 10px 0; }}
        .content {{ background: #f9f9f9; padding: 30px 20px; }}
        .ref-box {{ background: white; border: 2px solid #8BC34A; border-radius: 8px; padding: 15px; text-align: center; margin: 20px 0; }}
        .ref-box .ref {{ font-size: 24px; font-weight: bold; color: #2c3e50; font-family: monospace; }}
        .next-steps {{ background: white; padding: 20px; border-radius: 8px; }}
        .footer {{ text-align: center; padding: 20px; color: #666; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Application Received!</h1>
            <p style="color: #2c3e50; opacity: 0.8;">Thank you for applying to UBEC Protocol</p>
        </div>
        <div class="content">
            <p>Dear {contact_name},</p>
            <p>We have received your <strong>{type_labels.get(app_type, app_type.title())}</strong> application.</p>
            <div class="ref-box">
                <div style="font-size: 12px; color: #666;">YOUR REFERENCE NUMBER</div>
                <div class="ref">{reference_number}</div>
            </div>
            <div class="next-steps">
                <h3>What Happens Next?</h3>
                <ol>
                    <li><strong>Review:</strong> Our committee will review your application within {timelines.get(app_type, '60 days')}.</li>
                    <li><strong>Validation:</strong> We may contact your references.</li>
                    <li><strong>Decision:</strong> You'll receive an email with our decision.</li>
                </ol>
            </div>
            <p>Questions? Contact <a href="mailto:applications@ubec.network">applications@ubec.network</a></p>
            <p><em>"I am because we are"</em> — Ubuntu</p>
        </div>
        <div class="footer">
            Ubuntu Bioregional Economic Commons<br>
            <a href="https://bioregional.ubec.network">bioregional.ubec.network</a>
        </div>
    </div>
</body>
</html>
        """
        
        msg.attach(MIMEText(html_content, 'html'))
        
        with smtplib.SMTP(EMAIL_CONFIG['smtp_host'], EMAIL_CONFIG['smtp_port']) as server:
            server.starttls()
            server.login(EMAIL_CONFIG['smtp_user'], EMAIL_CONFIG['smtp_password'])
            server.send_message(msg)
        
        logger.info(f"Confirmation sent to {contact_email} for {reference_number}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send confirmation: {e}")
        return False


async def log_email(
    recipient: str,
    email_type: str,
    subject: str,
    ref_type: str,
    ref_id: int,
    status: str = 'sent'
):
    """Log sent email to database."""
    try:
        async with get_db_connection() as conn:
            await conn.execute("""
                INSERT INTO ubec_ui.email_log 
                (recipient_email, email_type, subject, reference_type, reference_id, status)
                VALUES ($1, $2, $3, $4, $5, $6)
            """, recipient, email_type, subject, ref_type, ref_id, status)
    except Exception as e:
        logger.warning(f"Failed to log email: {e}")


# =============================================================================
# Application Submission Endpoints
# =============================================================================

@router.post("/farmer", response_model=ApplicationResponse)
async def submit_farmer_application(application: FarmerApplicationCreate):
    """Submit a farmer application."""
    try:
        result = await store_application(
            app_type="farmer",
            data=application.dict(),
            contact_name=application.name,
            contact_email=application.contact_email,
            contact_phone=application.contact_phone,
            location=application.location,
            requested_amount=application.requested_amount
        )
        
        # Send emails
        send_notification_email(
            "farmer", result['reference_number'], application.name,
            application.contact_email, application.location,
            application.requested_amount
        )
        send_confirmation_email(
            "farmer", result['reference_number'], application.name,
            application.contact_email, application.requested_amount
        )
        
        await log_email(
            application.contact_email, 'confirmation',
            f"UBEC Application Received: {result['reference_number']}",
            'application', result['id']
        )
        
        return ApplicationResponse(
            success=True,
            message="Your farmer application has been submitted successfully.",
            reference_number=result['reference_number'],
            application_type="farmer",
            submitted_at=result['submitted_at']
        )
        
    except Exception as e:
        logger.error(f"Farmer application error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/community", response_model=ApplicationResponse)
async def submit_community_application(application: CommunityApplicationCreate):
    """Submit a community application."""
    try:
        result = await store_application(
            app_type="community",
            data=application.dict(),
            contact_name=application.contact_name,
            contact_email=application.contact_email,
            contact_phone=application.contact_phone,
            location=application.location,
            requested_amount=application.requested_amount,
            organization_name=application.organization_name,
            organization_type=application.organization_type
        )
        
        send_notification_email(
            "community", result['reference_number'], application.contact_name,
            application.contact_email, application.location,
            application.requested_amount, application.organization_name
        )
        send_confirmation_email(
            "community", result['reference_number'], application.contact_name,
            application.contact_email, application.requested_amount
        )
        
        await log_email(
            application.contact_email, 'confirmation',
            f"UBEC Application Received: {result['reference_number']}",
            'application', result['id']
        )
        
        return ApplicationResponse(
            success=True,
            message="Your community application has been submitted successfully.",
            reference_number=result['reference_number'],
            application_type="community",
            submitted_at=result['submitted_at']
        )
        
    except Exception as e:
        logger.error(f"Community application error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/activator", response_model=ApplicationResponse)
async def submit_activator_application(application: ActivatorApplicationCreate):
    """Submit a community activator application."""
    try:
        result = await store_application(
            app_type="activator",
            data=application.dict(),
            contact_name=application.name,
            contact_email=application.contact_email,
            contact_phone=application.contact_phone,
            location=application.location,
            requested_amount=application.requested_amount
        )
        
        send_notification_email(
            "activator", result['reference_number'], application.name,
            application.contact_email, application.location,
            application.requested_amount
        )
        send_confirmation_email(
            "activator", result['reference_number'], application.name,
            application.contact_email, application.requested_amount
        )
        
        await log_email(
            application.contact_email, 'confirmation',
            f"UBEC Application Received: {result['reference_number']}",
            'application', result['id']
        )
        
        return ApplicationResponse(
            success=True,
            message="Your activator application has been submitted successfully.",
            reference_number=result['reference_number'],
            application_type="activator",
            submitted_at=result['submitted_at']
        )
        
    except Exception as e:
        logger.error(f"Activator application error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/livinglab", response_model=ApplicationResponse)
async def submit_livinglab_application(application: LivingLabApplicationCreate):
    """Submit a living lab application."""
    try:
        result = await store_application(
            app_type="livinglab",
            data=application.dict(),
            contact_name=application.contact_name,
            contact_email=application.contact_email,
            contact_phone=application.contact_phone,
            location=application.location,
            requested_amount=application.requested_amount,
            organization_name=application.institution_name,
            organization_type=application.institution_type
        )
        
        send_notification_email(
            "livinglab", result['reference_number'], application.contact_name,
            application.contact_email, application.location,
            application.requested_amount, application.institution_name
        )
        send_confirmation_email(
            "livinglab", result['reference_number'], application.contact_name,
            application.contact_email, application.requested_amount
        )
        
        await log_email(
            application.contact_email, 'confirmation',
            f"UBEC Application Received: {result['reference_number']}",
            'application', result['id']
        )
        
        return ApplicationResponse(
            success=True,
            message="Your living lab application has been submitted successfully.",
            reference_number=result['reference_number'],
            application_type="livinglab",
            submitted_at=result['submitted_at']
        )
        
    except Exception as e:
        logger.error(f"Living lab application error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# Query Endpoints
# =============================================================================

@router.get("", response_model=List[ApplicationListItem])
async def list_applications(
    status: Optional[str] = Query(None),
    app_type: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0)
):
    """List applications with optional filters."""
    try:
        async with get_db_connection() as conn:
            query = """
                SELECT id, reference_number, application_type, status,
                       contact_name, contact_email, location,
                       requested_amount, submitted_at
                FROM ubec_ui.applications WHERE 1=1
            """
            params = []
            
            if status:
                params.append(status)
                query += f" AND status = ${len(params)}"
            
            if app_type:
                params.append(app_type)
                query += f" AND application_type = ${len(params)}"
            
            params.extend([limit, offset])
            query += f" ORDER BY submitted_at DESC LIMIT ${len(params)-1} OFFSET ${len(params)}"
            
            rows = await conn.fetch(query, *params)
            return [ApplicationListItem(**dict(row)) for row in rows]
            
    except Exception as e:
        logger.error(f"List applications error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/summary")
async def get_application_stats():
    """Get application statistics."""
    try:
        async with get_db_connection() as conn:
            stats = await conn.fetch("SELECT * FROM ubec_ui.application_summary")
            
            totals = await conn.fetchrow("""
                SELECT 
                    COUNT(*) as total,
                    COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending,
                    COUNT(CASE WHEN status = 'approved' THEN 1 END) as approved,
                    SUM(requested_amount) as total_requested,
                    SUM(CASE WHEN status = 'approved' THEN approved_amount ELSE 0 END) as total_approved
                FROM ubec_ui.applications
            """)
            
            return {
                "by_type_status": [dict(row) for row in stats],
                "totals": dict(totals)
            }
            
    except Exception as e:
        logger.error(f"Stats error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{reference_number}")
async def get_application(reference_number: str):
    """Get application by reference number."""
    try:
        async with get_db_connection() as conn:
            row = await conn.fetchrow("""
                SELECT * FROM ubec_ui.applications WHERE reference_number = $1
            """, reference_number)
            
            if not row:
                raise HTTPException(status_code=404, detail="Application not found")
            
            return dict(row)
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get application error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
