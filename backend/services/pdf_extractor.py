import fitz
from google.cloud import storage
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

async def extract_text_from_gcs_pdf(bucket_name: str, file_name: str) -> str:
    """
    Downloads a PDF from GCS and extracts its text content.

    Args:
        bucket_name: The name of the GCS bucket.
        file_name: The full path to the file in the bucket (e.g., 'requirements/srs.pdf').

    Returns:
        The extracted text as a single string.
    """
    try:
        # Get the project ID from the environment variable
        project_id = os.getenv("GOOGLE_CLOUD_PROJECT")

        # Initialize the storage client with the project ID
        storage_client = storage.Client(project=project_id)
        
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(file_name)

        # Download the PDF content into memory
        pdf_content = blob.download_as_bytes()

        # Use PyMuPDF to open the PDF from the in-memory content
        doc = fitz.open(stream=pdf_content, filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        
        return text
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return ""