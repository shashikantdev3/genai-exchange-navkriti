import os
import csv
import tempfile
import pandas as pd
from fpdf import FPDF
from typing import List, Dict, Any

async def export_data(format: str, traceability_matrix: List[Dict[str, Any]], test_cases: List[Dict[str, Any]]) -> str:
    """
    Export traceability matrix and test cases to the specified format
    
    Args:
        format: The format to export to (csv, xlsx, pdf)
        traceability_matrix: The traceability matrix data
        test_cases: The test cases data
        
    Returns:
        Path to the exported file
    """
    # Create a temporary file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=f".{format}")
    temp_file_path = temp_file.name
    temp_file.close()
    
    if format == "csv":
        return await export_to_csv(temp_file_path, traceability_matrix, test_cases)
    elif format == "xlsx":
        return await export_to_xlsx(temp_file_path, traceability_matrix, test_cases)
    elif format == "pdf":
        return await export_to_pdf(temp_file_path, traceability_matrix, test_cases)
    else:
        raise ValueError(f"Unsupported export format: {format}")

async def export_to_csv(file_path: str, traceability_matrix: List[Dict[str, Any]], test_cases: List[Dict[str, Any]]) -> str:
    """
    Export data to CSV format
    """
    # Create a CSV file with two sections: Traceability Matrix and Test Cases
    with open(file_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        
        # Write Traceability Matrix section
        writer.writerow(["TRACEABILITY MATRIX"])
        writer.writerow(["Requirement ID", "Description", "Test Cases", "Compliance", "Status"])
        
        for item in traceability_matrix:
            writer.writerow([
                item.get("requirement_id", ""),
                item.get("description", ""),
                ", ".join(item.get("test_cases", [])),
                ", ".join(item.get("compliance", [])),
                item.get("status", "")
            ])
        
        # Add a blank row between sections
        writer.writerow([])
        
        # Write Test Cases section
        writer.writerow(["TEST CASES"])
        writer.writerow(["Test Case ID", "Title", "Requirement ID", "Steps", "Expected Result", "Priority", "Compliance", "Status"])
        
        for test_case in test_cases:
            writer.writerow([
                test_case.get("test_case_id", ""),
                test_case.get("title", ""),
                test_case.get("requirement_id", ""),
                " | ".join(test_case.get("steps", [])),
                test_case.get("expected_result", ""),
                test_case.get("priority", ""),
                ", ".join(test_case.get("compliance_reference", [])),
                test_case.get("status", "")
            ])
    
    return file_path

async def export_to_xlsx(file_path: str, traceability_matrix: List[Dict[str, Any]], test_cases: List[Dict[str, Any]]) -> str:
    """
    Export data to XLSX format
    """
    # Create a Pandas Excel writer
    with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
        # Convert traceability matrix to DataFrame
        traceability_df = pd.DataFrame(traceability_matrix)
        
        # Handle list columns
        if 'test_cases' in traceability_df.columns:
            traceability_df['test_cases'] = traceability_df['test_cases'].apply(lambda x: ', '.join(x) if isinstance(x, list) else x)
        
        if 'compliance' in traceability_df.columns:
            traceability_df['compliance'] = traceability_df['compliance'].apply(lambda x: ', '.join(x) if isinstance(x, list) else x)
        
        # Write traceability matrix to Excel
        traceability_df.to_excel(writer, sheet_name='Traceability Matrix', index=False)
        
        # Convert test cases to DataFrame
        test_cases_df = pd.DataFrame(test_cases)
        
        # Handle list columns
        if 'steps' in test_cases_df.columns:
            test_cases_df['steps'] = test_cases_df['steps'].apply(lambda x: ' | '.join(x) if isinstance(x, list) else x)
        
        if 'compliance_reference' in test_cases_df.columns:
            test_cases_df['compliance_reference'] = test_cases_df['compliance_reference'].apply(lambda x: ', '.join(x) if isinstance(x, list) else x)
        
        # Write test cases to Excel
        test_cases_df.to_excel(writer, sheet_name='Test Cases', index=False)
    
    return file_path

async def export_to_pdf(file_path: str, traceability_matrix: List[Dict[str, Any]], test_cases: List[Dict[str, Any]]) -> str:
    """
    Export data to PDF format
    """
    # Create PDF
    pdf = FPDF()
    pdf.add_page()
    
    # Set font
    pdf.set_font("Arial", size=12)
    
    # Add title
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, "Healthcare AI Test Case Generator Report", ln=True, align='C')
    pdf.ln(10)
    
    # Add Traceability Matrix section
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, "Traceability Matrix", ln=True)
    pdf.ln(5)
    
    # Add table headers
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(30, 10, "Req ID", border=1)
    pdf.cell(50, 10, "Description", border=1)
    pdf.cell(40, 10, "Test Cases", border=1)
    pdf.cell(40, 10, "Compliance", border=1)
    pdf.cell(30, 10, "Status", border=1, ln=True)
    
    # Add table rows
    pdf.set_font("Arial", size=8)
    for item in traceability_matrix:
        pdf.cell(30, 10, item.get("requirement_id", ""), border=1)
        
        # Handle long descriptions
        description = item.get("description", "")
        if len(description) > 40:
            description = description[:37] + "..."
        pdf.cell(50, 10, description, border=1)
        
        # Join test cases
        test_cases_str = ", ".join(item.get("test_cases", []))
        if len(test_cases_str) > 35:
            test_cases_str = test_cases_str[:32] + "..."
        pdf.cell(40, 10, test_cases_str, border=1)
        
        # Join compliance
        compliance_str = ", ".join(item.get("compliance", []))
        if len(compliance_str) > 35:
            compliance_str = compliance_str[:32] + "..."
        pdf.cell(40, 10, compliance_str, border=1)
        
        pdf.cell(30, 10, item.get("status", ""), border=1, ln=True)
    
    pdf.ln(10)
    
    # Add Test Cases section
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, "Test Cases", ln=True)
    pdf.ln(5)
    
    # Add each test case
    for i, test_case in enumerate(test_cases):
        if i > 0:
            pdf.ln(5)
        
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(200, 10, f"Test Case: {test_case.get('test_case_id', '')}", ln=True)
        
        pdf.set_font("Arial", size=10)
        pdf.cell(40, 8, "Title:", border=0)
        pdf.cell(150, 8, test_case.get("title", ""), border=0, ln=True)
        
        pdf.cell(40, 8, "Requirement ID:", border=0)
        pdf.cell(150, 8, test_case.get("requirement_id", ""), border=0, ln=True)
        
        pdf.cell(40, 8, "Priority:", border=0)
        pdf.cell(150, 8, test_case.get("priority", ""), border=0, ln=True)
        
        pdf.cell(40, 8, "Status:", border=0)
        pdf.cell(150, 8, test_case.get("status", ""), border=0, ln=True)
        
        # Steps
        pdf.cell(40, 8, "Steps:", border=0, ln=True)
        steps = test_case.get("steps", [])
        for j, step in enumerate(steps):
            pdf.cell(10, 8, "", border=0)
            pdf.cell(180, 8, f"{j+1}. {step}", border=0, ln=True)
        
        pdf.cell(40, 8, "Expected Result:", border=0, ln=True)
        pdf.cell(10, 8, "", border=0)
        pdf.multi_cell(180, 8, test_case.get("expected_result", ""))
        
        # Compliance
        compliance_str = ", ".join(test_case.get("compliance_reference", []))
        pdf.cell(40, 8, "Compliance:", border=0)
        pdf.cell(150, 8, compliance_str, border=0, ln=True)
    
    # Save PDF
    pdf.output(file_path)
    
    return file_path