import os
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, storage as firebase_storage

# Load environment variables
load_dotenv()

# Initialize Firebase Admin SDK using service account
if not firebase_admin._apps:
    cred_path = "keys/serviceAccountKey.json"  # Path relative to backend/
    if not os.path.isfile(cred_path):
        raise FileNotFoundError(f"Firebase service account key not found at {cred_path}")

    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred, {
        "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET")
    })

# Get Firebase Storage bucket
bucket = firebase_storage.bucket()

async def upload_file_to_storage(file_content: bytes, file_name: str, content_type: str) -> str:
    """
    Upload a file to Firebase Storage and return its public URL.
    
    Args:
        file_content: File content in bytes
        file_name: Path/filename in storage
        content_type: MIME type of the file

    Returns:
        Public URL of the uploaded file
    """
    try:
        blob = bucket.blob(file_name)
        blob.upload_from_string(file_content, content_type=content_type)
        blob.make_public()
        return blob.public_url
    except Exception as e:
        print(f"[Firebase Upload Error] {e}")
        return f"https://storage.googleapis.com/{os.getenv('FIREBASE_STORAGE_BUCKET')}/{file_name}"

async def get_download_url(file_name: str) -> str:
    """
    Get the public URL of a file stored in Firebase Storage.

    Args:
        file_name: Path/filename in storage

    Returns:
        Public URL of the file
    """
    try:
        blob = bucket.blob(file_name)
        if not blob.exists():
            raise FileNotFoundError(f"File not found in bucket: {file_name}")
        blob.make_public()
        return blob.public_url
    except Exception as e:
        print(f"[Firebase Download URL Error] {e}")
        return f"https://storage.googleapis.com/{os.getenv('FIREBASE_STORAGE_BUCKET')}/{file_name}"

async def delete_file(file_name: str) -> bool:
    """
    Delete a file from Firebase Storage.

    Args:
        file_name: Path/filename in storage

    Returns:
        True if deletion was successful, False otherwise
    """
    try:
        blob = bucket.blob(file_name)
        blob.delete()
        return True
    except Exception as e:
        print(f"[Firebase Delete Error] {e}")
        return False
