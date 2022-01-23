from sqlalchemy.orm.session import Session
from api.crud.prospect_file import ProspectFileCrud
from api.schemas.prospect_file import ProspectFileStatus


def track_progress(id: int, db: Session):
    """Tracks prospect file progress"""

    # pull file out of db
    prospect_file = ProspectFileCrud.get_prospect_file_by_id(db, id)

    # if file does not exist, return None
    if prospect_file is None:
        return None

    # processing is completed -> return total and done
    if prospect_file.status == ProspectFileStatus.done:
        return {
            "total": prospect_file.rows_total,
            "done": prospect_file.rows_done,
        }
    # processing is not done -> return status
    else:
        return {
            "status": prospect_file.status,
        }
