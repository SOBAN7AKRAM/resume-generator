from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, HttpUrl, EmailStr
from typing import List, Optional
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
import random
import boto3
import uuid
import os
from tempfile import NamedTemporaryFile
from dotenv import load_dotenv

# Load .env variables
load_dotenv()


# AWS Configuration
AWS_BUCKET_NAME = os.getenv("AWS_BUCKET_NAME")
AWS_REGION = os.getenv("AWS_REGION")

s3_client = boto3.client("s3", region_name=AWS_REGION)


app = FastAPI()

# Jinja2 Environment
env = Environment(loader=FileSystemLoader("templates"))

# Pydantic Model
class SkillCategory(BaseModel):
    name: str
    tools: List[str]

class ExperienceEntry(BaseModel):
    company: str
    role: str
    start_date: str  # could also use `datetime` or `date` if format is fixed
    end_date: str
    achievements: List[str]

class EducationEntry(BaseModel):
    school: str
    start_date: str
    end_date: str
    degree: str
    courseworks: List[str]

class ResumeData(BaseModel):
    name: str
    email: EmailStr
    phone: str
    address: str
    linkedin: Optional[HttpUrl]
    github: Optional[HttpUrl]
    summary: str
    skills: List[SkillCategory]
    experience: List[ExperienceEntry]
    education: List[EducationEntry]


@app.post("/generate-resume/")
async def generate_resume(data: ResumeData):
    try:
        # Choose random template
        template_index = random.randint(1, 4)
        template = env.get_template(f"resume_template{template_index}.html")

        # Render HTML
        html_content = template.render(data=data.dict())

        # Write to temporary PDF
        with NamedTemporaryFile(suffix=".pdf", delete=False) as temp_pdf:
            HTML(string=html_content).write_pdf(temp_pdf.name)
            temp_pdf_path = temp_pdf.name
            

        # Upload to S3
        file_key = f"resumes/{uuid.uuid4()}.pdf"
        
        s3_client.upload_file(
            temp_pdf_path,
            AWS_BUCKET_NAME,
            file_key,
            ExtraArgs={'ContentType': 'application/pdf'}
        )

        # Generate pre-signed URL (valid for 1 hour)
        url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': AWS_BUCKET_NAME, 'Key': file_key},
            ExpiresIn=3600  # link valid for 1 hour
        )


        # Clean up temp file
        os.remove(temp_pdf_path)

        return {"url": url}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Resume generation failed: {str(e)}")
