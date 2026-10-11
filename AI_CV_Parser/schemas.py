from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, field_validator


# ---------- Shared pieces ----------
class WorkExperienceSchema(BaseModel):
    # LLM may return 2021 as int -> convert to "2021"
    model_config = ConfigDict(from_attributes=True, coerce_numbers_to_str=True)

    company: Optional[str] = None
    role: Optional[str] = None
    duration: Optional[str] = None


class EducationSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True, coerce_numbers_to_str=True)

    institution: Optional[str] = None
    degree: Optional[str] = None
    year: Optional[str] = None


# ---------- Validates the LLM JSON output ----------
class ParsedResume(BaseModel):
    model_config = ConfigDict(coerce_numbers_to_str=True)

    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    skills: list[str] = []
    work_experience: list[WorkExperienceSchema] = []
    education: list[EducationSchema] = []


# ---------- API response (from DB) ----------
class ResumeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    file_name: str
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    skills: list[str] = []
    work_experience: list[WorkExperienceSchema] = []
    education: list[EducationSchema] = []
    created_at: datetime

    # DB returns Skill objects -> convert to plain strings
    @field_validator("skills", mode="before")
    @classmethod
    def skills_to_names(cls, v):
        return [s.name if hasattr(s, "name") else s for s in (v or [])]