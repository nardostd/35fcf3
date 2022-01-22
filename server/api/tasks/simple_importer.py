import csv
import logging
from fastapi import logger
from typing import Set
from pydantic import ValidationError
from api.core.config import settings
from api.schemas.prospect_file import ProspectFile
from api.crud import ProspectFileCrud
from api.schemas.prospects import Prospect, ProspectCreate

logging.basicConfig(level=logging.INFO)
log = logger.logger


def process_file(db, file_id: int) -> Set[ProspectCreate]:
    """Process prospect file identified by file_id"""

    # get file meta data from database
    prospect_file = ProspectFileCrud.get_prospect_file_by_id(db, file_id)

    # a set to hold the discovered prospects
    prospects: set = set()

    # count the number of lines in the csv file
    total_number_of_lines: int = 0

    # read csv file from disk
    with open(prospect_file.file_path, newline="") as csvfile:
        rows = csv.reader(csvfile, delimiter=",", quotechar='"')
        for row in rows:

            # limit the number of rows to configured value of API
            if total_number_of_lines > settings.MAX_NUMBER_OF_ROWS:
                break

            # one more row is read
            total_number_of_lines += 1

            # validate row
            if is_valid_row(row, prospect_file):
                try:
                    # get email
                    email = row[prospect_file.email_index - 1]

                    # get first name or default to empty string
                    if not prospect_file.first_name_index:
                        first_name = ""
                    else:
                        first_name = row[prospect_file.first_name_index - 1]

                    # get last name or default to empty string
                    if not prospect_file.last_name_index:
                        last_name = ""
                    else:
                        last_name = row[prospect_file.last_name_index - 1]

                    # create the prospect object
                    prospects.add(
                        ProspectCreate(
                            email=email,
                            first_name=first_name,
                            last_name=last_name,
                        )
                    )
                except ValidationError as e:
                    log.error(e)

    # TODO persist the discovered prospects

    # update the prospect file fields
    prospect_file.rows_total = total_number_of_lines
    prospect_file.rows_done = len(prospects)

    # persist the updates
    ProspectFileCrud.update_prospect_file(
        db,
        {
            "id": prospect_file.id,
            "rows_total": prospect_file.rows_total,
            "rows_done": prospect_file.rows_done,
        },
    )

    return prospects


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
