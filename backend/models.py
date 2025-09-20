from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

# Request and Response Models
class FileUploadResponse(BaseModel):
    success: bool
    message: str
    file_metadata: Dict[str, Any]

class Requirement(BaseModel):
    requirement_id: str
    description: str
    priority: str = "Medium"
    compliance_references: List[str] = []

class TestCase(BaseModel):
    test_case_id: str
    title: str
    requirement_id: str
    steps: List[str]
    expected_result: str
    priority: str
    compliance_reference: List[str] = []
    status: str = "Not Tested"
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now().isoformat())

class TestCaseGenerationRequest(BaseModel):
    requirements: List[Requirement]

# New model for the /generate endpoint's request payload
class GenerateRequest(BaseModel):
    gcs_path: str

class TestCaseGenerationResponse(BaseModel):
    success: bool
    message: str
    test_cases: List[TestCase]
    generation_id: str

class TestCaseRegenerationRequest(BaseModel):
    requirements: List[Requirement]
    clarifications: str
    existing_test_cases: Optional[List[TestCase]] = None

class TraceabilityMatrixItem(BaseModel):
    requirement_id: str
    description: str
    test_cases: List[str]
    compliance: List[str]
    status: str

class AuditTrailItem(BaseModel):
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    details: Dict[str, Any]
    user_id: Optional[str] = None

class ExportResponse(BaseModel):
    success: bool
    message: str
    download_url: str

# Mock Data Functions
def get_mock_test_cases() -> List[TestCase]:
    """Return mock test cases for resilience when external APIs fail"""
    return [
        TestCase(
            test_case_id="TC-001",
            title="Verify user login with valid credentials",
            requirement_id="RQ-001",
            steps=["Navigate to login page", "Enter valid username", "Enter valid password", "Click login button"],
            expected_result="User should be logged in successfully and redirected to dashboard",
            priority="High",
            compliance_reference=["FDA 21 CFR Part 11", "HIPAA"],
            status="Not Tested"
        ),
        TestCase(
            test_case_id="TC-002",
            title="Verify patient data encryption at rest",
            requirement_id="RQ-002",
            steps=["Store patient data in database", "Verify encryption status in database", "Attempt to access raw data"],
            expected_result="Data should be stored in encrypted format and not readable without decryption",
            priority="Critical",
            compliance_reference=["HIPAA", "GDPR"],
            status="Not Tested"
        ),
        TestCase(
            test_case_id="TC-003",
            title="Verify audit logging for patient data access",
            requirement_id="RQ-003",
            steps=["Login as healthcare provider", "Access patient records", "Check audit logs"],
            expected_result="Audit log should contain entry with timestamp, user ID, and accessed record ID",
            priority="High",
            compliance_reference=["FDA 21 CFR Part 11", "HIPAA"],
            status="Not Tested"
        )
    ]

def get_mock_traceability_matrix() -> List[TraceabilityMatrixItem]:
    """Return mock traceability matrix for resilience when external APIs fail"""
    return [
        TraceabilityMatrixItem(
            requirement_id="RQ-001",
            description="System must authenticate users with username and password",
            test_cases=["TC-001"],
            compliance=["FDA 21 CFR Part 11", "HIPAA"],
            status="Not Tested"
        ),
        TraceabilityMatrixItem(
            requirement_id="RQ-002",
            description="System must encrypt all patient data at rest",
            test_cases=["TC-002"],
            compliance=["HIPAA", "GDPR"],
            status="Not Tested"
        ),
        TraceabilityMatrixItem(
            requirement_id="RQ-003",
            description="System must log all access to patient records",
            test_cases=["TC-003"],
            compliance=["FDA 21 CFR Part 11", "HIPAA"],
            status="Not Tested"
        )
    ]

def get_mock_audit_trail() -> List[AuditTrailItem]:
    """Return mock audit trail for resilience when external APIs fail"""
    return [
        AuditTrailItem(
            event_type="file_upload",
            details={"filename": "requirements.pdf", "size": 1024000},
            user_id="anonymous"
        ),
        AuditTrailItem(
            event_type="test_case_generation",
            details={"requirements_count": 3, "test_cases_count": 3},
            user_id="anonymous"
        ),
        AuditTrailItem(
            event_type="traceability_matrix_view",
            details={"items_count": 3},
            user_id="anonymous"
        )
    ]