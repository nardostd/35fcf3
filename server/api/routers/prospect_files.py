import hashlib
import uuid
from datetime import datetime
from typing import Optional, Union
from fastapi import (
    APIRouter,
    HTTPException,
    status,
    Depends,
    File,
    Form,
    UploadFile,
    BackgroundTasks,
)
from sqlalchemy.orm.session import Session
from api import schemas
from api.dependencies.auth import get_current_user
from api.dependencies.db import get_db
from api.core.config import settings
from api.crud import ProspectFileCrud
from api.services import tracker, worker
from api.core.logger import log

router = APIRouter(prefix="/api", tags=["prospects_files"])


@router.post(
    "/prospect_files/import",
    response_model=schemas.ProspectFileCreatedResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def import_prospects(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    email_index: int = Form(...),
    first_name_index: Optional[int] = Form(None),
    last_name_index: Optional[int] = Form(None),
    force: Optional[bool] = Form(None),
    has_headers: Optional[bool] = Form(None),
    current_user: schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Submit uploaded file to background process and send CREATED status code"""

    # request should include bearer token (clients needs to login first)
    if not current_user:
        log.info("HTTP_401_UNAUTHORIZED")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized request. Client needs to login first.",
        )

    # accept only certain mime types: text/csv, text/plain, ...
    if file.content_type not in settings.ALLOWED_MIME_TYPES:
        log.info("HTTP_415_UNSUPPORTED_MEDIA_TYPE")
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"File must be a plain text or csv file. {file.content_type}",
        )

    # read the contents of uploaded file
    contents = await file.read()

    # Uploaded file size should not exceed max value
    if len(contents) > settings.MAX_FILE_SIZE:
        log.info("HTTP_413_REQUEST_ENTITY_TOO_LARGE")
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large (max allowed size = {settings.MAX_FILE_SIZE / (1024 * 1024)} MB).",
        )

    # generate a unique request id for tracking progress
    unique_request_id = uuid.uuid4().hex

    # persist the uploaded file and its meta data
    prospect_file = ProspectFileCrud.create_prospect_file(
        db,
        current_user.id,
        {
            # required fields
            "file_name": file.filename,
            "email_index": email_index,
            # optional fields with default values
            "first_name_index": (first_name_index, None)[
                not first_name_index or first_name_index < 1
            ],
            "last_name_index": (last_name_index, None)[
                not last_name_index or last_name_index < 1
            ],
            "has_headers": (has_headers, None)[not has_headers],
            "force": (force, None)[not force],
            # derived fields
            "file_size": len(contents),
            "sha512_digest": hashlib.sha512(contents).hexdigest(),
            "uploaded_at": datetime.now(),
            "status": schemas.ProspectFileStatus.scheduled,
            "request_id": unique_request_id,
        },
        contents,
    )

    # If None, file must have been processed earlier and cannot be
    # processed again. The most appropriate status code I found is 422.
    # https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/422
    if prospect_file is None:
        log.info("HTTP_422_UNPROCESSABLE_ENTITY")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"The same exact file has already been processed previously.",
        )

    # submit the file id for asynchronous processing
    background_tasks.add_task(worker.execute, db, current_user.id, prospect_file.id)

    return {
        "request_id": unique_request_id,
        "links": {"file_status": f"/api/prospect_files/{unique_request_id}/progress"},
    }


@router.get(
    "/prospect_files/{request_id}/progress",
    response_model=Union[
        schemas.ProspectFileStatusResponse, schemas.ProspectFileDoneResponse
    ],
    status_code=status.HTTP_200_OK,
)
def track_progress(
    request_id: str,
    current_user: schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    if not current_user:
        log.info("HTTP_401_UNAUTHORIZED")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User must be authenticated",
        )

    result = tracker.track_progress(request_id, current_user.id, db)

    if result is None:
        log.info("HTTP_404_NOT_FOUND")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Resource file not found."
        )

    return result
