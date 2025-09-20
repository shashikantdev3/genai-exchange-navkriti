"""
Mock data service to provide fallback data when external APIs fail.
This ensures resilience during development or when external services are unavailable.
"""

from typing import List, Dict, Any
import random
import uuid
from datetime import datetime, timedelta

# Mock requirements data
MOCK_REQUIREMENTS = [
    {
        "requirement_id": "RQ-001",
        "description": "System must log all user activity for audit purposes",
        "priority": "high",
        "compliance": ["FDA 21 CFR Part 11", "ISO 13485"]
    },
    {
        "requirement_id": "RQ-002",
        "description": "System must validate user input to prevent SQL injection",
        "priority": "high",
        "compliance": ["HIPAA", "ISO 27001"]
    },
    {
        "requirement_id": "RQ-003",
        "description": "System must encrypt all PHI data at rest and in transit",
        "priority": "high",
        "compliance": ["HIPAA", "GDPR", "ISO 27001"]
    },
    {
        "requirement_id": "RQ-004",
        "description": "System must provide role-based access control",
        "priority": "medium",
        "compliance": ["HIPAA", "ISO 27001"]
    },
    {
        "requirement_id": "RQ-005",
        "description": "System must maintain an audit trail of all data modifications",
        "priority": "medium",
        "compliance": ["FDA 21 CFR Part 11", "HIPAA"]
    }
]

# Mock test case templates
TEST_CASE_TEMPLATES = [
    {
        "title": "Verify {action} functionality",
        "steps": [
            "Log in as {role} user",
            "Navigate to {feature} screen",
            "Perform {action} operation",
            "Verify the {result}"
        ],
        "expected_result": "The system should {expected_behavior} and display appropriate {message_type} message"
    },
    {
        "title": "Test {feature} with invalid inputs",
        "steps": [
            "Log in as {role} user",
            "Navigate to {feature} screen",
            "Enter invalid {data_type} in the {field} field",
            "Attempt to submit the form"
        ],
        "expected_result": "System should validate input and display appropriate error message"
    },
    {
        "title": "Verify {feature} access control",
        "steps": [
            "Log in as {role} user",
            "Attempt to access {feature} functionality",
            "Verify authorization check"
        ],
        "expected_result": "Access should be {access_result} based on user role permissions"
    }
]

# Data for template variables
TEMPLATE_DATA = {
    "action": ["create", "read", "update", "delete", "export", "import", "search", "filter"],
    "role": ["admin", "doctor", "nurse", "technician", "patient", "guest"],
    "feature": ["patient records", "medication management", "appointment scheduling", "billing", "reporting", "user management", "audit logs"],
    "result": ["operation result", "data changes", "system response", "error handling"],
    "expected_behavior": ["complete the operation successfully", "validate all inputs", "reject unauthorized access", "log the activity"],
    "message_type": ["success", "error", "warning", "information"],
    "data_type": ["text", "number", "date", "special characters", "empty value", "extremely long string"],
    "field": ["name", "ID", "date", "amount", "description", "code"],
    "access_result": ["granted", "denied"]
}

def get_random_from_list(items: List[str]) -> str:
    """Get a random item from a list"""
    return random.choice(items)

def fill_template(template: Dict[str, Any]) -> Dict[str, Any]:
    """Fill a template with random data"""
    result = template.copy()
    
    # Replace template variables in title
    if "{" in result["title"]:
        for key, values in TEMPLATE_DATA.items():
            if "{" + key + "}" in result["title"]:
                result["title"] = result["title"].replace("{" + key + "}", get_random_from_list(values))
    
    # Replace template variables in steps
    new_steps = []
    for step in result["steps"]:
        new_step = step
        for key, values in TEMPLATE_DATA.items():
            if "{" + key + "}" in new_step:
                new_step = new_step.replace("{" + key + "}", get_random_from_list(values))
        new_steps.append(new_step)
    result["steps"] = new_steps
    
    # Replace template variables in expected result
    if "{" in result["expected_result"]:
        for key, values in TEMPLATE_DATA.items():
            if "{" + key + "}" in result["expected_result"]:
                result["expected_result"] = result["expected_result"].replace("{" + key + "}", get_random_from_list(values))
    
    return result

def generate_mock_test_cases(count: int = 10) -> List[Dict[str, Any]]:
    """
    Generate mock test cases
    
    Args:
        count: Number of test cases to generate
        
    Returns:
        List of mock test cases
    """
    test_cases = []
    
    for i in range(count):
        # Select a requirement
        requirement = random.choice(MOCK_REQUIREMENTS)
        
        # Select and fill a test case template
        template = random.choice(TEST_CASE_TEMPLATES)
        test_case = fill_template(template)
        
        # Add test case specific fields
        test_case["test_case_id"] = f"TC-{1001 + i}"
        test_case["requirement_id"] = requirement["requirement_id"]
        test_case["priority"] = random.choice(["high", "medium", "low"])
        test_case["compliance_reference"] = requirement["compliance"]
        test_case["status"] = random.choice(["Not Tested", "Passed", "Failed", "Blocked"])
        
        test_cases.append(test_case)
    
    return test_cases

def generate_mock_traceability_matrix() -> List[Dict[str, Any]]:
    """
    Generate mock traceability matrix
    
    Returns:
        Mock traceability matrix
    """
    traceability_matrix = []
    
    # Generate test cases first to reference them
    test_cases = generate_mock_test_cases(15)
    
    # Group test cases by requirement
    test_cases_by_req = {}
    for test_case in test_cases:
        req_id = test_case["requirement_id"]
        if req_id not in test_cases_by_req:
            test_cases_by_req[req_id] = []
        test_cases_by_req[req_id].append(test_case["test_case_id"])
    
    # Create traceability matrix entries
    for req in MOCK_REQUIREMENTS:
        req_id = req["requirement_id"]
        matrix_entry = {
            "requirement_id": req_id,
            "description": req["description"],
            "test_cases": test_cases_by_req.get(req_id, []),
            "compliance": req["compliance"],
            "status": "Not Tested" if not test_cases_by_req.get(req_id) else random.choice(["Not Tested", "Partially Tested", "Fully Tested"])
        }
        traceability_matrix.append(matrix_entry)
    
    return traceability_matrix

def generate_mock_audit_trail(count: int = 20) -> List[Dict[str, Any]]:
    """
    Generate mock audit trail entries
    
    Args:
        count: Number of audit entries to generate
        
    Returns:
        List of mock audit entries
    """
    audit_entries = []
    
    actions = [
        "Uploaded requirements document",
        "Generated test cases",
        "Regenerated test cases with clarifications",
        "Viewed traceability matrix",
        "Exported test cases",
        "Modified test case",
        "Deleted test case",
        "Added new requirement",
        "Modified requirement",
        "Viewed audit trail"
    ]
    
    users = ["john.doe@healthcare.org", "jane.smith@healthcare.org", "admin@healthcare.org"]
    
    # Start from 30 days ago
    start_date = datetime.now() - timedelta(days=30)
    
    for i in range(count):
        # Generate a random timestamp within the last 30 days
        timestamp = start_date + timedelta(
            days=random.randint(0, 30),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59)
        )
        
        entry = {
            "id": str(uuid.uuid4()),
            "timestamp": timestamp.isoformat(),
            "user": random.choice(users),
            "action": random.choice(actions),
            "details": {
                "ip_address": f"192.168.1.{random.randint(2, 254)}",
                "browser": random.choice(["Chrome", "Firefox", "Safari", "Edge"]),
                "status": random.choice(["success", "success", "success", "failed"])  # Mostly successful
            }
        }
        
        # Add action-specific details
        if "document" in entry["action"]:
            entry["details"]["document_name"] = f"requirements-v{random.randint(1, 5)}.pdf"
        elif "test case" in entry["action"]:
            entry["details"]["test_case_id"] = f"TC-{1001 + random.randint(0, 20)}"
        elif "requirement" in entry["action"]:
            entry["details"]["requirement_id"] = f"RQ-{1 + random.randint(0, 10):03d}"
        
        audit_entries.append(entry)
    
    # Sort by timestamp
    audit_entries.sort(key=lambda x: x["timestamp"])
    
    return audit_entries