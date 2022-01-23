from sqlalchemy.orm.session import Session
from api.schemas.prospect_file import ProspectFileStatus
from api.crud import ProspectFileCrud
from .csv_processor import process_csv_file
from .persistor import persist


def execute(db: Session, file_id: int) -> dict:
    """
    Process uploaded file.
    This worker method can be used both synchronously and asynchronously.
    The returned result is useful for the synchronous case.
    """

    # get file meta data from database
    prospect_file = ProspectFileCrud.get_prospect_file_by_id(db, file_id)

    # update status to in_progress
    ProspectFileCrud.update_prospect_file(
        db,
        {
            "id": file_id,
            "status": ProspectFileStatus.in_progress,
        },
    )

    # process the csv file
    result = process_csv_file(
        {
            "file_path": prospect_file.file_path,
            "email_index": prospect_file.email_index,
            "first_name_index": prospect_file.first_name_index,
            "last_name_index": prospect_file.last_name_index,
            "has_headers": prospect_file.has_headers,
        }
    )

    # discovered prospects
    prospects = result["prospects"]

    # total number of lines in the file
    lines_read = result["lines_read"]

    # persist the prospects
    persisted_prospects = persist(
        db,
        prospects,
        {
            "force": prospect_file.force,
            "user_id": prospect_file.user_id,
        },
    )

    # update status (done), rows_total, and rows_done
    ProspectFileCrud.update_prospect_file(
        db,
        {
            "id": file_id,
            "rows_total": lines_read,
            "rows_done": len(persisted_prospects),
            "status": ProspectFileStatus.done,
        },
    )

    # compose a response for synchronous option. Include HAL links (HATEOS)
    return {
        "id": file_id,
        "total": lines_read,
        "done": len(persisted_prospects),
        "status": ProspectFileStatus.done,
        "_links": {
            "self": f"/api/prospect_files/{file_id}/progress",
        },
    }
