import os
from dotenv import load_dotenv
from google.cloud import bigquery
from google.api_core.exceptions import NotFound
from typing import List, Dict, Any
import json

# Load environment variables
load_dotenv()

# Initialize BigQuery Client
# This automatically uses the credentials set up in your environment
# (e.g., from gcloud auth application-default login)
project_id = os.getenv('BIGQUERY_PROJECT_ID')
if not project_id:
    raise ValueError("BIGQUERY_PROJECT_ID environment variable not set.")
client = bigquery.Client(project=project_id)

# Define dataset and table names
DATASET_ID = "healthcare_testcases"
REQUIREMENTS_TABLE = "requirements"
TESTCASES_TABLE = "testcases"
TRACEABILITY_TABLE = "traceability_matrix"

async def ensure_tables_exist():
    """
    Checks if the BigQuery dataset and tables exist, and creates them if they don't.
    """
    dataset_id = f"{client.project}.{DATASET_ID}"
    
    # --- Create Dataset if it doesn't exist ---
    try:
        client.get_dataset(dataset_id)
        print(f"Dataset {DATASET_ID} already exists.")
    except NotFound:
        print(f"Dataset {DATASET_ID} not found, creating it.")
        dataset = bigquery.Dataset(dataset_id)
        dataset.location = "US"  # You can change the location
        client.create_dataset(dataset, timeout=30)
        print(f"Created dataset {client.project}.{DATASET_ID}")

    # --- Schema Definitions ---
    testcases_schema = [
        bigquery.SchemaField("test_case_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("title", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("requirement_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("steps", "STRING", mode="REPEATED"),
        bigquery.SchemaField("expected_result", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("priority", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("compliance_reference", "STRING", mode="REPEATED"),
        bigquery.SchemaField("status", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("created_at", "TIMESTAMP", mode="NULLABLE"),
        bigquery.SchemaField("updated_at", "TIMESTAMP", mode="NULLABLE"),
    ]
    
    traceability_schema = [
        bigquery.SchemaField("requirement_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("test_case_ids", "STRING", mode="REPEATED"),
        bigquery.SchemaField("compliance_references", "STRING", mode="REPEATED"),
        bigquery.SchemaField("last_updated", "TIMESTAMP", mode="REQUIRED"),
    ]

    # --- Create Tables if they don't exist ---
    tables = {
        TESTCASES_TABLE: testcases_schema,
        TRACEABILITY_TABLE: traceability_schema
    }
    
    for table_name, schema in tables.items():
        table_id = f"{dataset_id}.{table_name}"
        try:
            client.get_table(table_id)
            print(f"Table {table_name} already exists.")
        except NotFound:
            print(f"Table {table_name} not found, creating it.")
            table = bigquery.Table(table_id, schema=schema)
            client.create_table(table)
            print(f"Created table {table_name}.")

async def save_test_cases(test_cases: List[Dict[str, Any]]) -> bool:
    """
    Saves a list of generated test cases to the BigQuery testcases table.

    Args:
        test_cases: A list of test case dictionaries.

    Returns:
        True if the insert was successful, False otherwise.
    """
    table_id = f"{client.project}.{DATASET_ID}.{TESTCASES_TABLE}"
    
    # Ensure the required tables exist before trying to insert
    await ensure_tables_exist()
    
    errors = client.insert_rows_json(table_id, test_cases)
    if not errors:
        print(f"Successfully inserted {len(test_cases)} rows into {TESTCASES_TABLE}.")
        return True
    else:
        print("Encountered errors while inserting rows: {}".format(errors))
        return False

async def update_traceability_matrix(test_cases: List[Dict[str, Any]]) -> bool:
    """
    Updates the traceability matrix using a MERGE statement. It aggregates
    test case data by requirement_id and then inserts or updates the matrix.
    
    Args:
        test_cases: A list of newly generated test cases.

    Returns:
        True if the MERGE operation was successful, False otherwise.
    """
    table_id = f"{client.project}.{DATASET_ID}.{TRACEABILITY_TABLE}"
    
    # --- Aggregate test case data by requirement ID ---
    matrix_updates = {}
    for tc in test_cases:
        req_id = tc.get("requirement_id")
        if not req_id:
            continue
            
        if req_id not in matrix_updates:
            matrix_updates[req_id] = {
                "test_case_ids": set(),
                "compliance_references": set()
            }
        
        matrix_updates[req_id]["test_case_ids"].add(tc["test_case_id"])
        
        # Add compliance references if they exist
        if tc.get("compliance_reference"):
            matrix_updates[req_id]["compliance_references"].update(tc["compliance_reference"])

    if not matrix_updates:
        print("No requirements to update in the traceability matrix.")
        return True

    # --- Build and execute the MERGE query ---
    # We create a temporary table with the new data to merge in
    temp_table_rows = []
    for req_id, data in matrix_updates.items():
        temp_table_rows.append({
            "requirement_id": req_id,
            "test_case_ids": list(data["test_case_ids"]),
            "compliance_references": list(data["compliance_references"]),
        })

    # The MERGE statement is the most reliable way to perform an "upsert" in BigQuery
    merge_query = f"""
    MERGE `{table_id}` T
    USING UNNEST(@updates) S
    ON T.requirement_id = S.requirement_id
    WHEN MATCHED THEN
      UPDATE SET 
        T.test_case_ids = S.test_case_ids,
        T.compliance_references = S.compliance_references,
        T.last_updated = CURRENT_TIMESTAMP()
    WHEN NOT MATCHED THEN
      INSERT (requirement_id, test_case_ids, compliance_references, last_updated) 
      VALUES (S.requirement_id, S.test_case_ids, S.compliance_references, CURRENT_TIMESTAMP())
    """

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ArrayQueryParameter("updates", "STRUCT<requirement_id STRING, test_case_ids ARRAY<STRING>, compliance_references ARRAY<STRING>>", temp_table_rows),
        ]
    )

    try:
        query_job = client.query(merge_query, job_config=job_config)
        query_job.result()  # Wait for the job to complete
        print(f"Successfully merged {len(temp_table_rows)} records into {TRACEABILITY_TABLE}.")
        return True
    except Exception as e:
        print(f"Error updating traceability matrix: {e}")
        return False

async def get_traceability_matrix() -> List[Dict[str, Any]]:
    """
    Queries and retrieves the full traceability matrix from BigQuery.

    Returns:
        A list of dictionaries, where each dictionary represents a row
        in the traceability matrix. Returns an empty list on error.
    """
    table_id = f"{client.project}.{DATASET_ID}.{TRACEABILITY_TABLE}"
    query = f"SELECT * FROM `{table_id}` ORDER BY requirement_id"
    
    try:
        query_job = client.query(query)
        rows = query_job.result()
        
        records = [dict(row) for row in rows]
        return records
    except Exception as e:
        print(f"Error querying BigQuery for traceability matrix: {e}")
        return []