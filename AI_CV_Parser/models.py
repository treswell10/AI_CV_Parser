from sqlalchemy import Column, Integer, Unicode, UnicodeText, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship

from database import Base


class Resume(Base):
    __tablename__ = "Resumes"

    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(Unicode(255), nullable=False)
    name = Column(Unicode(200), nullable=True)
    email = Column(Unicode(255), nullable=True, index=True)
    phone = Column(Unicode(50), nullable=True)
    raw_text = Column(UnicodeText, nullable=True)          # NVARCHAR(MAX)
    created_at = Column(DateTime, server_default=func.getdate(), nullable=False)

    skills = relationship("Skill", back_populates="resume", cascade="all, delete-orphan")
    work_experience = relationship("WorkExperience", back_populates="resume", cascade="all, delete-orphan")
    education = relationship("Education", back_populates="resume", cascade="all, delete-orphan")


class Skill(Base):
    __tablename__ = "ResumeSkills"

    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("Resumes.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(Unicode(150), nullable=False)

    resume = relationship("Resume", back_populates="skills")


class WorkExperience(Base):
    __tablename__ = "ResumeWorkExperience"

    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("Resumes.id", ondelete="CASCADE"), nullable=False, index=True)
    company = Column(Unicode(255), nullable=True)
    role = Column(Unicode(255), nullable=True)
    duration = Column(Unicode(100), nullable=True)

    resume = relationship("Resume", back_populates="work_experience")


class Education(Base):
    __tablename__ = "ResumeEducation"

    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("Resumes.id", ondelete="CASCADE"), nullable=False, index=True)
    institution = Column(Unicode(255), nullable=True)
    degree = Column(Unicode(255), nullable=True)
    year = Column(Unicode(50), nullable=True)

    resume = relationship("Resume", back_populates="education")