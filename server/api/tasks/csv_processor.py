import csv
import logging
from fastapi import logger
from typing import Set
from pydantic import ValidationError
from sqlalchemy.orm.session import Session
from api.core.config import settings
from api.schemas.prospect_file import ProspectFile, ProspectFileCreate
from api.crud import ProspectFileCrud
from api.schemas.prospects import ProspectCreate

logging.basicConfig(level=logging.INFO)
log = logger.logger


def process_csv_file(file_params: dict) -> dict:
    """Process prospect file identified by file_id"""

    # a set to hold the discovered prospects
    prospects: set = set()

    # count the number of lines in the csv file
    total_number_of_lines: int = 0

    # read csv file from disk
    with open(file_params["file_path"], newline="") as csvfile:

        rows = csv.reader(csvfile, delimiter=",", quotechar='"')

        for row in rows:

            # limit the number of rows to configured value of API
            if total_number_of_lines > settings.MAX_NUMBER_OF_ROWS:
                break

            # one more row is read
            total_number_of_lines += 1

            # skip invalid/malformed rows
            if is_valid_row(row, file_params) == False:
                continue

            try:
                # get email
                email = row[file_params["email_index"] - 1]

                # get first name or default to empty string
                if not file_params["first_name_index"]:
                    first_name = ""
                else:
                    first_name = row[file_params["first_name_index"] - 1]

                # get last name or default to empty string
                if not file_params["last_name_index"]:
                    last_name = ""
                else:
                    last_name = row[file_params["last_name_index"] - 1]

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

    return {
        "prospects": prospects,
        "lines_read": total_number_of_lines,
    }


# Invalid if the number of columns discovered in the row
# is less than any of the indices provided in the request.
def is_valid_row(row: list, file_params: dict) -> bool:
    """Validate a row in a CSV file. Mainly check if indices are not out of bound."""
    try:
        if (
            file_params["email_index"] < 1
            or file_params["email_index"] > len(row)
            or (
                file_params["first_name_index"] is not None
                and file_params["first_name_index"] > len(row)
            )
            or (
                file_params["last_name_index"] is not None
                and file_params["last_name_index"] > len(row)
            )
        ):
            raise ValueError("index out of bound.")
        return True

    except (ValueError):
        return False
