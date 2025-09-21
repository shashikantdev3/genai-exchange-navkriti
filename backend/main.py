import os
import logging
import traceback
from datetime import datetime
from dotenv import load_dotenv
from urllib.parse import unquote

# --- Core Libraries ---
from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from typing import List

# --- Google Cloud & Firebase Authentication ---
import firebase_admin
from firebase_admin import credentials

# Load environment variables from .env file FIRST
load_dotenv()

# --- Centralized Firebase Admin Initialization using ADC ---
# This block runs once and uses Application Default Credentials.
# It relies on the GOOGLE_APPLICATION_CREDENTIALS environment variable.
if not firebase_admin._apps:
    try:
        project_id = os.getenv("FIREBASE_PROJECT_ID")
        if not project_id:
            raise ValueError("FIREBASE_PROJECT_ID not found in .env file.")

        cred = credentials.ApplicationDefault()
        
        # Explicitly initialize the app with the Project ID to ensure consistency
        firebase_admin.initialize_app(cred, {
            "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET"),
            "projectId": project_id,
        })
        print(f"Firebase Admin SDK initialized successfully for project: {project_id}")
    except Exception as e:
        print(f"Failed to initialize Firebase Admin SDK: {e}")
# --- End of Initialization ---


# --- Import Local Modules ---
from models import (
    FileUploadResponse, 
    TestCaseGenerationResponse, 
    TestCaseRegenerationRequest, 
    ExportResponse, 
    TraceabilityMatrixItem, 
    AuditTrailItem, 
    GenerateRequest
)
from services.storage_service import upload_file_to_storage, get_download_url
from services.firestore_service import save_test_cases, get_all_test_cases, log_audit_event, get_audit_trail
from services.bigquery_service import update_traceability_matrix as bq_update_traceability_matrix, get_traceability_matrix as bq_get_traceability_matrix
from services.vertex_ai_service import VertexAIService
from services.export_service import export_data
from services.pdf_extractor import extract_text_from_gcs_pdf

# Initialize services
vertex_ai_service = VertexAIService()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI application
app = FastAPI(
    title="Healthcare AI Test Case Generator API",
    description="API for generating healthcare test cases using AI",
    version="1.0.0",
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, restrict this to your frontend's domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    logger.info("Application startup complete.")

@app.get("/")
async def root():
    """Root endpoint for health checks."""
    return {"status": "healthy", "message": "Healthcare AI Test Case Generator API"}

@app.post("/upload", response_model=FileUploadResponse)
async def upload_file_endpoint(file: UploadFile = File(...)):
    """Upload a requirements document."""
    try:
        content = await file.read()
        file_path_in_bucket = f"requirements/{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename}"
        storage_path = await upload_file_to_storage(
            file_content=content, 
            file_name=file_path_in_bucket, 
            content_type=file.content_type
        )
        return FileUploadResponse(
            success=True,
            message="File uploaded successfully.",
            file_metadata={"filename": file.filename, "size": len(content), "storage_path": storage_path},
        )
    except Exception as e:
        logger.error(f"Upload error: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate", response_model=TestCaseGenerationResponse)
async def generate_test_cases_endpoint(request: GenerateRequest):
    """Generate test cases from a file in GCS."""
    gcs_full_url = request.gcs_path
    
    try:
        bucket_name = os.getenv("FIREBASE_STORAGE_BUCKET")
        prefix = f"https://storage.googleapis.com/{bucket_name}/"
        if not gcs_full_url.startswith(prefix):
            raise HTTPException(status_code=400, detail="Invalid GCS URL format.")
        
        object_path = unquote(gcs_full_url.replace(prefix, "", 1))

        requirements_text = await extract_text_from_gcs_pdf(bucket_name, object_path)
        if not requirements_text:
            raise Exception("Failed to extract text from PDF or PDF is empty.")

        test_cases = await vertex_ai_service.generate_test_cases(requirements_text)
        if test_cases:
            await save_test_cases(test_cases)
            await bq_update_traceability_matrix(test_cases)
        
        return TestCaseGenerationResponse(
            success=True,
            message="Test cases generated successfully.",
            test_cases=test_cases,
            generation_id="gen-123"
        )
    except Exception as e:
        logger.error(f"Generate endpoint error: {traceback.format_exc()}")
        fallback_cases = await vertex_ai_service.generate_test_cases("") # Trigger fallback
        return TestCaseGenerationResponse(
            success=True,
            message=f"Test cases generated using mock data due to an error: {str(e)}",
            test_cases=fallback_cases,
            generation_id="gen-mock-fallback"
        )

@app.get("/traceability", response_model=List[TraceabilityMatrixItem])
async def get_traceability_matrix_endpoint():
    return await bq_get_traceability_matrix()

@app.get("/audit", response_model=List[AuditTrailItem])
async def get_audit_trail_endpoint():
    return await get_audit_trail()

@app.get("/export/{data_format}", response_model=ExportResponse)
async def export_data_endpoint(data_format: str, background_tasks: BackgroundTasks):
    """Export test cases and traceability matrix to a specified format."""
    try:
        if data_format not in ["csv", "xlsx", "pdf"]:
            raise HTTPException(status_code=400, detail=f"Unsupported format: {data_format}")

        test_cases = await get_all_test_cases()
        
        file_path = await export_data(data_format, [], test_cases)
        
        with open(file_path, "rb") as f:
            file_content = f.read()
        
        filename = f"exported_test_cases_{datetime.now().strftime('%Y%m%d')}.{data_format}"
        storage_path = await upload_file_to_storage(
            file_content=file_content, 
            file_name=f"exports/{filename}", 
            content_type="application/octet-stream"
        )
        download_url = await get_download_url(storage_path)
        
        background_tasks.add_task(os.remove, file_path)

        return ExportResponse(
            success=True,
            message="File exported successfully.",
            download_url=download_url
        )
    except Exception as e:
        logger.error(f"Export endpoint error: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

# Main execution block for running with `python main.py`
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)