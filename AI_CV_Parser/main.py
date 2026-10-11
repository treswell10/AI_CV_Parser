import os
import io
import json
import pypdf
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from openai import AzureOpenAI
from pydantic import ValidationError
from dotenv import load_dotenv

import models
from database import engine, get_db
from schemas import ParsedResume, ResumeOut

load_dotenv()

MODEL = os.environ.get("MODEL")

client = AzureOpenAI(
    azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT", "https://guardian.sars.gov.za/guardian"),
    api_key=os.environ.get("AZURE_OPENAI_API_KEY"),
    api_version=os.environ.get("AZURE_OPENAI_API_VERSION", "2024-06-01"),
)

# Creates tables if they don't exist (use Alembic later for migrations)
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Resume Parser API")


@app.post("/parse-resume", response_model=ResumeOut)
def parse_resume(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")

    file_bytes = file.file.read()
    if len(file_bytes) > 2 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="File too large. Max size is 2MB.")

    # 1. Extract text
    try:
        reader = pypdf.PdfReader(io.BytesIO(file_bytes))
        resume_text = "\n".join(p.extract_text() or "" for p in reader.pages).strip()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse PDF file: {e}")

    if not resume_text:
        raise HTTPException(status_code=400, detail="Could not read any text from PDF. Is it empty or scanned?")

    # 2. Call LLM
    prompt = f"""
Extract the following information from the resume below and return it as a valid JSON object:

- name
- email
- phone
- skills (as a list of strings)
- work_experience (as a list of objects containing company, role, and duration)
- education (as a list of objects containing institution, degree, and year)

Use null for missing values. Return only the JSON object.

Resume:
{resume_text}
"""
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You are a precise resume parsing system designed to extract candidate data as valid JSON."},
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0,
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"LLM call failed: {e}")

    # 3. Validate LLM output
    raw = response.choices[0].message.content.strip()
    raw = raw.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    try:
        parsed = ParsedResume.model_validate(json.loads(raw))
    except (json.JSONDecodeError, ValidationError) as e:
        raise HTTPException(status_code=502, detail=f"Invalid JSON from model: {e}")

    # 4. Save to DB
    resume = models.Resume(
        file_name=file.filename,
        name=parsed.name,
        email=parsed.email,
        phone=parsed.phone,
        raw_text=resume_text,
        skills=[models.Skill(name=s) for s in parsed.skills if s],
        work_experience=[models.WorkExperience(**w.model_dump()) for w in parsed.work_experience],
        education=[models.Education(**e.model_dump()) for e in parsed.education],
    )
    try:
        db.add(resume)
        db.commit()
        db.refresh(resume)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

    return resume


@app.get("/resumes", response_model=list[ResumeOut])
def list_resumes(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    return db.query(models.Resume).order_by(models.Resume.id.desc()).offset(skip).limit(limit).all()


@app.get("/resumes/{resume_id}", response_model=ResumeOut)
def get_resume(resume_id: int, db: Session = Depends(get_db)):
    resume = db.get(models.Resume, resume_id)
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    return resume


@app.delete("/resumes/{resume_id}", status_code=204)
def delete_resume(resume_id: int, db: Session = Depends(get_db)):
    resume = db.get(models.Resume, resume_id)
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    db.delete(resume)
    db.commit()