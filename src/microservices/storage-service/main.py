"""
Storage Service API
FastAPI microservice for generic file storage
"""

import os
from typing import Optional

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from storage_service import StorageService

app = FastAPI(
    title="Storage Service",
    description="Generic file storage microservice with hash-based deduplication",
    version="1.0.0",
)

# Initialize storage service
storage = StorageService(
    endpoint=os.getenv("MINIO_ENDPOINT", "minio:9000"),
    access_key=os.getenv("MINIO_ROOT_USER"),
    secret_key=os.getenv("MINIO_ROOT_PASSWORD"),
    secure=os.getenv("MINIO_SECURE", "false").lower() == "true",
    default_bucket=os.getenv("DEFAULT_BUCKET", "files"),
)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "storage-service"}


@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    bucket: Optional[str] = Form(None),
    metadata: Optional[str] = Form(None),
):
    """
    Upload a file to storage

    Returns:
        - hash: SHA256 hash of the file
        - filename: Generated unique filename
        - original_filename: Original filename
        - url: Public URL to access the file
        - size: File size in bytes
        - content_type: MIME type
        - bucket: Bucket where file is stored
        - already_exists: Whether file was already in storage
    """
    try:
        # Read file content
        content = await file.read()

        # Parse metadata if provided
        meta_dict = {}
        if metadata:
            try:
                import json

                meta_dict = json.loads(metadata)
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Invalid metadata JSON")

        # Upload file
        result = storage.upload_file(
            file_content=content,
            original_filename=file.filename,
            content_type=file.content_type or "application/octet-stream",
            bucket=bucket,
            metadata=meta_dict,
        )

        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("error"))

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/download/{filename}")
async def download_file(filename: str, bucket: Optional[str] = None):
    """Download a file by filename"""
    content = storage.download_file(filename, bucket)

    if content is None:
        raise HTTPException(status_code=404, detail="File not found")

    # Get file info for content type
    info = storage.get_file_info(filename, bucket)
    content_type = (
        info.get("content_type", "application/octet-stream")
        if info
        else "application/octet-stream"
    )

    return StreamingResponse(
        iter([content]),
        media_type=content_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@app.get("/info/{filename}")
async def get_file_info(filename: str, bucket: Optional[str] = None):
    """Get file metadata"""
    info = storage.get_file_info(filename, bucket)

    if info is None:
        raise HTTPException(status_code=404, detail="File not found")

    return info


@app.delete("/delete/{filename}")
async def delete_file(filename: str, bucket: Optional[str] = None):
    """Delete a file"""
    success = storage.delete_file(filename, bucket)

    if not success:
        raise HTTPException(status_code=404, detail="File not found or deletion failed")

    return {"success": True, "message": "File deleted successfully"}


@app.get("/exists/{file_hash}")
async def check_file_exists(
    file_hash: str,
    extension: str = "",
    bucket: Optional[str] = None,
):
    """Check if a file with given hash exists"""
    exists = storage.file_exists(file_hash, extension, bucket)
    return {"exists": exists, "hash": file_hash}


@app.get("/presigned/{filename}")
async def get_presigned_url(
    filename: str,
    bucket: Optional[str] = None,
    expiry_hours: int = 1,
):
    """Get a presigned URL for temporary access"""
    from datetime import timedelta

    url = storage.get_presigned_url(
        filename,
        bucket,
        expiry=timedelta(hours=expiry_hours),
    )

    if url is None:
        raise HTTPException(status_code=404, detail="File not found")

    return {"url": url, "expires_in_hours": expiry_hours}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
