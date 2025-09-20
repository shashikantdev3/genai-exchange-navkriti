import os
from firebase_admin import storage as firebase_storage

async def upload_file_to_storage(file_content: bytes, file_name: str, content_type: str) -> str:
    """
    Upload a file to Firebase Storage and return its public URL.
    
    Args:
        file_content: File content in bytes.
        file_name: Path/filename in storage.
        content_type: MIME type of the file.

    Returns:
        Public URL of the uploaded file.
    """
    try:
        # Get the storage bucket on-demand
        bucket = firebase_storage.bucket()
        blob = bucket.blob(file_name)
        blob.upload_from_string(file_content, content_type=content_type)
        
        # Make the file publicly readable
        blob.make_public()
        return blob.public_url
    except Exception as e:
        print(f"[Firebase Upload Error] {e}")
        # Construct a fallback URL in case of error
        bucket_name = os.getenv('FIREBASE_STORAGE_BUCKET')
        return f"https://storage.googleapis.com/{bucket_name}/{file_name}"

async def get_download_url(file_name: str) -> str:
    """
    Get the public URL of a file stored in Firebase Storage.

    Args:
        file_name: Path/filename in storage.

    Returns:
        Public URL of the file.
    """
    try:
        bucket = firebase_storage.bucket()
        blob = bucket.blob(file_name)
        if not blob.exists():
            raise FileNotFoundError(f"File not found in bucket: {file_name}")
        
        blob.make_public()
        return blob.public_url
    except Exception as e:
        print(f"[Firebase Download URL Error] {e}")
        bucket_name = os.getenv('FIREBASE_STORAGE_BUCKET')
        return f"https://storage.googleapis.com/{bucket_name}/{file_name}"