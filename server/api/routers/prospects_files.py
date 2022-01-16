from typing import Optional
from fastapi import APIRouter, HTTPException, status, Depends, File, Form, UploadFile
from sqlalchemy.orm.session import Session
from api import schemas
from api.dependencies.auth import get_current_user, get_token
from api.dependencies.db import get_db
from api.core.config import settings

router = APIRouter(prefix="/api", tags=["prospects_files"])

@router.post("/prospects_files/import", status_code=status.HTTP_202_ACCEPTED)
async def import_prospects(
    file: UploadFile = File(...),
    email_index: int = Form(...),
    first_name_index: Optional[int] = Form(None),
    last_name_index: Optional[int] = Form(None),
    force: Optional[bool] = Form(None),
    has_header: Optional[bool] = Form(None),
    current_user: schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit uploaded file to background process and send CREATED status code"""

    # request should include bearer token (clients needs to login first)
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized request. Client needs to login first."
        )

    # accept only text/plain
    if file.content_type != "text/plain":
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="File must be a plain text file."
        )

    # read the contents of uploaded file
    contents = await file.read()

    # Uploaded file size should not exceed max value
    if len(contents) > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large (max allowed size = {settings.MAX_FILE_SIZE / (1024 * 1024)} MB)."
        )

    # TODO schdule background task here...

    return {
        "file_name": file.filename,
        "file_size": len(contents),
        "email_index": email_index,
        "first_name_index": (first_name_index, -1)[not first_name_index],
        "last_name_index": (last_name_index, -1)[not last_name_index],
        "force": (force, False)[not force],
        "has_header": (has_header, False)[not has_header]
    }