import logging
from fastapi import logger
from typing import Set
from sqlalchemy.orm.session import Session
from api.schemas.prospect_file import ProspectFile
from api.schemas.prospects import Prospect
from . import synchronous, asynchronous

logging.basicConfig(level=logging.INFO)
log = logger.logger


def process_file(db: Session, file_id: int):
    """Process prospect file identified by file_id"""

    result = synchronous.submit(db, file_id)

    return result


# Invalid if the number of columns discovered in the row
# is less than any of the indices provided in the request.
def is_valid_row(row: list, prospect_file: ProspectFile) -> bool:
    """Validate a row in a CSV file. Mainly check if indices are not out of bound."""
    try:
        if (
            prospect_file.email_index < 1
            or prospect_file.email_index > len(row)
            or (
                prospect_file.first_name_index is not None
                and prospect_file.first_name_index > len(row)
            )
            or (
                prospect_file.last_name_index is not None
                and prospect_file.last_name_index > len(row)
            )
        ):
            raise ValueError("index out of bound.")
        return True

    except (ValueError):
        return False
