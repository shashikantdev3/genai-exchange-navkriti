import os
from dotenv import load_dotenv
from google.cloud import bigquery
from typing import List, Dict, Any
import json

# Load environment variables
load_dotenv()

# Initialize BigQuery client
client = bigquery.Client(project=os.getenv('BIGQUERY_PROJECT_ID'))

# Define dataset and table names
DATASET_ID = "healthcare_testcases"
REQUIREMENTS_TABLE = "requirements"
TESTCASES_TABLE = "testcases"
TRACEABILITY_TABLE = "traceability_matrix"

async def ensure_tables_exist():
    """Ensure that all required tables exist in BigQuery"""
    try:
        dataset_ref = client.dataset(DATASET_ID)
        
        # Try to get dataset or create if not exists
        try:
            client.get_dataset(dataset_ref)
        except Exception:
            dataset = bigquery.Dataset(dataset_ref)
            dataset.location = "US"
            client.create_dataset(dataset)
        
        # Create requirements table if not exists
        requirements_schema = [
            bigquery.SchemaField("requirement_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("description", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("priority", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("compliance_references", "STRING", mode="REPEATED"),
        ]
        
        requirements_table_ref = dataset_ref.table(REQUIREMENTS_TABLE)
        try:
            client.get_table(requirements_table_ref)
        except Exception:
            requirements_table = bigquery.Table(requirements_table_ref, schema=requirements_schema)
            client.create_table(requirements_table)
        
        # Create testcases table if not exists
        testcases_schema = [
            bigquery.SchemaField("test_case_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("title", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("requirement_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("steps", "STRING", mode="REPEATED"),
            bigquery.SchemaField("expected_result", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("priority", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("compliance_reference", "STRING", mode="REPEATED"),
            bigquery.SchemaField("status", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED"),
            bigquery.SchemaField("updated_at", "TIMESTAMP", mode="REQUIRED"),
        ]
        
        testcases_table_ref = dataset_ref.table(TESTCASES_TABLE)
        try:
            client.get_table(testcases_table_ref)
        except Exception:
            testcases_table = bigquery.Table(testcases_table_ref, schema=testcases_schema)
            client.create_table(testcases_table)
        
        # Create traceability table if not exists
        traceability_schema = [
            bigquery.SchemaField("requirement_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("description", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("test_cases", "STRING", mode="REPEATED"),
            bigquery.SchemaField("compliance", "STRING", mode="REPEATED"),
            bigquery.SchemaField("status", "STRING", mode="REQUIRED"),
        ]
        
        traceability_table_ref = dataset_ref.table(TRACEABILITY_TABLE)
        try:
            client.get_table(traceability_table_ref)
        except Exception:
            traceability_table = bigquery.Table(traceability_table_ref, schema=traceability_schema)
            client.create_table(traceability_table)
            
        return True
    except Exception as e:
        print(f"Error ensuring BigQuery tables exist: {str(e)}")
        return False

async def save_test_cases(test_cases: List[Dict[str, Any]]) -> bool:
    """
    Save test cases to BigQuery
    
    Args:
        test_cases: List of test cases to save
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Ensure tables exist
        await ensure_tables_exist()
        
        # Prepare rows for insertion
        rows_to_insert = []
        for test_case in test_cases:
            # Convert to dict if it's a Pydantic model
            if hasattr(test_case, "dict"):
                test_case = test_case.dict()
            
            # Convert lists to JSON strings if needed
            if isinstance(test_case.get('steps'), list):
                test_case['steps'] = [str(step) for step in test_case['steps']]
            
            if isinstance(test_case.get('compliance_reference'), list):
                test_case['compliance_reference'] = [str(ref) for ref in test_case['compliance_reference']]
            
            rows_to_insert.append(test_case)
        
        # Insert rows
        table_ref = client.dataset(DATASET_ID).table(TESTCASES_TABLE)
        errors = client.insert_rows_json(table_ref, rows_to_insert)
        
        if errors:
            print(f"Errors inserting rows into BigQuery: {errors}")
            return False
        
        # Update traceability matrix
        await update_traceability_matrix(test_cases)
        
        return True
    except Exception as e:
        print(f"Error saving test cases to BigQuery: {str(e)}")
        return False

async def update_test_cases(test_cases: List[Dict[str, Any]]) -> bool:
    """
    Update test cases in BigQuery
    
    Args:
        test_cases: List of test cases to update
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # For simplicity, we'll delete and re-insert the test cases
        # In a production environment, you might want to use a more efficient approach
        
        # Ensure tables exist
        await ensure_tables_exist()
        
        # Delete existing test cases
        for test_case in test_cases:
            test_case_id = test_case.get('test_case_id')
            if test_case_id:
                query = f"""
                DELETE FROM `{os.getenv('BIGQUERY_PROJECT_ID')}.{DATASET_ID}.{TESTCASES_TABLE}`
                WHERE test_case_id = '{test_case_id}'
                """
                query_job = client.query(query)
                query_job.result()
        
        # Insert updated test cases
        await save_test_cases(test_cases)
        
        # Update traceability matrix
        await update_traceability_matrix(test_cases)
        
        return True
    except Exception as e:
        print(f"Error updating test cases in BigQuery: {str(e)}")
        return False

async def update_traceability_matrix(test_cases: List[Dict[str, Any]]) -> bool:
    """
    Update traceability matrix in BigQuery based on test cases
    
    Args:
        test_cases: List of test cases to update traceability for
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Group test cases by requirement_id
        requirements_map = {}
        for test_case in test_cases:
            req_id = test_case.get('requirement_id')
            if req_id:
                if req_id not in requirements_map:
                    requirements_map[req_id] = {
                        'requirement_id': req_id,
                        'description': '',  # Will be populated from requirements table if available
                        'test_cases': [],
                        'compliance': [],
                        'status': 'Not Tested'
                    }
                
                # Add test case ID to the requirement's test cases
                requirements_map[req_id]['test_cases'].append(test_case.get('test_case_id'))
                
                # Add compliance references
                compliance_refs = test_case.get('compliance_reference', [])
                if isinstance(compliance_refs, list):
                    for ref in compliance_refs:
                        if ref not in requirements_map[req_id]['compliance']:
                            requirements_map[req_id]['compliance'].append(ref)
                
                # Update status if any test case is tested
                if test_case.get('status') != 'Not Tested':
                    requirements_map[req_id]['status'] = 'Partially Tested'
        
        # Update traceability matrix
        for req_id, traceability_item in requirements_map.items():
            # Delete existing entry
            query = f"""
            DELETE FROM `{os.getenv('BIGQUERY_PROJECT_ID')}.{DATASET_ID}.{TRACEABILITY_TABLE}`
            WHERE requirement_id = '{req_id}'
            """
            query_job = client.query(query)
            query_job.result()
            
            # Insert updated entry
            table_ref = client.dataset(DATASET_ID).table(TRACEABILITY_TABLE)
            errors = client.insert_rows_json(table_ref, [traceability_item])
            
            if errors:
                print(f"Errors inserting traceability item into BigQuery: {errors}")
        
        return True
    except Exception as e:
        print(f"Error updating traceability matrix in BigQuery: {str(e)}")
        return False

async def get_traceability_matrix() -> List[Dict[str, Any]]:
    """
    Get traceability matrix from BigQuery
    
    Returns:
        List of traceability matrix items
    """
    try:
        # Ensure tables exist
        await ensure_tables_exist()
        
        # Query traceability matrix
        query = f"""
        SELECT * FROM `{os.getenv('BIGQUERY_PROJECT_ID')}.{DATASET_ID}.{TRACEABILITY_TABLE}`
        """
        query_job = client.query(query)
        results = query_job.result()
        
        # Convert to list of dicts
        traceability_matrix = []
        for row in results:
            traceability_matrix.append(dict(row.items()))
        
        return traceability_matrix
    except Exception as e:
        print(f"Error getting traceability matrix from BigQuery: {str(e)}")
        # Return empty list for resilience
        return []