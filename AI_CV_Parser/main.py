import os
import io
import json
import pypdf
from fastapi import FastAPI, UploadFile, File, HTTPException
from openai import AzureOpenAI
from dotenv import load_dotenv

load_dotenv()

MODEL = os.environ.get("MODEL")

client = AzureOpenAI(
    azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT", "https://guardian.sars.gov.za/guardian"),
    api_key=os.environ.get("AZURE_OPENAI_API_KEY"),
    api_version=os.environ.get("AZURE_OPENAI_API_VERSION", "2024-06-01"),
)

app= FastAPI()

@app.post("/parse-resume")
def parse_resume(file : UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail= "Only PDF files are allowed. ")

    file_bytes = file.file.read()
    if len(file_bytes) > 2 * 1024 * 1024:
        raise HTTPException(status_code=413, detail= "file too large. Max size is 2MB. ")

    try:
        pdf_file= io.BytesIO(file_bytes)
        reader = pypdf.PdfReader(pdf_file)
        text_context=[]
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text_context.append(page_text)

        resume_text = "\n".join(text_context).strip()

    except Exception as e:
        raise HTTPException(status_code=400, detail= f"Failed to parse PDF file: {str(e)}")

    if not resume_text:
        raise HTTPException(status_code=400, detail=f"Could not read any text from PDF. is it empty or scanned?")

    prompt = f"""
    You are a resume parsing assistant.

    Extract the following information from the resume below and return it as a valid JSON object:

    - name
    - email
    - phone
    - skills (as a list)
    - work_experience (as a list of objects containing company, role, and duration)
    - education (as a list of objects containing institution, degree, and year)

    Return only the JSON object.
    Do not include explanations, markdown, or any extra text.

    Resume:
    {resume_text}
   """
    response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a precise resume parsing system designed "
                        "to extract candidate data as valid JSON."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            response_format={"type": "json_object"},
            temperature=0
        )

    raw_text = response.choices[0].message.content
    cleaned = raw_text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    parsed = json.loads(cleaned)
    return parsed


