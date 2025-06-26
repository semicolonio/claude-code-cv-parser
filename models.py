#!/usr/bin/env python3
"""Pydantic models for CV candidate data."""

from datetime import date
from typing import List, Optional
from pydantic import BaseModel, EmailStr


class ContactInfo(BaseModel):
    """Contact information for a candidate."""
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None
    portfolio: Optional[str] = None
    address: Optional[str] = None


class Experience(BaseModel):
    """Work experience entry."""
    company: str
    position: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    is_current: bool = False
    description: Optional[str] = None
    achievements: List[str] = []


class Education(BaseModel):
    """Education entry."""
    institution: str
    degree: str
    field_of_study: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    gpa: Optional[str] = None
    achievements: List[str] = []


class Project(BaseModel):
    """Project entry."""
    name: str
    description: str
    technologies: List[str] = []
    url: Optional[str] = None
    date: Optional[str] = None


class Certification(BaseModel):
    """Certification entry."""
    name: str
    issuer: str
    date_issued: Optional[str] = None
    expiry_date: Optional[str] = None
    credential_id: Optional[str] = None


class CandidateProfile(BaseModel):
    """Complete candidate profile extracted from CV."""
    name: str
    contact_info: ContactInfo
    summary: Optional[str] = None
    skills: List[str] = []
    experience: List[Experience] = []
    education: List[Education] = []
    projects: List[Project] = []
    certifications: List[Certification] = []
    languages: List[str] = []
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            date: lambda v: v.isoformat()
        }