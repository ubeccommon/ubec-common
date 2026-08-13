"""
UBEC Protocol - Application Schemas
====================================

Pydantic models for validating and serializing application data.

Attribution:
    This project uses the services of Claude and Anthropic PBC to inform 
    our decisions and recommendations.
"""

from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, validator
from datetime import datetime
from enum import Enum


class ApplicationType(str, Enum):
    FARMER = "farmer"
    COMMUNITY = "community"
    ACTIVATOR = "activator"
    LIVINGLAB = "livinglab"


class ApplicationStatus(str, Enum):
    PENDING = "pending"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"


# =============================================================================
# Base Application Schema
# =============================================================================

class ApplicationBase(BaseModel):
    """Base fields common to all applications."""
    contact_name: str = Field(..., min_length=2, max_length=255)
    contact_email: EmailStr
    contact_phone: Optional[str] = None
    location: str = Field(..., min_length=2, max_length=255)
    requested_amount: int = Field(..., gt=0)
    ubuntu_alignment: str = Field(..., min_length=50)
    agree_terms: bool = Field(...)
    agree_values: bool = Field(...)
    
    # References
    reference1_name: str = Field(..., min_length=2)
    reference1_contact: str = Field(..., min_length=5)
    reference2_name: Optional[str] = None
    reference2_contact: Optional[str] = None
    
    @validator('agree_terms', 'agree_values')
    def must_agree(cls, v):
        if not v:
            raise ValueError('You must agree to the terms and values')
        return v


# =============================================================================
# Farmer Application
# =============================================================================

class FarmerApplicationCreate(ApplicationBase):
    """Schema for creating a farmer application."""
    application_type: str = "farmer"
    
    # Personal info uses base fields
    name: str = Field(..., min_length=2, max_length=255)
    
    # Farm details
    farm_name: Optional[str] = None
    farm_size: str = Field(..., min_length=1)
    products: str = Field(..., min_length=10)
    regenerative_practices: str = Field(..., min_length=50)
    experience: str = Field(...)
    
    # Funding
    token_usage: str = Field(..., min_length=50)
    expected_impact: str = Field(..., min_length=50)
    
    # Ubuntu
    community_connections: str = Field(..., min_length=20)
    
    @validator('requested_amount')
    def validate_farmer_amount(cls, v):
        if v < 1000 or v > 50000:
            raise ValueError('Farmer token amount must be between 1,000 and 50,000 UBEC')
        return v
    
    @validator('name')
    def set_contact_name(cls, v, values):
        values['contact_name'] = v
        return v


# =============================================================================
# Community Application
# =============================================================================

class CommunityApplicationCreate(ApplicationBase):
    """Schema for creating a community application."""
    application_type: str = "community"
    
    # Organization info
    organization_name: str = Field(..., min_length=2, max_length=255)
    organization_type: str = Field(...)
    member_count: int = Field(..., ge=3)
    
    # Contact
    contact_role: str = Field(..., min_length=2)
    
    # Community work
    mission: str = Field(..., min_length=50)
    current_activities: str = Field(..., min_length=50)
    governance_structure: str = Field(..., min_length=30)
    
    # Funding
    token_usage: str = Field(..., min_length=50)
    expected_impact: str = Field(..., min_length=50)
    
    # Ubuntu
    regenerative_practices: str = Field(..., min_length=30)
    
    @validator('requested_amount')
    def validate_community_amount(cls, v):
        if v < 10000 or v > 200000:
            raise ValueError('Community token amount must be between 10,000 and 200,000 UBEC')
        return v


# =============================================================================
# Activator Application
# =============================================================================

class ActivatorApplicationCreate(ApplicationBase):
    """Schema for creating a community activator application."""
    application_type: str = "activator"
    
    # Personal info
    name: str = Field(..., min_length=2, max_length=255)
    affiliation: Optional[str] = None
    
    # Experience
    background: str = Field(..., min_length=50)
    skills: str = Field(..., min_length=50)
    track_record: str = Field(..., min_length=50)
    networks: str = Field(..., min_length=30)
    
    # Scope of work
    proposed_services: str = Field(..., min_length=50)
    geographic_scope: str = Field(..., min_length=10)
    time_commitment: str = Field(...)
    year1_plan: str = Field(..., min_length=100)
    
    # Funding
    budget_breakdown: str = Field(..., min_length=50)
    
    # Philosophy
    facilitation_philosophy: str = Field(..., min_length=50)
    
    @validator('requested_amount')
    def validate_activator_amount(cls, v):
        if v < 20000 or v > 100000:
            raise ValueError('Activator token amount must be between 20,000 and 100,000 UBEC annually')
        return v


# =============================================================================
# Living Lab Application
# =============================================================================

class LivingLabApplicationCreate(ApplicationBase):
    """Schema for creating a living lab application."""
    application_type: str = "livinglab"
    
    # Institution info
    institution_name: str = Field(..., min_length=2, max_length=255)
    institution_type: str = Field(...)
    student_count: int = Field(..., ge=10)
    
    # Contact
    contact_role: str = Field(..., min_length=2)
    
    # Site info
    land_area: str = Field(..., min_length=1)
    ecosystem_types: str = Field(..., min_length=5)
    site_description: str = Field(..., min_length=50)
    infrastructure: str = Field(..., min_length=30)
    
    # Educational program
    current_curriculum: str = Field(..., min_length=50)
    integration_plan: str = Field(..., min_length=50)
    citizen_science: str = Field(..., min_length=30)
    
    # Technical
    technical_support: str = Field(..., min_length=30)
    sensors: List[str] = Field(..., min_items=1)
    
    # Funding
    budget_breakdown: str = Field(..., min_length=50)
    
    # Community
    community_access: str = Field(..., min_length=30)
    
    @validator('requested_amount')
    def validate_livinglab_amount(cls, v):
        if v < 5000 or v > 25000:
            raise ValueError('Living Lab token amount must be between 5,000 and 25,000 UBEC')
        return v


# =============================================================================
# Response Schemas
# =============================================================================

class ApplicationResponse(BaseModel):
    """Response after successful application submission."""
    success: bool
    message: str
    reference_number: str
    application_type: str
    submitted_at: datetime
    
    class Config:
        from_attributes = True


class ApplicationListItem(BaseModel):
    """Summary item for listing applications."""
    id: int
    reference_number: str
    application_type: str
    status: str
    contact_name: str
    contact_email: str
    location: str
    requested_amount: int
    submitted_at: datetime
    
    class Config:
        from_attributes = True


class ApplicationDetail(ApplicationListItem):
    """Full application detail."""
    organization_name: Optional[str]
    application_data: dict
    approved_amount: Optional[int]
    reviewer_notes: Optional[str]
    reviewed_at: Optional[datetime]
    decided_at: Optional[datetime]
    
    class Config:
        from_attributes = True
