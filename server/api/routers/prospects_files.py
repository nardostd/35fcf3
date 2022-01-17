from datetime import datetime
import imp
from typing import Optional
from fastapi import APIRouter, HTTPException, status, Depends, File, Form, UploadFile
from sqlalchemy.orm.session import Session
from api import schemas
from api.dependencies.auth import get_current_user, get_token
from api.dependencies.db import get_db
from api.core.config import settings
from api.crud import ProspectsFileCrud
from api.models import ProspectsFile
from api.tasks import simple_importer
import hashlib

from api.schemas.prospects_file import ProspectsFileCreate

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

    # meta data of uploaded file
    prospects_file_meta_data = {
        # required fields
        "file_name": file.filename,
        "email_index": email_index,

        # optional fields with default values
        "first_name_index": (first_name_index, -1)[not first_name_index],
        "last_name_index": (last_name_index, -1)[not last_name_index],
        "has_header": (has_header, False)[not has_header],

        # derived fields
        "file_size": len(contents),
        "sha512_digest": hashlib.sha512(contents).hexdigest(),
        "uploaded_at": datetime.now(),
    }
    
    # persist the uploaded file meta data
    prospects_file = ProspectsFileCrud.create_prospects_file(
        db,
        current_user.id,
        prospects_file_meta_data
    )

    # schedule importing task
    simple_importer.process_file(prospects_file.id, force)