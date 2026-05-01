"""
File upload routes - handle image uploads for products and claims
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import os
import uuid
from datetime import datetime
from pathlib import Path

from app.core.database import get_db
from app.core.security import get_current_user
from app.core.config import settings
from app.models.user import User

router = APIRouter(prefix="/upload", tags=["File Upload"])

# Create upload directory if it doesn't exist
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB


def allowed_file(filename: str) -> bool:
    """Check if file extension is allowed"""
    return Path(filename).suffix.lower() in ALLOWED_EXTENSIONS


async def save_upload_file(upload_file: UploadFile) -> str:
    """Save uploaded file and return the URL"""
    
    # Validate file
    if not allowed_file(upload_file.filename):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File type not allowed. Only jpg, jpeg, png, gif, webp are allowed."
        )
    
    # Generate unique filename
    file_ext = Path(upload_file.filename).suffix.lower()
    unique_filename = f"{uuid.uuid4().hex}{file_ext}"
    
    # Create date-based subdirectory
    date_path = datetime.now().strftime("%Y/%m")
    full_dir = UPLOAD_DIR / date_path
    full_dir.mkdir(parents=True, exist_ok=True)
    
    file_path = full_dir / unique_filename
    
    # Save file
    content = await upload_file.read()
    
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File too large. Maximum size is 5MB."
        )
    
    with open(file_path, "wb") as f:
        f.write(content)
    
    # Return URL path
    return f"/uploads/{date_path}/{unique_filename}"


@router.post("/image", status_code=status.HTTP_201_CREATED)
async def upload_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """Upload a single image file"""
    
    try:
        image_url = await save_upload_file(file)
        return {
            "url": image_url,
            "filename": file.filename,
            "message": "Image uploaded successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload image: {str(e)}"
        )


@router.post("/images", status_code=status.HTTP_201_CREATED)
async def upload_multiple_images(
    files: list[UploadFile] = File(...),
    current_user: User = Depends(get_current_user)
):
    """Upload multiple image files"""
    
    if len(files) > 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 10 images allowed at once"
        )
    
    uploaded_urls = []
    errors = []
    
    for idx, file in enumerate(files):
        try:
            image_url = await save_upload_file(file)
            uploaded_urls.append({
                "index": idx,
                "url": image_url,
                "filename": file.filename
            })
        except HTTPException as e:
            errors.append({
                "index": idx,
                "filename": file.filename,
                "error": e.detail
            })
        except Exception as e:
            errors.append({
                "index": idx,
                "filename": file.filename,
                "error": str(e)
            })
    
    return {
        "uploaded": uploaded_urls,
        "errors": errors,
        "total_uploaded": len(uploaded_urls),
        "total_errors": len(errors)
    }


@router.delete("/image")
async def delete_image(
    image_url: str = Form(...),
    current_user: User = Depends(get_current_user)
):
    """Delete an uploaded image"""
    
    # Security: Only allow deleting from uploads directory
    if not image_url.startswith("/uploads/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid image URL"
        )
    
    # Construct full path
    file_path = Path("." + image_url)
    
    if file_path.exists():
        try:
            file_path.unlink()
            return {"message": "Image deleted successfully"}
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete image: {str(e)}"
            )
    
    return {"message": "Image not found"}