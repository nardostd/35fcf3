from typing import Set
from sqlalchemy.orm.session import Session
from api.schemas.prospect_file import ProspectFileStatus
from api.crud import ProspectFileCrud, ProspectCrud
from api.schemas.prospects import Prospect
from .csv_processor import process_csv_file


def submit(db: Session, file_id: int) -> dict:
    """Process uploaded file synchronously"""

    # get file meta data from database
    prospect_file = ProspectFileCrud.get_prospect_file_by_id(db, file_id)

    # get user id
    user_id = prospect_file.user_id

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
        }
    )

    # discovered prospects
    prospects = result["prospects"]

    # total number of lines in the file
    lines_read = result["lines_read"]

    # collection to hold persisted prospects
    persisted_prospects: Set[Prospect] = set()

    # iterate over the discovered prospects and persist
    for prospect in prospects:
        persisted_prospects.add(
            ProspectCrud.create_prospect(
                db,
                user_id,
                {
                    "email": prospect.email,
                    "first_name": prospect.first_name,
                    "last_name": prospect.last_name,
                },
            )
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

    # compose a result and return
    return {
        "id": file_id,
        "rows_total": lines_read,
        "rows_done": len(persisted_prospects),
        "status": ProspectFileStatus.done,
    }
