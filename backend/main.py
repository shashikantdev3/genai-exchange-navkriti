import os
import logging
import traceback
from datetime import datetime
from dotenv import load_dotenv

from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from typing import List

# Load environment variables
load_dotenv()

# Import models
import models

# Import services
from services.storage_service import upload_file_to_storage, get_download_url
from services.firestore_service import (
    save_test_cases,
    get_all_test_cases,
    log_audit_event,
    get_audit_trail,
)
from services.bigquery_service import (
    save_test_cases_to_bigquery,
    update_traceability_matrix,
    get_traceability_matrix,
)
from services.vertex_ai_service import generate_test_cases as vertex_generate_test_cases
from services.agent_builder_service import refine_prompt
from services.export_service import export_data
from services.mock_data_service import (
    generate_mock_test_cases,
    generate_mock_traceability_matrix,
    generate_mock_audit_trail,
)

# Initialize Firebase Admin SDK using service account
import firebase_admin
from firebase_admin import credentials, storage as firebase_storage

if not firebase_admin._apps:
    cred_path = "keys/serviceAccountKey.json"  # path relative to backend/
    if not os.path.isfile(cred_path):
        raise FileNotFoundError(f"Firebase service account key not found at {cred_path}")

    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred, {
        "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET")
    })

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="Healthcare AI Test Case Generator API",
    description="API for generating healthcare test cases using AI",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint - health check"""
    return {"status": "healthy", "message": "Healthcare AI Test Case Generator API"}

@app.post("/upload", response_model=models.FileUploadResponse)
async def upload_file_endpoint(file: UploadFile = File(...)):
    """Upload a requirements document (PDF, Word, text)"""
    try:
        allowed_types = [
            "application/pdf",
            "application/msword",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "text/plain",
        ]
        if file.content_type not in allowed_types:
            raise HTTPException(status_code=400, detail="File type not supported.")

        content = await file.read()
        file_size = len(content)

        # Upload to Firebase Storage
        storage_path = await upload_file_to_storage(file_content=content, file_name=file.filename, content_type=file.content_type)

        # Log action
        await log_audit_event(
            user="current_user@example.com",
            action="Upload requirements document",
            details={"filename": file.filename, "content_type": file.content_type, "size": file_size},
        )

        return models.FileUploadResponse(
            filename=file.filename,
            content_type=file.content_type,
            size=file_size,
            storage_path=storage_path,
            upload_id=storage_path.split("/")[-1],
        )
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate", response_model=models.TestCaseGenerationResponse)
async def generate_test_cases_endpoint(request: models.TestCaseGenerationRequest):
    """Generate test cases from requirements"""
    try:
        try:
            test_cases = await vertex_generate_test_cases(request.requirements)
            await save_test_cases(test_cases)
            await save_test_cases_to_bigquery(test_cases)
            await update_traceability_matrix(test_cases)

            await log_audit_event(
                user="current_user@example.com",
                action="Generated test cases",
                details={"requirement_count": len(request.requirements), "test_case_count": len(test_cases)},
            )

            return models.TestCaseGenerationResponse(
                test_cases=test_cases,
                generation_id=f"gen-{test_cases[0]['test_case_id']}" if test_cases else "gen-unknown",
            )
        except Exception:
            mock_test_cases = generate_mock_test_cases(len(request.requirements) * 2)
            return models.TestCaseGenerationResponse(test_cases=mock_test_cases, generation_id="gen-mock")
    except Exception as e:
        logger.error(f"Generate endpoint error: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/regenerate", response_model=models.TestCaseGenerationResponse)
async def regenerate_test_cases_endpoint(request: models.TestCaseRegenerationRequest):
    """Regenerate test cases with user clarifications"""
    try:
        try:
            refined_prompt = await refine_prompt(
                original_requirements=request.original_requirements,
                original_test_cases=request.original_test_cases,
                clarifications=request.clarifications,
            )

            test_cases = await vertex_generate_test_cases(request.original_requirements, refined_prompt=refined_prompt)
            await save_test_cases(test_cases, update=True)
            await save_test_cases_to_bigquery(test_cases, update=True)
            await update_traceability_matrix(test_cases)

            await log_audit_event(
                user="current_user@example.com",
                action="Regenerated test cases",
                details={
                    "requirement_count": len(request.original_requirements),
                    "test_case_count": len(test_cases),
                    "clarification_count": len(request.clarifications),
                },
            )

            return models.TestCaseGenerationResponse(
                test_cases=test_cases,
                generation_id=f"regen-{test_cases[0]['test_case_id']}" if test_cases else "regen-unknown",
            )
        except Exception:
            mock_test_cases = generate_mock_test_cases(len(request.original_requirements) * 2)
            for tc in mock_test_cases:
                tc["test_case_id"] = f"{tc['test_case_id']}-R"
            return models.TestCaseGenerationResponse(test_cases=mock_test_cases, generation_id="regen-mock")
    except Exception as e:
        logger.error(f"Regenerate endpoint error: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/traceability", response_model=List[models.TraceabilityMatrixResponse])
async def get_traceability_matrix_endpoint():
    """Get traceability matrix"""
    try:
        try:
            traceability_matrix = await get_traceability_matrix()
            await log_audit_event(user="current_user@example.com", action="Viewed traceability matrix", details={})
            return traceability_matrix
        except Exception:
            return generate_mock_traceability_matrix()
    except Exception as e:
        logger.error(f"Traceability endpoint error: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/audit", response_model=List[models.AuditTrailResponse])
async def get_audit_trail_endpoint():
    """Get audit trail"""
    try:
        try:
            audit_trail = await get_audit_trail()
            await log_audit_event(user="current_user@example.com", action="Viewed audit trail", details={})
            return audit_trail
        except Exception:
            return generate_mock_audit_trail()
    except Exception as e:
        logger.error(f"Audit endpoint error: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/export/{format}", response_model=models.ExportResponse)
async def export_data_endpoint(format: str, background_tasks: BackgroundTasks):
    """Export data to specified format"""
    try:
        if format not in ["csv", "xlsx", "pdf"]:
            raise HTTPException(status_code=400, detail=f"Unsupported format: {format}")

        try:
            traceability_matrix = await get_traceability_matrix()
            test_cases = await get_all_test_cases()
        except Exception:
            traceability_matrix = generate_mock_traceability_matrix()
            test_cases = generate_mock_test_cases(15)

        file_path = await export_data(format, traceability_matrix, test_cases)
        with open(file_path, "rb") as f:
            file_content = f.read()

        filename = f"healthcare_test_cases.{format}"
        storage_path = await upload_file_to_storage(file_content=file_content, file_name=filename, content_type="application/octet-stream")
        download_url = await get_download_url(storage_path)
        background_tasks.add_task(os.remove, file_path)

        await log_audit_event(
            user="current_user@example.com",
            action=f"Exported data to {format}",
            details={"filename": filename, "size": len(file_content), "format": format},
        )

        return models.ExportResponse(
            download_url=download_url,
            filename=filename,
            size=len(file_content),
            generated_at=datetime.now().isoformat(),
        )
    except Exception as e:
        logger.error(f"Export endpoint error: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
