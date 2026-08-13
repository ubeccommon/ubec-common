"""
UBEC Protocol - Application API Routes
=======================================

API endpoints for receiving beneficiary applications.
Stores applications in PostgreSQL (ubec_ui schema) and sends email notifications.

Database: ubec_ui_interface
Schema: ubec_ui

Endpoints:
    POST /api/v1/applications/farmer     - Submit farmer application
    POST /api/v1/applications/community  - Submit community application
    POST /api/v1/applications/activator  - Submit activator application
    POST /api/v1/applications/livinglab  - Submit living lab application
    GET  /api/v1/applications/stats      - Get application statistics

Attribution:
    This project uses the services of Claude and Anthropic PBC to inform 
    our decisions and recommendations.
"""

import logging
import json
from datetime import datetime
from typing import Optional, List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr, Field, validator

from database.ui_db_connection import get_db_connection, get_db_transaction
from services.email_service import send_confirmation_email, send_admin_notification

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/applications", tags=["applications"])


# =============================================================================
# Pydantic Models
# =============================================================================

class FarmerApplicationCreate(BaseModel):
    """Schema for farmer application."""
    contact_name: str = Field(..., min_length=2, max_length=255)
    contact_email: EmailStr
    contact_phone: Optional[str] = None
    location: str = Field(..., min_length=2, max_length=255)
    farm_name: str = Field(..., min_length=2)
    farm_size: str = Field(..., min_length=1)
    farm_type: str = Field(..., min_length=2)
    years_farming: int = Field(..., ge=0)
    primary_products: str = Field(..., min_length=10)
    current_practices: str = Field(..., min_length=20)
    regeneration_goals: str = Field(..., min_length=20)
    challenges: str = Field(..., min_length=10)
    requested_amount: int = Field(..., gt=0)
    token_usage: str = Field(..., min_length=20)
    community_involvement: str = Field(..., min_length=10)
    ubuntu_alignment: str = Field(..., min_length=20)
    reference1_name: str = Field(..., min_length=2)
    reference1_contact: str = Field(..., min_length=5)
    reference2_name: Optional[str] = None
    reference2_contact: Optional[str] = None
    agree_terms: bool
    agree_values: bool
    
    @validator('requested_amount')
    def validate_amount(cls, v):
        if v < 1000 or v > 50000:
            raise ValueError('Amount must be between 1,000 and 50,000 UBEC')
        return v


class CommunityApplicationCreate(BaseModel):
    """Schema for community application."""
    contact_name: str = Field(..., min_length=2, max_length=255)
    contact_email: EmailStr
    contact_phone: Optional[str] = None
    contact_role: str = Field(..., min_length=2)
    location: str = Field(..., min_length=2, max_length=255)
    organization_name: str = Field(..., min_length=2, max_length=255)
    organization_type: str
    member_count: int = Field(..., ge=3)
    mission: str = Field(..., min_length=20)
    current_activities: str = Field(..., min_length=20)
    governance_structure: str = Field(..., min_length=10)
    requested_amount: int = Field(..., gt=0)
    token_usage: str = Field(..., min_length=20)
    expected_impact: str = Field(..., min_length=20)
    ubuntu_alignment: str = Field(..., min_length=20)
    regenerative_practices: str = Field(..., min_length=10)
    reference1_name: str = Field(..., min_length=2)
    reference1_contact: str = Field(..., min_length=5)
    reference2_name: Optional[str] = None
    reference2_contact: Optional[str] = None
    agree_terms: bool
    agree_values: bool
    
    @validator('requested_amount')
    def validate_amount(cls, v):
        if v < 10000 or v > 200000:
            raise ValueError('Amount must be between 10,000 and 200,000 UBEC')
        return v


class ActivatorApplicationCreate(BaseModel):
    """Schema for community activator application."""
    name: str = Field(..., min_length=2, max_length=255)
    contact_email: EmailStr
    contact_phone: Optional[str] = None
    location: str = Field(..., min_length=2, max_length=255)
    affiliation: Optional[str] = None
    background: str = Field(..., min_length=20)
    skills: str = Field(..., min_length=20)
    track_record: str = Field(..., min_length=20)
    networks: str = Field(..., min_length=10)
    proposed_services: str = Field(..., min_length=20)
    geographic_scope: str = Field(..., min_length=5)
    time_commitment: str
    year1_plan: str = Field(..., min_length=50)
    requested_amount: int = Field(..., gt=0)
    budget_breakdown: str = Field(..., min_length=20)
    facilitation_philosophy: str = Field(..., min_length=20)
    ubuntu_alignment: str = Field(..., min_length=20)
    reference1_name: str = Field(..., min_length=2)
    reference1_contact: str = Field(..., min_length=5)
    reference2_name: Optional[str] = None
    reference2_contact: Optional[str] = None
    agree_terms: bool
    agree_values: bool
    
    @validator('requested_amount')
    def validate_amount(cls, v):
        if v < 20000 or v > 100000:
            raise ValueError('Amount must be between 20,000 and 100,000 UBEC')
        return v


class LivingLabApplicationCreate(BaseModel):
    """Schema for living lab application."""
    contact_name: str = Field(..., min_length=2, max_length=255)
    contact_email: EmailStr
    contact_phone: Optional[str] = None
    contact_role: str = Field(..., min_length=2)
    location: str = Field(..., min_length=2, max_length=255)
    institution_name: str = Field(..., min_length=2, max_length=255)
    institution_type: str
    student_count: int = Field(..., ge=10)
    land_area: str = Field(..., min_length=1)
    ecosystem_types: str = Field(..., min_length=2)
    site_description: str = Field(..., min_length=20)
    infrastructure: str = Field(..., min_length=10)
    current_curriculum: str = Field(..., min_length=20)
    integration_plan: str = Field(..., min_length=20)
    citizen_science: str = Field(..., min_length=10)
    technical_support: str = Field(..., min_length=10)
    sensors: List[str] = Field(..., min_items=1)
    requested_amount: int = Field(..., gt=0)
    budget_breakdown: str = Field(..., min_length=20)
    community_access: str = Field(..., min_length=10)
    ubuntu_alignment: str = Field(..., min_length=20)
    reference1_name: str = Field(..., min_length=2)
    reference1_contact: str = Field(..., min_length=5)
    agree_terms: bool
    agree_values: bool
    
    @validator('requested_amount')
    def validate_amount(cls, v):
        if v < 5000 or v > 25000:
            raise ValueError('Amount must be between 5,000 and 25,000 UBEC')
        return v


class ApplicationResponse(BaseModel):
    """Response for successful application submission."""
    success: bool = True
    message: str
    reference_number: str
    application_type: str
    submitted_at: datetime


# =============================================================================
# Database Functions
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
    """Store application in database and return result."""
    
    # Generate reference number
    prefixes = {
        'farmer': 'FRM', 'community': 'COM',
        'activator': 'ACT', 'livinglab': 'LAB'
    }
    prefix = prefixes.get(app_type, 'APP')
    
    async with get_db_transaction() as conn:
        # Get next sequence number
        result = await conn.fetchrow("""
            SELECT COALESCE(MAX(
                CAST(SUBSTRING(reference_number FROM '[0-9]+$') AS INTEGER)
            ), 0) + 1 as next_num
            FROM ubec_ui.applications
            WHERE reference_number LIKE $1
        """, f"{prefix}-%")
        
        next_num = result['next_num']
        reference_number = f"{prefix}-{datetime.utcnow().year}-{next_num:04d}"
        
        # Build references array
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
        
        # Filter out non-data fields for application_data JSON
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
            contact_name=application.contact_name,
            contact_email=application.contact_email,
            contact_phone=application.contact_phone,
            location=application.location,
            requested_amount=application.requested_amount
        )
        
        # Send emails (don't fail if email fails)
        send_confirmation_email(
            "farmer", result['reference_number'],
            application.contact_name, application.contact_email,
            result['submitted_at']
        )
        send_admin_notification(
            "farmer", result['reference_number'],
            application.contact_name, application.contact_email,
            application.location, application.requested_amount,
            application.farm_name
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
        
        # Send emails
        send_confirmation_email(
            "community", result['reference_number'],
            application.contact_name, application.contact_email,
            result['submitted_at']
        )
        send_admin_notification(
            "community", result['reference_number'],
            application.contact_name, application.contact_email,
            application.location, application.requested_amount,
            application.organization_name
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
            requested_amount=application.requested_amount,
            organization_name=application.affiliation
        )
        
        # Send emails
        send_confirmation_email(
            "activator", result['reference_number'],
            application.name, application.contact_email,
            result['submitted_at']
        )
        send_admin_notification(
            "activator", result['reference_number'],
            application.name, application.contact_email,
            application.location, application.requested_amount,
            application.affiliation
        )
        
        return ApplicationResponse(
            success=True,
            message="Your community activator application has been submitted successfully.",
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
        
        # Send emails
        send_confirmation_email(
            "livinglab", result['reference_number'],
            application.contact_name, application.contact_email,
            result['submitted_at']
        )
        send_admin_notification(
            "livinglab", result['reference_number'],
            application.contact_name, application.contact_email,
            application.location, application.requested_amount,
            application.institution_name
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


@router.get("/stats")
async def get_application_stats():
    """Get application statistics."""
    try:
        async with get_db_connection() as conn:
            stats = await conn.fetchrow("""
                SELECT 
                    COUNT(*) as total,
                    COUNT(*) FILTER (WHERE status = 'pending') as pending,
                    COUNT(*) FILTER (WHERE status = 'approved') as approved,
                    COUNT(*) FILTER (WHERE status = 'rejected') as rejected,
                    COUNT(*) FILTER (WHERE application_type = 'farmer') as farmers,
                    COUNT(*) FILTER (WHERE application_type = 'community') as communities,
                    COUNT(*) FILTER (WHERE application_type = 'activator') as activators,
                    COUNT(*) FILTER (WHERE application_type = 'livinglab') as livinglabs
                FROM ubec_ui.applications
            """)
            
            return {
                "total": stats['total'],
                "by_status": {
                    "pending": stats['pending'],
                    "approved": stats['approved'],
                    "rejected": stats['rejected']
                },
                "by_type": {
                    "farmer": stats['farmers'],
                    "community": stats['communities'],
                    "activator": stats['activators'],
                    "livinglab": stats['livinglabs']
                }
            }
            
    except Exception as e:
        logger.error(f"Stats error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
