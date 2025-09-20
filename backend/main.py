import os
import logging
import traceback
from datetime import datetime
from dotenv import load_dotenv
from urllib.parse import urlparse

from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from typing import List

# Load environment variables from .env file
load_dotenv()

# Import models from your models.py file
from models import (
    FileUploadResponse, 
    TestCaseGenerationResponse, 
    TestCaseRegenerationRequest, 
    ExportResponse, 
    TraceabilityMatrixItem, 
    AuditTrailItem, 
    GenerateRequest
)

# Import services from the services directory
from services.storage_service import upload_file_to_storage, get_download_url
from services.firestore_service import save_test_cases, get_all_test_cases, log_audit_event, get_audit_trail
from services.bigquery_service import save_test_cases as bq_save_test_cases, update_traceability_matrix as bq_update_traceability_matrix, get_traceability_matrix as bq_get_traceability_matrix
from services.vertex_ai_service import VertexAIService
from services.agent_builder_service import refine_prompt
from services.export_service import export_data
from services.mock_data_service import generate_mock_test_cases, generate_mock_traceability_matrix, generate_mock_audit_trail
from services.pdf_extractor import extract_text_from_gcs_pdf

# Initialize services
vertex_ai_service = VertexAIService()

# Configure logging to see output in your terminal
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI application
app = FastAPI(
    title="Healthcare AI Test Case Generator API",
    description="API for generating healthcare test cases using AI",
    version="1.0.0",
)

# Configure CORS (Cross-Origin Resource Sharing) middleware
# This allows your frontend (running on a different port) to communicate with the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to your frontend's domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    # You can add logic here that needs to run when the server starts
    # For example, verifying connections to databases or external services
    logger.info("Application startup complete.")

@app.get("/")
async def root():
    """Root endpoint for health checks."""
    return {"status": "healthy", "message": "Healthcare AI Test Case Generator API"}

@app.post("/upload", response_model=FileUploadResponse)
async def upload_file_endpoint(file: UploadFile = File(...)):
    """Upload a requirements document (PDF, Word, text)."""
    try:
        # Define allowed content types for the uploaded file
        allowed_types = [
            "application/pdf",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "text/plain"
        ]
        if file.content_type not in allowed_types:
            raise HTTPException(status_code=400, detail="File type not supported. Please upload a PDF, DOCX, or TXT file.")

        content = await file.read()
        file_size = len(content)

        # Define the path where the file will be stored in the GCS bucket
        file_path_in_bucket = f"requirements/{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename}"

        storage_path = await upload_file_to_storage(
            file_content=content, 
            file_name=file_path_in_bucket, 
            content_type=file.content_type
        )

        await log_audit_event(
            user_id="current_user@example.com", # In a real app, get this from auth token
            event_type="Upload requirements document",
            details={"filename": file.filename, "size": file_size, "storage_path": storage_path},
        )

        return FileUploadResponse(
            success=True,
            message="File uploaded successfully.",
            file_metadata={"filename": file.filename, "size": file_size, "storage_path": storage_path},
        )
    except Exception as e:
        logger.error(f"Upload error: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate", response_model=TestCaseGenerationResponse)
async def generate_test_cases_endpoint(request: GenerateRequest):
    """Generate test cases from a file in GCS."""
    gcs_full_url = request.gcs_path
    
    try:
        # Correctly parse the GCS path to get only the object name
        bucket_name = os.getenv("FIREBASE_STORAGE_BUCKET")
        
        # Check if the URL format is as expected
        prefix = f"https://storage.googleapis.com/{bucket_name}/"
        if not gcs_full_url.startswith(prefix):
            raise HTTPException(status_code=400, detail="Invalid GCS URL format.")
        
        # The object path is everything after the bucket name and the next slash
        object_path = gcs_full_url.replace(prefix, "", 1)
        
        # URL Decode the object path in case of special characters in the filename
        from urllib.parse import unquote
        object_path = unquote(object_path)

        requirements_text = await extract_text_from_gcs_pdf(bucket_name, object_path)
        print(f"Extracted requirements text: {requirements_text[:500]}...")  # Print first 500 chars for brevity

        if not requirements_text:
            raise Exception("Failed to extract text from PDF or PDF is empty.")

        test_cases = await vertex_ai_service.generate_test_cases(requirements_text)

        await save_test_cases(test_cases)
        await bq_update_traceability_matrix(test_cases)
        await log_audit_event(
            user_id="current_user@example.com",
            event_type="Generated test cases",
            details={"file_path": object_path, "test_case_count": len(test_cases)},
        )
        
        return TestCaseGenerationResponse(
            success=True,
            message="Test cases generated successfully.",
            test_cases=test_cases,
            generation_id=f"gen-{test_cases[0]['test_case_id']}" if test_cases else "gen-unknown",
        )

    except Exception as e:
        logger.error(f"Generate endpoint error: {traceback.format_exc()}")
        # The service will now automatically use its internal fallback logic
        fallback_cases = await vertex_ai_service.generate_test_cases("") # Trigger fallback
        
        await log_audit_event(
            user_id="current_user@example.com",
            event_type="Generated mock test cases",
            details={"file_path": gcs_full_url, "error": str(e)},
        )
        
        return TestCaseGenerationResponse(
            success=True,
            message=f"Test cases generated using mock data due to an error: {str(e)}",
            test_cases=fallback_cases,
            generation_id="gen-mock-fallback"
        )

@app.post("/regenerate", response_model=TestCaseGenerationResponse)
async def regenerate_test_cases_endpoint(request: TestCaseRegenerationRequest):
    """Regenerate test cases with user clarifications (using mock logic)."""
    try:
        # In a real implementation, you would use the refined prompt to call the AI
        refined_prompt = await refine_prompt(
            requirements=request.requirements,
            clarifications=request.clarifications,
        )
        # For now, we'll return mock data as the regeneration logic is complex
        logger.info(f"Refined prompt for regeneration: {refined_prompt}")
        
        mock_test_cases = generate_mock_test_cases(10)
        
        return TestCaseGenerationResponse(
            success=True,
            message="Test cases regenerated using mock data.",
            test_cases=mock_test_cases,
            generation_id="regen-mock"
        )
    except Exception as e:
        logger.error(f"Regenerate endpoint error: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/traceability", response_model=List[TraceabilityMatrixItem])
async def get_traceability_matrix_endpoint():
    """Get the traceability matrix, with a fallback to mock data."""
    try:
        traceability_matrix = await bq_get_traceability_matrix()
        if not traceability_matrix:
            return generate_mock_traceability_matrix()
        return traceability_matrix
    except Exception as e:
        logger.error(f"Traceability endpoint error: {traceback.format_exc()}")
        return generate_mock_traceability_matrix()

@app.get("/audit", response_model=List[AuditTrailItem])
async def get_audit_trail_endpoint():
    """Get the audit trail, with a fallback to mock data."""
    try:
        audit_trail = await get_audit_trail()
        if not audit_trail:
            return generate_mock_audit_trail()
        return audit_trail
    except Exception as e:
        logger.error(f"Audit endpoint error: {traceback.format_exc()}")
        return generate_mock_audit_trail()

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
        
        # Clean up the local temporary file after upload
        background_tasks.add_task(os.remove, file_path)

        return ExportResponse(
            success=True,
            message="File exported successfully.",
            download_url=download_url
        )
    except Exception as e:
        logger.error(f"Export endpoint error: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

# This block allows you to run the server directly from the command line
# using `python main.py` for development.
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)