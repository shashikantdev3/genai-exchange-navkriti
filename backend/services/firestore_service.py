import os
from dotenv import load_dotenv
from google.cloud import firestore
import firebase_admin
from firebase_admin import credentials, firestore as firebase_firestore
from typing import List, Dict, Any
import uuid
from datetime import datetime
import json

# Load environment variables
load_dotenv()

# Initialize Firebase Admin SDK if not already initialized
try:
    firebase_app = firebase_admin.get_app()
except ValueError:
    # Use service account or default credentials
    cred = credentials.ApplicationDefault()
    firebase_admin.initialize_app(cred, {
        'projectId': os.getenv('FIREBASE_PROJECT_ID')
    })

# Get Firestore client
db = firebase_firestore.client()

async def save_test_cases(test_cases: List[Dict[str, Any]]) -> bool:
    """
    Save test cases to Firestore
    
    Args:
        test_cases: List of test cases to save
        
    Returns:
        True if successful, False otherwise
    """
    try:
        batch = db.batch()
        
        for test_case in test_cases:
            # Convert to dict if it's a Pydantic model
            if hasattr(test_case, "dict"):
                test_case = test_case.dict()
                
            # Create a document reference with the test case ID
            doc_ref = db.collection('testcases').document(test_case.get('test_case_id'))
            batch.set(doc_ref, test_case)
        
        # Commit the batch
        batch.commit()
        return True
    except Exception as e:
        print(f"Error saving test cases to Firestore: {str(e)}")
        return False

async def update_test_cases(test_cases: List[Dict[str, Any]]) -> bool:
    """
    Update test cases in Firestore
    
    Args:
        test_cases: List of test cases to update
        
    Returns:
        True if successful, False otherwise
    """
    try:
        batch = db.batch()
        
        for test_case in test_cases:
            # Convert to dict if it's a Pydantic model
            if hasattr(test_case, "dict"):
                test_case = test_case.dict()
                
            # Update the updated_at timestamp
            test_case['updated_at'] = datetime.now().isoformat()
            
            # Create a document reference with the test case ID
            doc_ref = db.collection('testcases').document(test_case.get('test_case_id'))
            batch.update(doc_ref, test_case)
        
        # Commit the batch
        batch.commit()
        return True
    except Exception as e:
        print(f"Error updating test cases in Firestore: {str(e)}")
        return False

async def get_all_test_cases() -> List[Dict[str, Any]]:
    """
    Get all test cases from Firestore
    
    Returns:
        List of test cases
    """
    try:
        # Query the testcases collection
        docs = db.collection('testcases').stream()
        
        # Convert to list of dicts
        test_cases = [doc.to_dict() for doc in docs]
        
        return test_cases
    except Exception as e:
        print(f"Error getting test cases from Firestore: {str(e)}")
        # Return empty list for resilience
        return []

async def log_audit_event(event_type: str, details: Dict[str, Any], user_id: str = "anonymous") -> bool:
    """
    Log an audit event to Firestore
    
    Args:
        event_type: Type of event (e.g., file_upload, test_case_generation)
        details: Details of the event
        user_id: ID of the user who performed the action
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Create audit event document
        event_id = str(uuid.uuid4())
        event_data = {
            'event_id': event_id,
            'event_type': event_type,
            'timestamp': datetime.now().isoformat(),
            'details': details,
            'user_id': user_id
        }
        
        # Add to Firestore
        db.collection('audit').document(event_id).set(event_data)
        
        return True
    except Exception as e:
        print(f"Error logging audit event to Firestore: {str(e)}")
        return False

async def get_audit_trail() -> List[Dict[str, Any]]:
    """
    Get audit trail from Firestore
    
    Returns:
        List of audit events
    """
    try:
        # Query the audit collection, ordered by timestamp
        docs = db.collection('audit').order_by('timestamp', direction=firestore.Query.DESCENDING).stream()
        
        # Convert to list of dicts
        audit_trail = [doc.to_dict() for doc in docs]
        
        return audit_trail
    except Exception as e:
        print(f"Error getting audit trail from Firestore: {str(e)}")
        # Return empty list for resilience
        return []